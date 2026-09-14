from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import or_

from ..extensions import db
from ..models import Supplier, SupplierProduct, Product, PurchaseOrder
from ..auth.decorators import role_required
from ..audit.service import diff_snapshot, log_audit, snapshot_fields

suppliers_bp = Blueprint('suppliers', __name__)

VALID_STATUS_FILTERS = {'active', 'inactive', 'all'}


def _supplier_payload(supplier, include_products=False):
    payload = {
        'id': supplier.id,
        'name': supplier.name,
        'documentType': supplier.document_type,
        'documentNumber': supplier.document_number,
        'contactName': supplier.primary_contact_name,
        'contactPhone': supplier.primary_contact_phone,
        'contactEmail': supplier.primary_contact_email,
        'address': supplier.address,
        'city': supplier.city,
        'notes': supplier.notes,
        'isActive': supplier.is_active,
    }

    if include_products:
        rows = (
            SupplierProduct.query.filter_by(supplier_id=supplier.id, is_active=True)
            .join(Product, SupplierProduct.product_id == Product.id)
            .order_by(Product.name.asc())
            .all()
        )
        payload['products'] = [{
            'productId': row.product_id,
            'productName': row.product.name,
            'sku': row.product.sku,
            'unitLabel': row.product.unit_label,
            'unitWeightKg': float(row.product.unit_weight_kg) if row.product.unit_weight_kg is not None else None,
            'supplierSku': row.supplier_sku,
            'purchasePrice': float(row.purchase_price) if row.purchase_price is not None else None,
            'leadTimeDays': row.lead_time_days,
            'isPreferred': row.is_preferred,
        } for row in rows]
        payload['productsCount'] = len(payload['products'])

        last_order = (
            PurchaseOrder.query.filter_by(supplier_id=supplier.id)
            .order_by(PurchaseOrder.order_date.desc())
            .first()
        )
        payload['purchaseOrdersCount'] = PurchaseOrder.query.filter_by(supplier_id=supplier.id).count()
        payload['lastPurchaseOrderDate'] = (
            last_order.order_date.isoformat() if last_order and last_order.order_date else None
        )

    return payload


def _apply_supplier_fields(supplier, data):
    if 'name' in data:
        if not data['name']:
            return 'El nombre del proveedor es requerido'
        supplier.name = data['name']

    if 'documentType' in data:
        supplier.document_type = data['documentType'] or None

    if 'documentNumber' in data:
        supplier.document_number = data['documentNumber'] or None

    if 'contactName' in data:
        supplier.primary_contact_name = data['contactName'] or None

    if 'contactPhone' in data:
        supplier.primary_contact_phone = data['contactPhone'] or None

    if 'contactEmail' in data:
        supplier.primary_contact_email = data['contactEmail'] or None

    if 'address' in data:
        supplier.address = data['address'] or None

    if 'city' in data:
        supplier.city = data['city'] or None

    if 'notes' in data:
        supplier.notes = data['notes'] or None

    if 'isActive' in data:
        value = data['isActive']
        supplier.is_active = value if isinstance(value, bool) else str(value).lower() in ('true', '1', 'on')

    return None


@suppliers_bp.route('', methods=['GET'])
@role_required('admin', 'bodeguero')
def list_suppliers():
    query = Supplier.query

    status = request.args.get('status')
    if status not in VALID_STATUS_FILTERS:
        status = 'active'
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)
    # 'all' -> sin filtro de is_active

    search = request.args.get('search')
    if search:
        query = query.filter(or_(
            Supplier.name.ilike(f'%{search}%'),
            Supplier.document_number.ilike(f'%{search}%'),
        ))

    query = query.order_by(Supplier.name.asc())

    page = request.args.get('page', default=1, type=int)
    per_page = min(request.args.get('per_page', default=20, type=int), 100)

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'suppliers': [_supplier_payload(s) for s in paginated.items],
        'total': paginated.total,
        'page': paginated.page,
        'per_page': paginated.per_page,
        'pages': paginated.pages,
    })


@suppliers_bp.route('/<int:supplier_id>', methods=['GET'])
@role_required('admin', 'bodeguero')
def get_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    return jsonify(_supplier_payload(supplier, include_products=True))


@suppliers_bp.route('', methods=['POST'])
@role_required('admin', 'bodeguero')
def create_supplier():
    data = request.get_json(silent=True) or {}

    if not data.get('name'):
        return jsonify({'message': 'El nombre del proveedor es requerido'}), 400

    supplier = Supplier()
    error = _apply_supplier_fields(supplier, data)
    if error:
        return jsonify({'message': error}), 400

    db.session.add(supplier)
    db.session.flush()
    log_audit(
        int(get_jwt_identity()), 'Proveedores', 'create',
        f'Creó el proveedor "{supplier.name}"', entity_type='supplier', entity_id=supplier.id,
    )
    db.session.commit()
    return jsonify(_supplier_payload(supplier)), 201


@suppliers_bp.route('/<int:supplier_id>', methods=['PUT'])
@role_required('admin', 'bodeguero')
def update_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    before = snapshot_fields(supplier)
    data = request.get_json(silent=True) or {}

    error = _apply_supplier_fields(supplier, data)
    if error:
        return jsonify({'message': error}), 400

    if list(data.keys()) == ['isActive']:
        action = 'activate' if supplier.is_active else 'deactivate'
        description = f'{"Activó" if supplier.is_active else "Desactivó"} el proveedor "{supplier.name}"'
    else:
        action = 'update'
        description = f'Editó el proveedor "{supplier.name}"'
    log_audit(
        int(get_jwt_identity()), 'Proveedores', action, description,
        entity_type='supplier', entity_id=supplier.id, changes=diff_snapshot(supplier, before),
    )

    db.session.commit()
    return jsonify(_supplier_payload(supplier))


@suppliers_bp.route('/<int:supplier_id>/products', methods=['POST'])
@role_required('admin', 'bodeguero')
def associate_product(supplier_id):
    # Upsert sobre supplier_products (misma tabla que gestiona el campo
    # "Proveedor" de ProductFormPage, ver decision 19), pero desde el lado
    # del proveedor: elegir un producto existente y fijar sus datos de
    # abastecimiento con este proveedor.
    supplier = Supplier.query.get_or_404(supplier_id)
    data = request.get_json(silent=True) or {}

    product_id = data.get('productId')
    if not product_id:
        return jsonify({'message': 'El producto es requerido'}), 400
    product = Product.query.get(int(product_id))
    if not product:
        return jsonify({'message': 'Producto no encontrado'}), 404

    # purchase_price es NOT NULL en la tabla real (a diferencia del modelo
    # SQLAlchemy, que no lo marca) - siempre requerido, no solo cuando viene
    # en el payload, para no romper el INSERT de una fila nueva.
    if data.get('purchasePrice') in (None, ''):
        return jsonify({'message': 'El precio de compra es requerido'}), 400
    try:
        purchase_price = float(str(data['purchasePrice']).replace(',', '.'))
    except (TypeError, ValueError):
        return jsonify({'message': 'El precio de compra debe ser un número válido'}), 400

    lead_time_days = None
    if data.get('leadTimeDays') not in (None, ''):
        try:
            lead_time_days = int(data['leadTimeDays'])
        except (TypeError, ValueError):
            return jsonify({'message': 'El tiempo de entrega debe ser un número entero de días'}), 400

    row = SupplierProduct.query.filter_by(supplier_id=supplier.id, product_id=product.id).first()
    if not row:
        row = SupplierProduct(supplier_id=supplier.id, product_id=product.id)
        db.session.add(row)

    row.supplier_sku = data.get('supplierSku') or None
    row.purchase_price = purchase_price
    row.lead_time_days = lead_time_days
    row.is_active = True
    db.session.flush()  # asigna row.id, necesario para excluirla al desmarcar otras preferidas

    if data.get('isPreferred'):
        SupplierProduct.query.filter(
            SupplierProduct.product_id == product.id, SupplierProduct.id != row.id
        ).update({'is_preferred': False})
        row.is_preferred = True
    else:
        row.is_preferred = False

    log_audit(
        int(get_jwt_identity()), 'Proveedores', 'associate_product',
        f'Asoció el producto "{product.name}" al proveedor "{supplier.name}"',
        entity_type='supplier', entity_id=supplier.id,
    )
    db.session.commit()
    return jsonify(_supplier_payload(supplier, include_products=True)), 201


@suppliers_bp.route('/<int:supplier_id>', methods=['DELETE'])
@role_required('admin', 'bodeguero')
def delete_supplier(supplier_id):
    # Borrado permanente real, mismo patron de dos pasos que products: solo
    # se permite sobre proveedores ya inactivos.
    supplier = Supplier.query.get_or_404(supplier_id)
    if supplier.is_active:
        return jsonify({'message': 'Desactiva el proveedor antes de eliminarlo permanentemente'}), 400

    SupplierProduct.query.filter_by(supplier_id=supplier.id).delete()
    supplier_name = supplier.name
    log_audit(
        int(get_jwt_identity()), 'Proveedores', 'delete',
        f'Eliminó permanentemente el proveedor "{supplier_name}"', entity_type='supplier', entity_id=supplier_id,
    )
    db.session.delete(supplier)
    db.session.commit()
    return '', 204
