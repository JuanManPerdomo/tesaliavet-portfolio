import os
from datetime import datetime, date

from flask import Blueprint, request, jsonify, current_app, send_file, abort
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import or_

from ..extensions import db
from ..models import PurchaseOrder, PurchaseOrderDetail, Supplier, Product, SupplierProduct
from ..auth.decorators import role_required
from ..products.routes import _sync_stock_alert
from ..audit.service import diff_snapshot, log_audit, snapshot_fields

purchase_orders_bp = Blueprint('purchase_orders', __name__)

VALID_STATUS_FILTERS = {'Borrador', 'Enviada', 'Recibida', 'Cancelada', 'all'}

ALLOWED_INVOICE_TYPES = {'application/pdf': 'pdf', 'image/jpeg': 'jpg', 'image/png': 'png'}
MAX_INVOICE_SIZE = 5 * 1024 * 1024  # 5MB

# Transiciones legales: desde que estado se puede pasar a cuales otros.
ALLOWED_TRANSITIONS = {
    'Borrador': {'Enviada', 'Cancelada'},
    'Enviada': {'Recibida', 'Cancelada'},
    'Recibida': set(),
    'Cancelada': set(),
}


def _current_user_id():
    uid = get_jwt_identity()
    return int(uid) if uid else None


def _purchase_order_payload(order, include_items=True):
    payload = {
        'id': order.id,
        'supplierId': order.supplier_id,
        'supplierName': order.supplier.name if order.supplier else None,
        'supplierContactPhone': order.supplier.primary_contact_phone if order.supplier else None,
        'supplierContactEmail': order.supplier.primary_contact_email if order.supplier else None,
        'createdBy': order.created_by,
        'createdByName': (
            f'{order.created_by_user.first_name} {order.created_by_user.last_name}'
            if order.created_by_user else None
        ),
        'orderDate': order.order_date.isoformat() if order.order_date else None,
        'expectedDeliveryDate': order.expected_delivery_date.isoformat() if order.expected_delivery_date else None,
        'receivedAt': order.received_at.isoformat() if order.received_at else None,
        'status': order.status,
        'totalAmount': float(order.total_amount),
        'shippingCost': float(order.shipping_cost or 0),
        'taxAmount': float(order.tax_amount or 0),
        'notes': order.notes,
        'invoiceUrl': f'/purchase-orders/{order.id}/invoice' if order.invoice_path else None,
    }

    if include_items:
        payload['itemsSubtotal'] = round(sum(float(item.subtotal or 0) for item in order.details), 2)
        payload['items'] = [{
            'id': item.id,
            'productId': item.product_id,
            'productName': item.product.name if item.product else None,
            'sku': item.product.sku if item.product else None,
            'unitLabel': item.product.unit_label if item.product else None,
            'unitWeightKg': (
                float(item.product.unit_weight_kg)
                if item.product and item.product.unit_weight_kg is not None else None
            ),
            'quantityOrdered': float(item.quantity_ordered),
            'quantityReceived': float(item.quantity_received),
            'unitCost': float(item.unit_cost),
            'subtotal': float(item.subtotal) if item.subtotal is not None else None,
        } for item in order.details]

    return payload


def _validate_items(items_data, supplier_id):
    """Valida y normaliza la lista de items del payload. Devuelve
    (items_normalizados, error) - error es un string si algo esta mal.
    Cada producto debe estar asociado al proveedor de la orden (via
    supplier_products, decision 19) - una orden no mezcla productos de
    varios proveedores, y no se permite repetir el mismo producto en dos
    lineas de la misma orden."""
    if not items_data or not isinstance(items_data, list):
        return None, 'La orden debe tener al menos un producto'

    normalized = []
    seen_product_ids = set()
    for raw in items_data:
        product_id = raw.get('productId')
        product = Product.query.get(int(product_id)) if product_id else None
        if not product:
            return None, 'Uno de los productos de la orden no existe'

        if product.id in seen_product_ids:
            return None, f'"{product.name}" está repetido en la orden'
        seen_product_ids.add(product.id)

        is_associated = SupplierProduct.query.filter_by(
            supplier_id=supplier_id, product_id=product.id, is_active=True
        ).first()
        if not is_associated:
            return None, f'"{product.name}" no está asociado a este proveedor'

        try:
            quantity = round(float(str(raw.get('quantityOrdered', '')).replace(',', '.')), 2)
        except (TypeError, ValueError):
            return None, f'Cantidad inválida para {product.name}'
        if quantity <= 0:
            return None, f'La cantidad de {product.name} debe ser mayor a cero'

        try:
            unit_cost = round(float(str(raw.get('unitCost', '')).replace(',', '.')), 2)
        except (TypeError, ValueError):
            return None, f'Precio de compra inválido para {product.name}'
        if unit_cost < 0:
            return None, f'El precio de compra de {product.name} no puede ser negativo'

        normalized.append({'product': product, 'quantity': quantity, 'unit_cost': unit_cost})

    return normalized, None


def _apply_items(order, normalized_items):
    """Reemplaza por completo los detalles de la orden (solo se usa mientras
    esta en Borrador) y devuelve el subtotal de productos (sin costos
    adicionales) - quien llama decide si recalcula el total con ese valor."""
    PurchaseOrderDetail.query.filter_by(purchase_order_id=order.id).delete()

    items_subtotal = 0
    for item in normalized_items:
        subtotal = round(item['quantity'] * item['unit_cost'], 2)
        items_subtotal += subtotal
        db.session.add(PurchaseOrderDetail(
            purchase_order_id=order.id,
            product_id=item['product'].id,
            quantity_ordered=item['quantity'],
            unit_cost=item['unit_cost'],
            subtotal=subtotal,
        ))

    return round(items_subtotal, 2)


def _recalculate_total(order, items_subtotal):
    """RF40: el total de la orden suma el subtotal de productos mas los
    costos adicionales de cabecera (transporte, impuestos) - hoy en la
    practica casi siempre quedan en cero (el proveedor factura todo
    incluido en el precio), pero el campo queda disponible por si algun
    proveedor los cobra aparte."""
    order.total_amount = round(
        items_subtotal + float(order.shipping_cost or 0) + float(order.tax_amount or 0), 2
    )


def _parse_amount(value):
    """Convierte un costo adicional (transporte/impuestos) a float no
    negativo. Devuelve None si el valor es invalido - el caller decide el
    mensaje de error. Ausente/vacio se trata como 0, no como invalido."""
    if value in (None, ''):
        return 0.0
    try:
        amount = round(float(str(value).replace(',', '.')), 2)
    except (TypeError, ValueError):
        return None
    return amount if amount >= 0 else None


@purchase_orders_bp.route('', methods=['GET'])
@role_required('admin', 'bodeguero')
def list_purchase_orders():
    query = PurchaseOrder.query

    status = request.args.get('status')
    if status not in VALID_STATUS_FILTERS:
        status = 'all'
    if status != 'all':
        query = query.filter_by(status=status)

    supplier_id = request.args.get('supplier_id', type=int)
    if supplier_id:
        query = query.filter_by(supplier_id=supplier_id)

    search = request.args.get('search')
    if search:
        query = query.join(Supplier, PurchaseOrder.supplier_id == Supplier.id).filter(
            or_(Supplier.name.ilike(f'%{search}%'), PurchaseOrder.id == (int(search) if search.isdigit() else -1))
        )

    query = query.order_by(PurchaseOrder.order_date.desc())

    page = request.args.get('page', default=1, type=int)
    per_page = min(request.args.get('per_page', default=20, type=int), 100)

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'purchaseOrders': [_purchase_order_payload(o, include_items=False) for o in paginated.items],
        'total': paginated.total,
        'page': paginated.page,
        'per_page': paginated.per_page,
        'pages': paginated.pages,
    })


@purchase_orders_bp.route('/<int:order_id>', methods=['GET'])
@role_required('admin', 'bodeguero')
def get_purchase_order(order_id):
    order = PurchaseOrder.query.get_or_404(order_id)
    return jsonify(_purchase_order_payload(order))


@purchase_orders_bp.route('', methods=['POST'])
@role_required('admin', 'bodeguero')
def create_purchase_order():
    data = request.get_json(silent=True) or {}

    supplier_id = data.get('supplierId')
    supplier = Supplier.query.get(int(supplier_id)) if supplier_id else None
    if not supplier:
        return jsonify({'message': 'El proveedor es requerido'}), 400

    normalized_items, error = _validate_items(data.get('items'), supplier.id)
    if error:
        return jsonify({'message': error}), 400

    shipping_cost = _parse_amount(data.get('shippingCost'))
    if shipping_cost is None:
        return jsonify({'message': 'El costo de transporte debe ser un número mayor o igual a cero'}), 400

    tax_amount = _parse_amount(data.get('taxAmount'))
    if tax_amount is None:
        return jsonify({'message': 'El costo de impuestos debe ser un número mayor o igual a cero'}), 400

    expected_delivery_date = None
    if data.get('expectedDeliveryDate'):
        try:
            expected_delivery_date = date.fromisoformat(data['expectedDeliveryDate'])
        except ValueError:
            return jsonify({'message': 'Fecha de entrega esperada inválida'}), 400

    order = PurchaseOrder(
        supplier_id=supplier.id,
        created_by=_current_user_id(),
        expected_delivery_date=expected_delivery_date,
        notes=data.get('notes') or None,
        status='Borrador',
        shipping_cost=shipping_cost,
        tax_amount=tax_amount,
    )
    db.session.add(order)
    db.session.flush()  # asigna order.id para los detalles

    items_subtotal = _apply_items(order, normalized_items)
    _recalculate_total(order, items_subtotal)

    log_audit(
        _current_user_id(), 'Proveedores', 'create',
        f'Creó la orden de compra #{order.id} para "{supplier.name}"',
        entity_type='purchase_order', entity_id=order.id,
    )
    db.session.commit()
    return jsonify(_purchase_order_payload(order)), 201


@purchase_orders_bp.route('/<int:order_id>', methods=['PUT'])
@role_required('admin', 'bodeguero')
def update_purchase_order(order_id):
    order = PurchaseOrder.query.get_or_404(order_id)
    if order.status != 'Borrador':
        return jsonify({'message': 'Solo se puede editar una orden en estado Borrador'}), 400
    before = snapshot_fields(order)

    data = request.get_json(silent=True) or {}

    if 'supplierId' in data:
        supplier = Supplier.query.get(int(data['supplierId'])) if data['supplierId'] else None
        if not supplier:
            return jsonify({'message': 'El proveedor es requerido'}), 400
        order.supplier_id = supplier.id

    if 'expectedDeliveryDate' in data:
        if data['expectedDeliveryDate']:
            try:
                order.expected_delivery_date = date.fromisoformat(data['expectedDeliveryDate'])
            except ValueError:
                return jsonify({'message': 'Fecha de entrega esperada inválida'}), 400
        else:
            order.expected_delivery_date = None

    if 'notes' in data:
        order.notes = data['notes'] or None

    if 'shippingCost' in data:
        shipping_cost = _parse_amount(data.get('shippingCost'))
        if shipping_cost is None:
            return jsonify({'message': 'El costo de transporte debe ser un número mayor o igual a cero'}), 400
        order.shipping_cost = shipping_cost

    if 'taxAmount' in data:
        tax_amount = _parse_amount(data.get('taxAmount'))
        if tax_amount is None:
            return jsonify({'message': 'El costo de impuestos debe ser un número mayor o igual a cero'}), 400
        order.tax_amount = tax_amount

    if 'items' in data:
        normalized_items, error = _validate_items(data.get('items'), order.supplier_id)
        if error:
            return jsonify({'message': error}), 400
        items_subtotal = _apply_items(order, normalized_items)
    else:
        items_subtotal = round(sum(float(item.subtotal or 0) for item in order.details), 2)

    _recalculate_total(order, items_subtotal)

    log_audit(
        _current_user_id(), 'Proveedores', 'update',
        f'Editó la orden de compra #{order.id}', entity_type='purchase_order', entity_id=order.id,
        changes=diff_snapshot(order, before),
    )
    db.session.commit()
    return jsonify(_purchase_order_payload(order))


@purchase_orders_bp.route('/<int:order_id>/status', methods=['PUT'])
@role_required('admin', 'bodeguero')
def update_purchase_order_status(order_id):
    order = PurchaseOrder.query.get_or_404(order_id)
    before = snapshot_fields(order)
    data = request.get_json(silent=True) or {}

    new_status = data.get('status')
    if new_status not in ALLOWED_TRANSITIONS.get(order.status, set()):
        return jsonify({
            'message': f'No se puede pasar una orden de "{order.status}" a "{new_status}"'
        }), 400

    if new_status == 'Recibida':
        # Recepcion todo-o-nada: se suma la cantidad pedida de cada linea al
        # stock del producto y se resincroniza su alerta de stock (mismo
        # helper que usa Productos, decision 27), en una sola operacion.
        for item in order.details:
            item.quantity_received = item.quantity_ordered
            product = item.product
            product.stock = (product.stock or 0) + item.quantity_ordered
            _sync_stock_alert(product)
        order.received_at = datetime.now()

    order.status = new_status
    log_audit(
        _current_user_id(), 'Proveedores', 'status_change',
        f'Cambió la orden de compra #{order.id} a "{new_status}"',
        entity_type='purchase_order', entity_id=order.id, changes=diff_snapshot(order, before),
    )
    db.session.commit()
    return jsonify(_purchase_order_payload(order))


@purchase_orders_bp.route('/<int:order_id>', methods=['DELETE'])
@role_required('admin', 'bodeguero')
def delete_purchase_order(order_id):
    # Solo se puede borrar una orden que nunca se envio - una vez Enviada es
    # un documento real del negocio, se cancela pero no se borra (mismo
    # criterio que decision 13 con las citas: el historial no desaparece).
    order = PurchaseOrder.query.get_or_404(order_id)
    if order.status != 'Borrador':
        return jsonify({'message': 'Solo se puede eliminar una orden en estado Borrador'}), 400

    order_id_for_log = order.id
    log_audit(
        _current_user_id(), 'Proveedores', 'delete',
        f'Eliminó la orden de compra #{order_id_for_log}', entity_type='purchase_order', entity_id=order_id_for_log,
    )
    db.session.delete(order)
    db.session.commit()
    return '', 204


@purchase_orders_bp.route('/<int:order_id>/invoice', methods=['POST'])
@role_required('admin', 'bodeguero')
def upload_purchase_order_invoice(order_id):
    # No se restringe por estado: la factura/remision del proveedor suele
    # llegar despues de crear la orden (al enviarla o al recibirla), no en
    # el momento de crearla - a diferencia de las lineas de productos, que
    # solo se pueden editar en Borrador.
    order = PurchaseOrder.query.get_or_404(order_id)

    invoice_file = request.files.get('invoice')
    if not invoice_file or not invoice_file.filename:
        return jsonify({'message': 'Selecciona un archivo para adjuntar'}), 400

    extension = ALLOWED_INVOICE_TYPES.get(invoice_file.mimetype)
    if not extension:
        return jsonify({'message': 'Formato inválido. Solo se aceptan PDF, JPG o PNG.'}), 400

    content = invoice_file.read()
    if len(content) > MAX_INVOICE_SIZE:
        return jsonify({'message': 'El archivo supera el tamaño máximo de 5MB.'}), 400

    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'purchase_orders')
    os.makedirs(upload_dir, exist_ok=True)

    if order.invoice_path:
        old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], order.invoice_path)
        if os.path.exists(old_path):
            os.remove(old_path)

    filename = f'po_{order.id}.{extension}'
    with open(os.path.join(upload_dir, filename), 'wb') as f:
        f.write(content)

    order.invoice_path = f'purchase_orders/{filename}'
    order.invoice_mime = invoice_file.mimetype

    log_audit(
        _current_user_id(), 'Proveedores', 'update',
        f'Adjuntó la factura del proveedor a la orden de compra #{order.id}',
        entity_type='purchase_order', entity_id=order.id,
    )
    db.session.commit()
    return jsonify(_purchase_order_payload(order))


@purchase_orders_bp.route('/<int:order_id>/invoice', methods=['DELETE'])
@role_required('admin', 'bodeguero')
def delete_purchase_order_invoice(order_id):
    """Quita la factura del proveedor sin borrar la orden - pedido explícito
    de Juan Manuel: poder quitar cualquier imagen/adjunto, no solo
    reemplazarlo por otro."""
    order = PurchaseOrder.query.get_or_404(order_id)
    if not order.invoice_path:
        return jsonify({'message': 'Esta orden no tiene factura adjunta'}), 400

    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], order.invoice_path)
    if os.path.exists(full_path):
        os.remove(full_path)
    order.invoice_path = None
    order.invoice_mime = None

    log_audit(
        _current_user_id(), 'Proveedores', 'update',
        f'Quitó la factura del proveedor de la orden de compra #{order.id}',
        entity_type='purchase_order', entity_id=order.id,
    )
    db.session.commit()
    return jsonify(_purchase_order_payload(order))


@purchase_orders_bp.route('/<int:order_id>/invoice', methods=['GET'])
@role_required('admin', 'bodeguero')
def get_purchase_order_invoice(order_id):
    order = PurchaseOrder.query.get_or_404(order_id)
    if not order.invoice_path:
        abort(404)
    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], order.invoice_path)
    if not os.path.exists(full_path):
        abort(404)
    return send_file(full_path, mimetype=order.invoice_mime or 'application/pdf')
