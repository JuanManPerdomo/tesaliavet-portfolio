import calendar
from datetime import datetime, timedelta, time
from decimal import Decimal, InvalidOperation

from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_

from ..extensions import db
from ..models import SalesOrder, SalesOrderItem, Invoice, Payment, Return, ReturnItem, User, Product
from ..auth.decorators import role_required
from ..products.routes import _sync_stock_alert
from ..audit.service import diff_snapshot, log_audit, snapshot_fields
from .mailer import send_order_cancelled, send_order_delivered, send_payment_registered, send_return_processed
from ..cash_register.service import get_open_session
from ..reports.exporters import build_pdf

orders_bp = Blueprint('orders', __name__)

VALID_STATUSES = {'Pendiente', 'Pagado', 'Entregado', 'Cancelado'}

# Recogida solo en tienda, decision 28 en CLAUDE.md - no hay envios, asi que
# shipping_city/shipping_address se reinterpretan como direccion de
# facturacion del cliente. No es un campo que el cliente elija.
DELIVERY_CITY = 'Tesalia'

# Plazo real de devoluciones, pedido explicitamente a Juan Manuel antes de
# construir esto (no inventado, mismo criterio que las reglas de citas -
# decision 12 en CLAUDE.md).
RETURN_WINDOW_DAYS = 8
VALID_REFUND_METHODS = {'Efectivo', 'Transferencia'}

# Mismo criterio que el checkout del cliente (decision 28/41): sin pasarela
# de pago online, solo Efectivo/Transferencia presenciales.
VALID_PAYMENT_METHODS = {'Efectivo', 'Transferencia'}


def _current_user_id():
    return int(get_jwt_identity())


def create_order_from_cart(cart, data, payment_method):
    """Crea un SalesOrder + sus SalesOrderItem a partir de un carrito activo
    (decision 28 en CLAUDE.md). No hace commit, el llamador decide cuando
    (despues de, por ejemplo, marcar el carrito como 'Convertido')."""
    order = SalesOrder(
        user_id=cart.user_id,
        status='Pendiente',
        payment_method=payment_method,
        shipping_name=data['shippingName'],
        shipping_phone=data.get('shippingPhone') or None,
        shipping_address=data['shippingAddress'],
        shipping_city=DELIVERY_CITY,
        notes=data.get('notes') or None,
    )
    db.session.add(order)
    db.session.flush()  # asigna order.id, necesario para los items

    subtotal_total = Decimal('0')
    tax_total = Decimal('0')
    for cart_item in cart.items:
        product = cart_item.product
        unit_price = product.selling_price
        tax_rate = product.tax_rate
        quantity = cart_item.quantity
        item_subtotal = quantity * unit_price
        item_tax = item_subtotal * (tax_rate / Decimal('100'))
        subtotal_total += item_subtotal
        tax_total += item_tax

        db.session.add(SalesOrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=quantity,
            unit_price=unit_price,
            tax_rate=tax_rate,
        ))

    order.subtotal = subtotal_total
    order.tax_total = tax_total
    order.total = subtotal_total + tax_total
    return order


def _order_item_payload(item):
    return {
        'id': item.id,
        'productId': item.product_id,
        'productName': item.product.name if item.product else None,
        'productImage': (
            f'/products/{item.product_id}/photo' if item.product and item.product.image_path else None
        ),
        'quantity': float(item.quantity),
        'unitPrice': float(item.unit_price),
        'taxRate': float(item.tax_rate),
        'subtotal': float(item.subtotal) if item.subtotal is not None else None,
        'total': float(item.total) if item.total is not None else None,
    }


def _payment_payload(order):
    invoice = order.invoice
    if not invoice or not invoice.payment:
        return None
    payment = invoice.payment
    return {
        'amount': float(payment.amount),
        'reference': payment.reference,
        'paidAt': payment.paid_at.isoformat() if payment.paid_at else None,
        'registeredByName': (
            f'{payment.registered_by_user.first_name} {payment.registered_by_user.last_name}'
            if payment.registered_by_user else None
        ),
        'invoiceNumber': invoice.invoice_number,
    }


def _return_item_payload(item):
    return {
        'id': item.id,
        'salesOrderItemId': item.sales_order_item_id,
        'productId': item.product_id,
        'productName': item.product.name if item.product else None,
        'quantity': float(item.quantity),
        'unitPrice': float(item.unit_price),
        'amount': float(item.amount),
    }


def _return_payload(ret):
    return {
        'id': ret.id,
        'orderId': ret.order_id,
        'reason': ret.reason,
        'refundMethod': ret.refund_method,
        'refundReference': ret.refund_reference,
        'refundAmount': float(ret.refund_amount),
        'createdAt': ret.created_at.isoformat() if ret.created_at else None,
        'registeredByName': (
            f'{ret.registered_by_user.first_name} {ret.registered_by_user.last_name}'
            if ret.registered_by_user else None
        ),
        'items': [_return_item_payload(item) for item in ret.items],
    }


def _returned_quantity_by_item(order):
    """Cuanto ya se devolvio de cada sales_order_item de este pedido, sumando
    todas las devoluciones previas - usado para topar cuanto se puede
    devolver todavia en una devolucion nueva."""
    totals = {}
    for ret in order.returns:
        for item in ret.items:
            totals[item.sales_order_item_id] = totals.get(item.sales_order_item_id, Decimal('0')) + item.quantity
    return totals


def _order_payload(order):
    return {
        'id': order.id,
        'status': order.status,
        'paymentMethod': order.payment_method,
        'payment': _payment_payload(order),
        'shippingName': order.shipping_name,
        'shippingPhone': order.shipping_phone,
        'shippingAddress': order.shipping_address,
        'shippingCity': order.shipping_city,
        'subtotal': float(order.subtotal),
        'taxTotal': float(order.tax_total),
        'total': float(order.total),
        'notes': order.notes,
        'cancelReason': order.cancel_reason,
        'createdAt': order.created_at.isoformat(),
        'deliveredAt': order.delivered_at.isoformat() if order.delivered_at else None,
        'customerName': (
            f'{order.user.first_name} {order.user.last_name}' if order.user else None
        ),
        'customerEmail': order.user.email if order.user else None,
        'items': [_order_item_payload(item) for item in order.items],
        'returns': [_return_payload(r) for r in order.returns],
    }


@orders_bp.route('', methods=['GET'])
@jwt_required()
def list_my_orders():
    orders = (
        SalesOrder.query.filter_by(user_id=_current_user_id())
        .order_by(SalesOrder.created_at.desc())
        .all()
    )
    return jsonify([_order_payload(o) for o in orders])


@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    user = User.query.get(_current_user_id())
    # Bodeguero tambien puede ver cualquier pedido (no solo el suyo) al
    # vender/registrar pagos cubriendo la caja (decision Bodeguero,
    # 2026-09-02) - mismo criterio de "staff" que admin en este endpoint
    # compartido con el cliente (decision 87).
    is_admin = bool(user) and any(r.name in ('admin', 'bodeguero') for r in user.roles)

    if is_admin:
        order = SalesOrder.query.get_or_404(order_id)
    else:
        order = SalesOrder.query.filter_by(id=order_id, user_id=_current_user_id()).first()
        if not order:
            return jsonify({'message': 'Pedido no encontrado'}), 404

    return jsonify(_order_payload(order))


def _invoice_pdf_bytes(order):
    """Recibo interno en PDF (sin cufe/DIAN, decision 28) - reusa build_pdf
    de reports/exporters.py (mismo patron ya usado en Reportes, decision 52),
    encabezado como KPIs + tabla de lineas del pedido."""
    invoice = order.invoice
    kpis = [
        ('Recibo', invoice.invoice_number),
        ('Fecha', invoice.issue_date.strftime('%d/%m/%Y %H:%M') if invoice.issue_date else '—'),
        ('Cliente', invoice.client_name),
        ('Documento', f'{invoice.client_doc_type} {invoice.client_document}'.strip()),
        ('Método de pago', order.payment_method),
    ]
    if invoice.payment and invoice.payment.reference:
        kpis.append(('Referencia', invoice.payment.reference))

    headers = ['Producto', 'Cantidad', 'Precio unit.', 'IVA', 'Total línea']
    rows = [
        [
            item.product.name if item.product else 'Producto eliminado',
            float(item.quantity),
            f'$ {float(item.unit_price):,.0f}',
            f'{float(item.tax_rate):.0f}%',
            f'$ {float(item.total or 0):,.0f}',
        ]
        for item in order.items
    ]
    rows.append(['', '', '', 'Subtotal', f'$ {float(invoice.subtotal):,.0f}'])
    rows.append(['', '', '', 'IVA', f'$ {float(invoice.tax_total):,.0f}'])
    rows.append(['', '', '', 'Total', f'$ {float(invoice.total):,.0f}'])

    return build_pdf(f'Recibo {invoice.invoice_number} — TesaliaVet', kpis, headers, rows)


@orders_bp.route('/<int:order_id>/invoice/pdf', methods=['GET'])
@jwt_required()
def download_invoice_pdf(order_id):
    # Mismo patron de autorizacion que get_order: admin/bodeguero ven
    # cualquier pedido, el cliente solo el suyo.
    user = User.query.get(_current_user_id())
    is_admin = bool(user) and any(r.name in ('admin', 'bodeguero') for r in user.roles)

    if is_admin:
        order = SalesOrder.query.get_or_404(order_id)
    else:
        order = SalesOrder.query.filter_by(id=order_id, user_id=_current_user_id()).first()
        if not order:
            return jsonify({'message': 'Pedido no encontrado'}), 404

    if not order.invoice:
        return jsonify({'message': 'Este pedido todavía no tiene un pago registrado'}), 400

    content = _invoice_pdf_bytes(order)
    return Response(
        content, mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment; filename="{order.invoice.invoice_number}.pdf"'},
    )


def _order_search_filter(search):
    # Matchea ID de pedido (si es numerico), nombre/correo del cliente, o
    # nombre de producto en alguna linea - .has()/.any() en vez de join
    # explicito para no duplicar filas por pedidos con varias lineas.
    like = f'%{search}%'
    conditions = [
        SalesOrder.user.has(or_(User.first_name.ilike(like), User.last_name.ilike(like), User.email.ilike(like))),
        SalesOrder.items.any(SalesOrderItem.product.has(Product.name.ilike(like))),
    ]
    if search.isdigit():
        conditions.append(SalesOrder.id == int(search))
    return or_(*conditions)


@orders_bp.route('/staff', methods=['GET'])
@role_required('admin', 'bodeguero')
def list_staff_orders():
    query = SalesOrder.query

    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)

    owner_id = request.args.get('owner_id', type=int)
    if owner_id:
        # Usado desde el detalle de un cliente en /panel/clientes para ver
        # sus pedidos (mismo patron que appointments/routes.py).
        query = query.filter_by(user_id=owner_id)

    search = request.args.get('search')
    if search:
        query = query.filter(_order_search_filter(search))

    orders = query.order_by(SalesOrder.created_at.desc()).all()
    return jsonify([_order_payload(o) for o in orders])


@orders_bp.route('/staff/<int:order_id>', methods=['PUT'])
@role_required('admin', 'bodeguero')
def update_order_staff(order_id):
    # Solo mueve el estado de cumplimiento (Entregado/Cancelado) - pasar a
    # 'Pagado' es exclusivo de POST /staff/<id>/payment (decision 28: el
    # pago se registra aparte, con su propio recibo).
    order = SalesOrder.query.get_or_404(order_id)
    before = snapshot_fields(order)
    data = request.get_json(silent=True) or {}

    if 'status' in data:
        status = data['status']
        if status not in VALID_STATUSES or status == 'Pagado':
            return jsonify({'message': 'Estado inválido'}), 400
        if status == 'Entregado' and order.status != 'Pagado':
            return jsonify({'message': 'Solo se puede entregar un pedido ya pagado'}), 400

        cancel_reason = None
        if status == 'Cancelado':
            # RF25 (matriz de trazabilidad): anular una venta exige motivo
            # obligatorio, sin importar si ya estaba pagada/facturada o
            # todavia Pendiente - mismo criterio que la justificacion
            # obligatoria de una diferencia de caja (decision 46).
            cancel_reason = (data.get('cancelReason') or '').strip()
            if not cancel_reason:
                return jsonify({'message': 'La anulación requiere un motivo'}), 400

        if status == 'Entregado':
            order.delivered_at = datetime.now()
        order.status = status
        if cancel_reason:
            order.cancel_reason = cancel_reason

        action = 'cancel' if status == 'Cancelado' else 'status_change'
        description = (
            f'Anuló el pedido #{order.id} — motivo: {cancel_reason}'
            if status == 'Cancelado'
            else f'Cambió el pedido #{order.id} a "{status}"'
        )
        log_audit(
            int(get_jwt_identity()), 'Ventas', action,
            description, entity_type='sales_order', entity_id=order.id, changes=diff_snapshot(order, before),
        )

    db.session.commit()
    if 'status' in data:
        if data['status'] == 'Entregado':
            send_order_delivered(order)
        elif data['status'] == 'Cancelado':
            send_order_cancelled(order)
    return jsonify(_order_payload(order))


def _finalize_payment(order, payment_method, amount, cash_session, reference=None, notes=None):
    """Crea el recibo interno (Invoice, sin cufe/DIAN) y la fila de Payment de
    un pedido, lo pasa a 'Pagado' y descuenta el stock vendido (decision 80 -
    el stock nunca se reserva en el checkout/POS, se descuenta recien aca).
    Compartido por register_payment (pago de un pedido creado online,
    decision 41) y register_walkin_sale (venta presencial, decision 81) - no
    hace commit, el llamador decide cuando."""
    customer = order.user
    invoice = Invoice(
        order_id=order.id,
        invoice_number=f'REC-{order.id:06d}',
        client_name=f'{customer.first_name} {customer.last_name}' if customer else order.shipping_name,
        client_document=customer.numero_documento if customer else '',
        client_doc_type=customer.tipo_documento if customer else '',
        client_email=customer.email if customer else None,
        client_address=order.shipping_address,
        subtotal=order.subtotal,
        tax_total=order.tax_total,
        total=order.total,
        status='Emitida',
    )
    db.session.add(invoice)
    db.session.flush()  # asigna invoice.id

    payment = Payment(
        invoice_id=invoice.id,
        amount=amount,
        payment_method=payment_method,
        reference=reference,
        registered_by=_current_user_id(),
        notes=notes,
        cash_register_session_id=cash_session.id,
    )
    db.session.add(payment)

    order.status = 'Pagado'

    for item in order.items:
        product = item.product
        if product is None:
            continue
        new_stock = (product.stock or Decimal('0')) - item.quantity
        product.stock = new_stock if new_stock > 0 else Decimal('0')
        _sync_stock_alert(product)

    return invoice, payment


@orders_bp.route('/staff/<int:order_id>/payment', methods=['POST'])
@role_required('admin', 'bodeguero')
def register_payment(order_id):
    # Registra el pago manual (Efectivo/Transferencia, decision 28 en
    # CLAUDE.md) de un pedido creado por el cliente en la app - el pedido ya
    # existe en 'Pendiente', esto solo confirma que se cobro.
    order = SalesOrder.query.get_or_404(order_id)

    if order.status != 'Pendiente':
        return jsonify({'message': 'Este pedido ya no está pendiente de pago'}), 400
    if order.invoice:
        return jsonify({'message': 'Este pedido ya tiene un pago registrado'}), 400

    cash_session = get_open_session()
    if not cash_session:
        return jsonify({'message': 'No hay una caja abierta. Abre la caja antes de registrar pagos.'}), 400

    data = request.get_json(silent=True) or {}
    try:
        amount = Decimal(str(data.get('amount')))
    except (InvalidOperation, TypeError):
        return jsonify({'message': 'El monto es requerido'}), 400
    if amount <= 0:
        return jsonify({'message': 'El monto debe ser mayor a cero'}), 400

    invoice, _payment = _finalize_payment(
        order, order.payment_method, amount, cash_session,
        reference=data.get('reference') or None, notes=data.get('notes') or None,
    )

    log_audit(
        _current_user_id(), 'Ventas', 'register_payment',
        f'Registró el pago del pedido #{order.id} ($ {amount:,.0f})', entity_type='sales_order', entity_id=order.id,
    )
    db.session.commit()
    send_payment_registered(order, invoice, _invoice_pdf_bytes(order))

    return jsonify(_order_payload(order)), 201


@orders_bp.route('/staff', methods=['POST'])
@role_required('admin', 'bodeguero')
def register_walkin_sale():
    """Punto de venta: registra una venta presencial de punta a punta (pedido
    + pago juntos, en un solo paso porque el cliente paga en el momento) -
    unica forma real de dejar en el sistema una venta que no paso por el
    checkout de la app (decision 81 en CLAUDE.md). El cliente debe ser una
    cuenta ya registrada (rol 'cliente') - si no existe, se crea primero
    desde /panel/usuarios (decision 29), no aca."""
    cash_session = get_open_session()
    if not cash_session:
        return jsonify({'message': 'No hay una caja abierta. Abre la caja antes de registrar una venta.'}), 400

    data = request.get_json(silent=True) or {}

    customer_id = data.get('customerId')
    customer = User.query.get(customer_id) if customer_id else None
    if not customer or not customer.is_active or not any(r.name == 'cliente' for r in customer.roles):
        return jsonify({'message': 'Selecciona un cliente activo'}), 400

    payment_method = data.get('paymentMethod')
    if payment_method not in VALID_PAYMENT_METHODS:
        return jsonify({'message': 'Método de pago inválido'}), 400

    items_data = data.get('items') or []
    if not items_data:
        return jsonify({'message': 'Agrega al menos un producto'}), 400

    resolved_items = []
    subtotal_total = Decimal('0')
    tax_total = Decimal('0')
    for entry in items_data:
        product = Product.query.filter_by(id=entry.get('productId'), is_active=True).first()
        if not product:
            return jsonify({'message': 'Uno de los productos ya no está disponible'}), 400
        try:
            quantity = Decimal(str(entry.get('quantity')))
        except (InvalidOperation, TypeError):
            return jsonify({'message': 'Cantidad inválida'}), 400
        if quantity <= 0:
            return jsonify({'message': 'La cantidad debe ser mayor a cero'}), 400
        if quantity > product.stock:
            return jsonify({'message': f'No hay suficiente stock de "{product.name}"'}), 400

        unit_price = product.selling_price
        tax_rate = product.tax_rate
        item_subtotal = quantity * unit_price
        item_tax = item_subtotal * (tax_rate / Decimal('100'))
        subtotal_total += item_subtotal
        tax_total += item_tax
        resolved_items.append((product, quantity, unit_price, tax_rate))

    order = SalesOrder(
        user_id=customer.id,
        status='Pendiente',
        payment_method=payment_method,
        shipping_name=f'{customer.first_name} {customer.last_name}',
        shipping_phone=customer.phone or None,
        # shipping_address/city son la direccion de facturacion (decision 28,
        # sin envios) - para una venta en el mostrador no tiene sentido
        # pedirsela al cliente, se usa la que ya tenga guardada o un
        # marcador generico si no tiene ninguna.
        shipping_address=customer.direccion or 'Venta registrada en tienda física',
        shipping_city=DELIVERY_CITY,
        notes=data.get('notes') or None,
        subtotal=subtotal_total,
        tax_total=tax_total,
        total=subtotal_total + tax_total,
    )
    db.session.add(order)
    db.session.flush()  # asigna order.id

    for product, quantity, unit_price, tax_rate in resolved_items:
        db.session.add(SalesOrderItem(
            order_id=order.id, product_id=product.id, quantity=quantity,
            unit_price=unit_price, tax_rate=tax_rate,
        ))

    invoice, _payment = _finalize_payment(
        order, payment_method, order.total, cash_session,
        reference=data.get('reference') or None, notes=data.get('notes') or None,
    )

    log_audit(
        _current_user_id(), 'Ventas', 'pos_sale',
        f'Registró una venta presencial #{order.id} ($ {order.total:,.0f}) a '
        f'{customer.first_name} {customer.last_name}',
        entity_type='sales_order', entity_id=order.id,
    )
    db.session.commit()
    send_payment_registered(order, invoice, _invoice_pdf_bytes(order))

    return jsonify(_order_payload(order)), 201


def _return_search_filter(search):
    like = f'%{search}%'
    conditions = [
        Return.order.has(SalesOrder.user.has(
            or_(User.first_name.ilike(like), User.last_name.ilike(like), User.email.ilike(like))
        )),
        Return.items.any(ReturnItem.product.has(Product.name.ilike(like))),
    ]
    if search.isdigit():
        conditions.append(Return.order_id == int(search))
    return or_(*conditions)


@orders_bp.route('/staff/returns', methods=['GET'])
@role_required('admin')
def list_staff_returns():
    query = Return.query

    search = request.args.get('search')
    if search:
        query = query.filter(_return_search_filter(search))

    returns = query.order_by(Return.created_at.desc()).all()
    return jsonify([
        {
            **_return_payload(r),
            'orderCustomerName': (
                f'{r.order.user.first_name} {r.order.user.last_name}' if r.order and r.order.user else None
            ),
        }
        for r in returns
    ])


@orders_bp.route('/staff/<int:order_id>/returns', methods=['POST'])
@role_required('admin')
def register_return(order_id):
    # Devolucion parcial sobre un pedido ya Entregado, dentro de un plazo
    # real de 8 dias (RETURN_WINDOW_DAYS) - reglas pedidas explicitamente a
    # Juan Manuel antes de construir esto. Es el espejo de "registrar pago":
    # un hecho ya consumado (el que un admin la registre ya es la
    # aprobacion), suma stock de vuelta y deja el registro de cuanto se
    # reembolsa - el reembolso en si pasa fuera del sistema (efectivo en
    # caja o transferencia manual), igual que el pago original.
    order = SalesOrder.query.get_or_404(order_id)

    if order.status != 'Entregado':
        return jsonify({'message': 'Solo se pueden devolver pedidos ya entregados'}), 400
    if not order.delivered_at or datetime.now() - order.delivered_at > timedelta(days=RETURN_WINDOW_DAYS):
        return jsonify({'message': f'El plazo de {RETURN_WINDOW_DAYS} días para devoluciones ya venció'}), 400

    cash_session = get_open_session()
    if not cash_session:
        return jsonify({'message': 'No hay una caja abierta. Abre la caja antes de registrar devoluciones.'}), 400

    data = request.get_json(silent=True) or {}
    reason = (data.get('reason') or '').strip()
    refund_method = data.get('refundMethod')
    items_data = data.get('items') or []

    if not reason:
        return jsonify({'message': 'El motivo es requerido'}), 400
    if refund_method not in VALID_REFUND_METHODS:
        return jsonify({'message': 'Método de reembolso inválido'}), 400
    if not items_data:
        return jsonify({'message': 'Selecciona al menos un producto a devolver'}), 400

    already_returned = _returned_quantity_by_item(order)
    order_items_by_id = {item.id: item for item in order.items}

    return_items = []
    products_to_restock = []  # (product, quantity) - order_item.product ya esta cargado
    refund_amount = Decimal('0')
    for entry in items_data:
        order_item = order_items_by_id.get(entry.get('salesOrderItemId'))
        if not order_item:
            return jsonify({'message': 'Producto no encontrado en este pedido'}), 400
        try:
            quantity = Decimal(str(entry.get('quantity')))
        except (InvalidOperation, TypeError):
            return jsonify({'message': 'Cantidad inválida'}), 400
        if quantity <= 0:
            continue

        remaining = order_item.quantity - already_returned.get(order_item.id, Decimal('0'))
        if quantity > remaining:
            return jsonify({
                'message': f'No puedes devolver más de {remaining} de "{order_item.product.name}"'
            }), 400

        amount = quantity * order_item.unit_price * (1 + order_item.tax_rate / Decimal('100'))
        refund_amount += amount
        return_items.append(ReturnItem(
            sales_order_item_id=order_item.id,
            product_id=order_item.product_id,
            quantity=quantity,
            unit_price=order_item.unit_price,
            tax_rate=order_item.tax_rate,
            amount=amount,
        ))
        products_to_restock.append((order_item.product, quantity))

    if not return_items:
        return jsonify({'message': 'Selecciona al menos un producto a devolver'}), 400

    ret = Return(
        order_id=order.id,
        registered_by=_current_user_id(),
        reason=reason,
        refund_method=refund_method,
        refund_reference=data.get('refundReference') or None,
        refund_amount=refund_amount,
        cash_register_session_id=cash_session.id,
    )
    ret.items = return_items
    db.session.add(ret)

    for product, quantity in products_to_restock:
        product.stock = (product.stock or 0) + quantity
        _sync_stock_alert(product)

    log_audit(
        _current_user_id(), 'Ventas', 'register_return',
        f'Registró una devolución de $ {refund_amount:,.0f} en el pedido #{order.id}',
        entity_type='sales_order', entity_id=order.id,
    )
    db.session.commit()
    send_return_processed(order, ret)

    return jsonify(_order_payload(order)), 201


# --- Dashboard de Inicio (decision 47 en CLAUDE.md) ------------------------
# Mismo criterio de "neto" que ya usa Caja (decision 46): pagos - devoluciones
# del rango, sin mezclar el fondo base de ninguna sesion (esto es un resumen
# de ventas, no un cuadre de caja).

DASHBOARD_CHART_HOURS = range(7, 20)  # 7am-7pm, mismo horario tipico de atencion
MONTH_LABELS = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']


def _net_income_between(start, end):
    payments = Payment.query.filter(Payment.paid_at >= start, Payment.paid_at < end).all()
    returns = Return.query.filter(Return.created_at >= start, Return.created_at < end).all()
    income = sum((p.amount for p in payments), Decimal('0'))
    refunded = sum((r.refund_amount for r in returns), Decimal('0'))
    return income - refunded


def _sales_count_between(start, end):
    return Payment.query.filter(Payment.paid_at >= start, Payment.paid_at < end).count()


def _percent_change(current, previous):
    if not previous:
        return None
    return float((Decimal(str(current)) - Decimal(str(previous))) / Decimal(str(previous)) * 100)


def _months_back(base_date, n):
    """Año/mes que quedan n meses antes de base_date (n=0 -> el mismo mes)."""
    month = base_date.month - n
    year = base_date.year
    while month <= 0:
        month += 12
        year -= 1
    return year, month


def _month_bounds(year, month):
    days_in_month = calendar.monthrange(year, month)[1]
    start = datetime(year, month, 1)
    end = start + timedelta(days=days_in_month)
    return start, end


@orders_bp.route('/staff/kpis', methods=['GET'])
@role_required('admin')
def dashboard_kpis():
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    today_start = datetime.combine(today, time.min)
    yesterday_start = datetime.combine(yesterday, time.min)

    income_today = _net_income_between(today_start, today_start + timedelta(days=1))
    income_yesterday = _net_income_between(yesterday_start, today_start)
    sales_today = _sales_count_between(today_start, today_start + timedelta(days=1))
    sales_yesterday = _sales_count_between(yesterday_start, today_start)

    return jsonify({
        'incomeToday': float(income_today),
        'incomeChangePercent': _percent_change(income_today, income_yesterday),
        'salesToday': sales_today,
        'salesChangePercent': _percent_change(sales_today, sales_yesterday),
    })


@orders_bp.route('/staff/income-chart', methods=['GET'])
@role_required('admin')
def income_chart():
    range_param = request.args.get('range', 'semana')
    if range_param not in ('dia', 'semana', 'mes', 'año'):
        return jsonify({'message': 'Rango inválido'}), 400

    now = datetime.now()
    today = now.date()
    series = []

    if range_param == 'dia':
        for hour in DASHBOARD_CHART_HOURS:
            start = datetime.combine(today, time(hour=hour))
            end = start + timedelta(hours=1)
            label = f'{hour if hour <= 12 else hour - 12}{"am" if hour < 12 else "pm"}'
            series.append({'label': label, 'value': float(_net_income_between(start, end))})
        current_total = _net_income_between(datetime.combine(today, time.min), now)
        prev_day = today - timedelta(days=1)
        previous_total = _net_income_between(
            datetime.combine(prev_day, time.min), datetime.combine(today, time.min)
        )

    elif range_param == 'semana':
        monday = today - timedelta(days=today.weekday())
        day_count = (today - monday).days + 1
        day_labels = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        for i in range(day_count):
            d = monday + timedelta(days=i)
            start = datetime.combine(d, time.min)
            end = start + timedelta(days=1)
            label = 'Hoy' if d == today else day_labels[d.weekday()]
            series.append({'label': label, 'value': float(_net_income_between(start, end))})
        current_total = sum(Decimal(str(s['value'])) for s in series)
        prev_monday = monday - timedelta(days=7)
        previous_total = _net_income_between(
            datetime.combine(prev_monday, time.min), datetime.combine(prev_monday + timedelta(days=day_count), time.min)
        )

    elif range_param == 'mes':
        for i in range(5, -1, -1):
            year, month = _months_back(today, i)
            start, end = _month_bounds(year, month)
            series.append({'label': MONTH_LABELS[month - 1], 'value': float(_net_income_between(start, end))})
        current_total = sum(Decimal(str(s['value'])) for s in series)

        previous_total = Decimal('0')
        for i in range(11, 5, -1):
            year, month = _months_back(today, i)
            start, end = _month_bounds(year, month)
            previous_total += _net_income_between(start, end)

    else:  # año - a diferencia de Reportes (que sí desglosa un año por mes),
        # acá cada barra es UN AÑO completo - los últimos 5, año calendario
        # en curso incluido (parcial) - mismo patrón de ventana móvil que ya
        # usa "mes" (6 meses vs. los 6 anteriores), un nivel más arriba: 5
        # años vs. los 5 años anteriores a ese bloque.
        for i in range(4, -1, -1):
            y = today.year - i
            start = datetime(y, 1, 1)
            end = datetime(y, 12, 31) + timedelta(days=1) if y < today.year else now
            series.append({'label': str(y), 'value': float(_net_income_between(start, end))})
        current_total = sum(Decimal(str(s['value'])) for s in series)

        previous_total = Decimal('0')
        for i in range(9, 4, -1):
            y = today.year - i
            start, end = datetime(y, 1, 1), datetime(y, 12, 31) + timedelta(days=1)
            previous_total += _net_income_between(start, end)

    return jsonify({
        'range': range_param,
        'series': series,
        'total': float(current_total),
        'comparisonPercent': _percent_change(current_total, previous_total),
    })


@orders_bp.route('/staff/recent-payments', methods=['GET'])
@role_required('admin')
def recent_payments():
    limit = min(request.args.get('limit', default=6, type=int), 20)
    payments = Payment.query.order_by(Payment.paid_at.desc()).limit(limit).all()
    return jsonify([
        {
            'id': p.id,
            'orderId': p.invoice.order_id if p.invoice else None,
            'invoiceNumber': p.invoice.invoice_number if p.invoice else None,
            'customerName': (
                f'{p.invoice.order.user.first_name} {p.invoice.order.user.last_name}'
                if p.invoice and p.invoice.order and p.invoice.order.user
                else (p.invoice.client_name if p.invoice else None)
            ),
            'amount': float(p.amount),
            'method': p.payment_method,
            'paidAt': p.paid_at.isoformat() if p.paid_at else None,
        }
        for p in payments
    ])
