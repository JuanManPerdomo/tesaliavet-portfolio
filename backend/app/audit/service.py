from datetime import date, datetime
from decimal import Decimal

from ..extensions import db
from ..models import User, AuditLog, Category, Species, Supplier

EXCLUDED_SUFFIXES = ('_path', '_mime', '_hash')
EXCLUDED_FIELDS = {'id', 'created_at', 'updated_at', 'reset_code_attempts', 'reset_code_expires_at'}
MAX_VALUE_LENGTH = 120  # trunca textos largos (ej. una respuesta de PQRS)

FIELD_LABELS = {
    'first_name': 'Nombre', 'last_name': 'Apellido', 'email': 'Correo',
    'phone': 'Teléfono', 'direccion': 'Dirección', 'ciudad': 'Municipio',
    'departamento': 'Departamento', 'is_active': 'Activo',
    'name': 'Nombre', 'description': 'Descripción', 'sku': 'SKU',
    'purchase_price': 'Precio de compra', 'selling_price': 'Precio de venta',
    'tax_rate': 'IVA', 'stock': 'Stock', 'min_stock': 'Stock mínimo',
    'unit_label': 'Unidad', 'unit_weight_kg': 'Peso por unidad',
    'is_pharmacy': 'Farmacia Veterinaria', 'category_id': 'Categoría',
    'parent_id': 'Categoría padre', 'species_id': 'Especie',
    'veterinarian_id': 'Veterinario', 'status': 'Estado',
    'shipping_cost': 'Transporte', 'tax_amount': 'Impuestos',
    'cancel_reason': 'Motivo de anulación', 'response': 'Respuesta',
    'counted_cash': 'Efectivo contado', 'expected_cash': 'Efectivo esperado',
    'cash_difference': 'Diferencia', 'difference_justification': 'Justificación',
    'notes': 'Notas', 'gender': 'Género', 'breed_id': 'Raza',
    'responded_by': 'Respondido por', 'responded_at': 'Fecha de respuesta',
    'closed_at': 'Fecha de cierre', 'delivered_at': 'Fecha de entrega',
    'received_at': 'Fecha de recepción', 'expected_delivery_date': 'Fecha de entrega esperada',
    'supplier_id': 'Proveedor',
}

# category_id/parent_id -> Category.name, species_id -> Species.name,
# veterinarian_id -> "Nombre Apellido" de User - lista corta de FKs donde
# mostrar el id crudo no dice nada.
FK_RESOLVERS = {
    'category_id': (Category, lambda o: o.name),
    'parent_id': (Category, lambda o: o.name),
    'species_id': (Species, lambda o: o.name),
    'veterinarian_id': (User, lambda o: f'{o.first_name} {o.last_name}'),
    'responded_by': (User, lambda o: f'{o.first_name} {o.last_name}'),
    'supplier_id': (Supplier, lambda o: o.name),
}


def _serialize(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, str) and len(value) > MAX_VALUE_LENGTH:
        return value[:MAX_VALUE_LENGTH - 1].rstrip() + '…'
    return value


def _resolve_fk(field, value):
    if value is None or field not in FK_RESOLVERS:
        return _serialize(value)
    model, name_fn = FK_RESOLVERS[field]
    obj = model.query.get(value)
    return name_fn(obj) if obj else _serialize(value)


def _relevant_fields(instance):
    insp = db.inspect(instance)
    return [
        attr.key for attr in insp.mapper.column_attrs
        if attr.key not in EXCLUDED_FIELDS and not attr.key.endswith(EXCLUDED_SUFFIXES)
    ]


def snapshot_fields(instance):
    """Copia los valores actuales de los campos relevantes de `instance`
    ANTES de aplicar cualquier cambio - se compara despues con
    diff_snapshot(). Se usa esto (y no el historial interno de SQLAlchemy,
    `inspect(obj).attrs[campo].history`) porque una query intermedia
    cualquiera entre aplicar los cambios y armar el diff (ej.
    _sync_stock_alert haciendo StockAlert.query...) dispara un autoflush
    que reescribe el "estado confirmado" de cada atributo y borra ese
    historial - se confirmo este bug real probando con un producto (el
    diff salia vacio pese a que el precio y el stock si cambiaron). Con un
    snapshot propio, comparado a mano contra el estado final, el resultado
    no depende de cuantas queries intermedias haya."""
    return {field: getattr(instance, field) for field in _relevant_fields(instance)}


def diff_snapshot(instance, before):
    """Compara `before` (de snapshot_fields, tomado ANTES de mutar la fila)
    contra el estado actual de `instance` - se llama despues de aplicar los
    cambios, en cualquier punto (ya no importa si hubo queries intermedias
    de por medio). Devuelve una lista de {field, label, old, new}, vacía si
    no cambió nada real."""
    changes = []
    for field, old in before.items():
        new = getattr(instance, field)
        if old == new:
            continue
        changes.append({
            'field': field,
            'label': FIELD_LABELS.get(field, field),
            'old': _resolve_fk(field, old),
            'new': _resolve_fk(field, new),
        })
    return changes


def log_audit(user_id, module, action, description, entity_type=None, entity_id=None, changes=None):
    """Deja un registro de auditoria. No hace commit propio - se cuelga del
    commit() que ya hace el endpoint que lo llama, mismo patron que
    _sync_stock_alert en products/routes.py.

    user_name/user_email se guardan como snapshot de texto (a diferencia de
    registered_by/resolved_by en otras tablas) porque el proposito de un log
    de auditoria es sobrevivir a que se borre la cuenta.

    `changes` (opcional): lista de {field, label, old, new} de
    diff_snapshot() - solo tiene sentido para ediciones de una fila
    existente, None para create/delete/login/etc."""
    user = User.query.get(user_id) if user_id else None
    db.session.add(AuditLog(
        user_id=user_id,
        user_name=f'{user.first_name} {user.last_name}' if user else None,
        user_email=user.email if user else None,
        module=module,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        changes=changes or None,
    ))
