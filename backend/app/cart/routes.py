from decimal import Decimal, InvalidOperation

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models import Cart, CartItem, Product, User
from ..orders.routes import _order_payload, create_order_from_cart
from ..orders.mailer import send_order_confirmed
from ..audit.service import log_audit

cart_bp = Blueprint('cart', __name__)

# Regla de negocio real (decision 28 en CLAUDE.md): sin pasarela de pago
# online, solo Efectivo/Transferencia presenciales - Tarjeta se descarto a
# proposito (el negocio no tiene datafono).
DELIVERY_CITY = 'Tesalia'
VALID_PAYMENT_METHODS = {'Efectivo', 'Transferencia'}


def _current_user_id():
    return int(get_jwt_identity())


def _get_or_create_active_cart():
    cart = Cart.query.filter_by(user_id=_current_user_id(), status='Activo').first()
    if not cart:
        cart = Cart(user_id=_current_user_id(), status='Activo')
        db.session.add(cart)
        db.session.flush()
    return cart


def _cart_item_payload(item):
    product = item.product
    # El carrito siempre muestra el precio/IVA VIGENTE del producto, no el
    # que se guardo cuando se agrego (el que queda congelado es el del
    # pedido ya confirmado, en sales_order_items).
    unit_price = product.selling_price if product else item.unit_price
    tax_rate = product.tax_rate if product else Decimal('0')
    quantity = item.quantity
    subtotal = quantity * unit_price
    tax = subtotal * (tax_rate / Decimal('100'))
    return {
        'id': item.id,
        'productId': item.product_id,
        'productName': product.name if product else None,
        'productImage': (
            f'/products/{item.product_id}/photo' if product and product.image_path else None
        ),
        'quantity': float(quantity),
        'unitPrice': float(unit_price),
        'taxRate': float(tax_rate),
        'stock': float(product.stock) if product else 0,
        'isActive': bool(product.is_active) if product else False,
        'subtotal': float(subtotal),
        'total': float(subtotal + tax),
    }


def _cart_payload(cart):
    items = [_cart_item_payload(i) for i in cart.items]
    subtotal = sum(i['subtotal'] for i in items)
    total = sum(i['total'] for i in items)
    return {
        'id': cart.id,
        'items': items,
        'subtotal': subtotal,
        'taxTotal': total - subtotal,
        'total': total,
        'deliveryCity': DELIVERY_CITY,
    }


@cart_bp.route('', methods=['GET'])
@jwt_required()
def get_cart():
    cart = _get_or_create_active_cart()
    db.session.commit()  # persiste el carrito si se acaba de crear uno vacio
    return jsonify(_cart_payload(cart))


@cart_bp.route('/items', methods=['POST'])
@jwt_required()
def add_item():
    data = request.get_json(silent=True) or {}
    product_id = data.get('productId')
    if not product_id:
        return jsonify({'message': 'El producto es requerido'}), 400

    product = Product.query.filter_by(id=product_id, is_active=True).first()
    if not product:
        return jsonify({'message': 'Producto no encontrado'}), 404

    try:
        quantity = Decimal(str(data.get('quantity', 1)))
    except (InvalidOperation, TypeError):
        return jsonify({'message': 'Cantidad inválida'}), 400
    if quantity <= 0:
        return jsonify({'message': 'La cantidad debe ser mayor a cero'}), 400

    cart = _get_or_create_active_cart()

    item = CartItem.query.filter_by(cart_id=cart.id, product_id=product.id).first()
    new_quantity = (item.quantity if item else Decimal('0')) + quantity
    if new_quantity > product.stock:
        return jsonify({'message': 'No hay suficiente stock disponible para esa cantidad'}), 400

    if item:
        item.quantity = new_quantity
        item.unit_price = product.selling_price
    else:
        item = CartItem(
            cart_id=cart.id, product_id=product.id, quantity=quantity, unit_price=product.selling_price
        )
        db.session.add(item)

    db.session.commit()
    return jsonify(_cart_payload(cart)), 201


@cart_bp.route('/items/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_item(item_id):
    cart = _get_or_create_active_cart()
    item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()
    if not item:
        return jsonify({'message': 'Producto no encontrado en el carrito'}), 404

    data = request.get_json(silent=True) or {}
    try:
        quantity = Decimal(str(data.get('quantity')))
    except (InvalidOperation, TypeError):
        return jsonify({'message': 'Cantidad inválida'}), 400
    if quantity <= 0:
        return jsonify({'message': 'La cantidad debe ser mayor a cero'}), 400
    if item.product and quantity > item.product.stock:
        return jsonify({'message': 'No hay suficiente stock disponible para esa cantidad'}), 400

    item.quantity = quantity
    db.session.commit()
    return jsonify(_cart_payload(cart))


@cart_bp.route('/items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_item(item_id):
    cart = _get_or_create_active_cart()
    item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
    return jsonify(_cart_payload(cart))


@cart_bp.route('/checkout', methods=['POST'])
@jwt_required()
def checkout():
    cart = _get_or_create_active_cart()
    if not cart.items:
        return jsonify({'message': 'Tu carrito está vacío'}), 400

    data = request.get_json(silent=True) or {}
    required = ['shippingName', 'shippingAddress', 'paymentMethod']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'message': f'Faltan campos requeridos: {", ".join(missing)}'}), 400

    payment_method = data['paymentMethod']
    if payment_method not in VALID_PAYMENT_METHODS:
        return jsonify({'message': 'Método de pago inválido'}), 400

    # Gap real (decision 24/34/49 en CLAUDE.md): direccion/ciudad/departamento
    # de users nunca se llenan solas. Si el cliente no tenia departamento
    # registrado, el checkout lo exige aca (el frontend ya lo pide con el
    # mismo desplegable en cascada de /mi-perfil) - si ya lo tenia, no hace
    # falta que lo vuelva a mandar.
    user = User.query.get(_current_user_id())
    if user and not user.departamento:
        departamento = (data.get('departamento') or '').strip()
        ciudad = (data.get('ciudad') or '').strip()
        if not departamento or not ciudad:
            return jsonify({'message': 'Completa tu departamento y municipio para continuar'}), 400

    # Revalida disponibilidad al momento de pagar: pudo cambiar desde que
    # se agrego al carrito.
    for cart_item in cart.items:
        product = cart_item.product
        if not product or not product.is_active:
            return jsonify({'message': 'Un producto de tu carrito ya no está disponible'}), 400
        if cart_item.quantity > product.stock:
            return jsonify({'message': f'No hay suficiente stock de "{product.name}"'}), 400

    order = create_order_from_cart(cart, data, payment_method)
    cart.status = 'Convertido'

    # Si el cliente no tenia direccion/departamento/municipio registrados y
    # los escribio aca para este pedido, se guardan de una vez en su perfil
    # - la proxima compra ya viene prellenada, sin pantalla extra.
    if user and not user.direccion:
        user.direccion = data['shippingAddress'].strip()
    if user and not user.departamento:
        user.departamento = data['departamento'].strip()
        user.ciudad = data['ciudad'].strip()

    log_audit(
        _current_user_id(), 'Ventas', 'create',
        f'Realizó el pedido #{order.id} por $ {order.total:,.0f}', entity_type='sales_order', entity_id=order.id,
    )
    db.session.commit()
    send_order_confirmed(order)

    return jsonify(_order_payload(order)), 201
