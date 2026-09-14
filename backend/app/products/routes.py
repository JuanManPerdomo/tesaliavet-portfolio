import os
import random
import re
import unicodedata
from datetime import datetime

from flask import Blueprint, request, jsonify, send_file, abort, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from sqlalchemy import func, or_

from ..extensions import db
from ..models import (
    Product, Category, Species, User, SupplierProduct, StockAlert, SalesOrder, SalesOrderItem,
    PurchaseOrderDetail, ReturnItem, CartItem,
)
from ..auth.decorators import role_required
from ..audit.service import diff_snapshot, log_audit, snapshot_fields

products_bp = Blueprint('products', __name__)

SORT_OPTIONS = {
    'price_asc': Product.selling_price.asc(),
    'price_desc': Product.selling_price.desc(),
    'newest': Product.created_at.desc(),
}

ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png'}
EXTENSION_BY_MIME = {'image/jpeg': 'jpg', 'image/png': 'png'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

VALID_TAX_RATES = {0.0, 5.0, 19.0}
VALID_UNITS = {'Unidad', 'Bulto', 'Caja', 'Kg', 'Gramo', 'Arroba', 'Litro', 'Mililitro', 'Onza'}
VALID_STATUS_FILTERS = {'active', 'inactive', 'all'}


def _category_sku_prefix(category):
    """Deriva un prefijo de 3+ letras a partir del nombre de la categoria
    (sin tildes, solo letras, mayusculas) - ej. "Medicamentos" -> "MED".
    Si ese prefijo ya lo usa una categoria DISTINTA (revisando los SKU
    reales, no un catalogo de abreviaturas aparte), se alarga letra por
    letra hasta que quede libre - evita que dos categorias terminen
    compartiendo el mismo prefijo por coincidencia."""
    normalized = unicodedata.normalize('NFKD', category.name or '').encode('ascii', 'ignore').decode('ascii')
    letters = re.sub(r'[^A-Za-z]', '', normalized).upper() or 'PRD'

    length = 3
    while length <= len(letters) and length <= 6:
        candidate = letters[:length]
        conflict = Product.query.filter(
            Product.category_id != category.id, Product.sku.like(f'{candidate}-%')
        ).first()
        if not conflict:
            return candidate
        length += 1

    return letters[:6]


def _next_sku_for_prefix(prefix):
    """Siguiente numero libre de 3 digitos para un prefijo (ej. MED-002),
    mirando los SKU reales que ya empiezan con ese prefijo - no un
    contador aparte, asi nunca se desincroniza si se borra/edita un
    producto a mano."""
    pattern = re.compile(rf'^{re.escape(prefix)}-(\d+)$')
    max_number = 0
    skus = db.session.query(Product.sku).filter(Product.sku.like(f'{prefix}-%')).all()
    for (sku,) in skus:
        match = pattern.match(sku or '')
        if match:
            max_number = max(max_number, int(match.group(1)))
    return max_number + 1


def _requesting_staff_with_product_access():
    """True si la request trae un JWT valido de un usuario con rol admin o
    bodeguero (los dos roles que gestionan el catalogo completo, incluidos
    inactivos - decision Bodeguero, 2026-09-02). No falla si no hay JWT (uso
    publico del catalogo)."""
    try:
        verify_jwt_in_request(optional=True)
    except Exception:
        return False
    uid = get_jwt_identity()
    if not uid:
        return False
    user = User.query.get(int(uid))
    return bool(user) and any(r.name in ('admin', 'bodeguero') for r in user.roles)


def _preferred_supplier(product):
    return SupplierProduct.query.filter_by(product_id=product.id, is_preferred=True).first()


def _sync_stock_alert(product):
    """Crea/actualiza/resuelve la alerta de stock del producto segun su
    stock/min_stock actuales - stock_alerts es un log de eventos real (tiene
    resolved_at/resolved_by), no solo un espejo de products, asi que se
    mantiene sincronizada aqui en vez de calcularse al vuelo en cada lectura."""
    active_alert = StockAlert.query.filter_by(product_id=product.id, status='Activa').first()
    is_low = product.is_active and product.stock <= product.min_stock

    if is_low:
        if active_alert:
            active_alert.current_stock = product.stock
            active_alert.min_stock = product.min_stock
        else:
            db.session.add(StockAlert(
                product_id=product.id,
                current_stock=product.stock,
                min_stock=product.min_stock,
            ))
    elif active_alert:
        active_alert.status = 'Resuelta'
        active_alert.resolved_at = datetime.now()
        uid = get_jwt_identity()
        active_alert.resolved_by = int(uid) if uid else None


def _product_payload(product):
    category = product.category
    preferred = _preferred_supplier(product)
    return {
        'id': product.id,
        'sku': product.sku,
        'barcode': product.barcode,
        'name': product.name,
        'description': product.description,
        'brand': product.brand,
        'purchasePrice': float(product.purchase_price),
        'price': float(product.selling_price),
        'stock': float(product.stock),
        'minStock': float(product.min_stock),
        'unitLabel': product.unit_label,
        'unitWeightKg': float(product.unit_weight_kg) if product.unit_weight_kg is not None else None,
        'taxRate': float(product.tax_rate),
        'isActive': product.is_active,
        'category': {
            'id': category.id,
            'name': category.name,
            'parentId': category.parent_id,
            'parentName': category.parent.name if category.parent else None,
        } if category else None,
        'species': {'id': product.species.id, 'name': product.species.name} if product.species else None,
        'supplier': {'id': preferred.supplier.id, 'name': preferred.supplier.name} if preferred else None,
        'image': f'/products/{product.id}/photo' if product.image_path else None,
    }


def _apply_filters(query):
    category_ids = request.args.getlist('category_id', type=int)
    if category_ids:
        query = query.filter(Product.category_id.in_(category_ids))

    species_ids = request.args.getlist('species_id', type=int)
    if species_ids:
        query = query.filter(Product.species_id.in_(species_ids))

    brands = request.args.getlist('brand')
    if brands:
        query = query.filter(Product.brand.in_(brands))

    min_price = request.args.get('min_price', type=float)
    if min_price is not None:
        query = query.filter(Product.selling_price >= min_price)

    max_price = request.args.get('max_price', type=float)
    if max_price is not None:
        query = query.filter(Product.selling_price <= max_price)

    search = request.args.get('search')
    if search:
        query = query.filter(or_(Product.name.ilike(f'%{search}%'), Product.sku.ilike(f'%{search}%')))

    return query


def _products_upload_dir():
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'products')
    os.makedirs(path, exist_ok=True)
    return path


def _save_product_photo(product, photo_file):
    if photo_file.mimetype not in ALLOWED_IMAGE_TYPES:
        return 'La imagen debe ser JPG o PNG'
    content = photo_file.read()
    if len(content) > MAX_IMAGE_SIZE:
        return 'La imagen no debe superar 5MB'

    upload_dir = _products_upload_dir()
    for existing in os.listdir(upload_dir):
        if existing.startswith(f'product_{product.id}.'):
            os.remove(os.path.join(upload_dir, existing))

    filename = f'product_{product.id}.{EXTENSION_BY_MIME[photo_file.mimetype]}'
    with open(os.path.join(upload_dir, filename), 'wb') as f:
        f.write(content)

    product.image_path = f'products/{filename}'
    product.image_mime = photo_file.mimetype
    return None


def _remove_product_photo(product):
    """Deja el producto sin foto (borra el archivo real de disco) - pedido
    explícito de Juan Manuel: en todo lo que suba una imagen, poder
    quitarla por completo, no solo reemplazarla por otra."""
    if not product.image_path:
        return
    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product.image_path)
    if os.path.exists(full_path):
        os.remove(full_path)
    product.image_path = None
    product.image_mime = None


def _sync_supplier(product, supplier_id_raw):
    """Gestiona la fila supplier_products preferida del producto (a lo sumo una,
    ver decision de disenio: se reutiliza supplier_products en vez de agregar
    products.supplier_id)."""
    if supplier_id_raw is None:
        return None

    SupplierProduct.query.filter_by(product_id=product.id, is_preferred=True).update(
        {'is_preferred': False}
    )

    if not supplier_id_raw:
        return None

    try:
        supplier_id = int(supplier_id_raw)
    except (TypeError, ValueError):
        return 'Proveedor inválido'

    row = SupplierProduct.query.filter_by(product_id=product.id, supplier_id=supplier_id).first()
    if row:
        row.is_preferred = True
        row.purchase_price = product.purchase_price
    else:
        db.session.add(SupplierProduct(
            product_id=product.id,
            supplier_id=supplier_id,
            purchase_price=product.purchase_price,
            is_preferred=True,
        ))
    return None


def _apply_product_fields(product, data):
    if 'sku' in data:
        if not data['sku']:
            return 'El SKU es requerido'
        product.sku = data['sku']

    if 'name' in data:
        if not data['name']:
            return 'El nombre del producto es requerido'
        product.name = data['name']

    if 'categoryId' in data:
        if not data['categoryId']:
            return 'La categoría es requerida'
        try:
            product.category_id = int(data['categoryId'])
        except ValueError:
            return 'Categoría inválida'

    if 'speciesId' in data:
        if data['speciesId']:
            try:
                product.species_id = int(data['speciesId'])
            except ValueError:
                return 'Especie inválida'
        else:
            product.species_id = None

    if 'barcode' in data:
        product.barcode = data['barcode'] or None

    if 'description' in data:
        product.description = data['description'] or None

    if 'brand' in data:
        product.brand = data['brand'] or None

    if 'purchasePrice' in data:
        try:
            product.purchase_price = float(str(data['purchasePrice']).replace(',', '.'))
        except (TypeError, ValueError):
            return 'El precio de compra debe ser un número válido'

    if 'sellingPrice' in data:
        try:
            product.selling_price = float(str(data['sellingPrice']).replace(',', '.'))
        except (TypeError, ValueError):
            return 'El precio de venta debe ser un número válido'

    if 'stock' in data:
        try:
            stock = float(str(data['stock']).replace(',', '.'))
        except (TypeError, ValueError):
            return 'El stock debe ser un número válido'
        # Regla de negocio pedida por Juan Manuel (2026-08-28): el stock se
        # cuenta en unidades completas, sin decimales - a diferencia de las
        # cantidades de una venta/compra/devolucion puntual, que si pueden
        # ser fraccionarias para productos por Kg/Litro (decision 33).
        if stock != int(stock):
            return 'El stock debe ser un número entero, sin decimales'
        product.stock = stock

    if 'minStock' in data:
        try:
            min_stock = float(str(data['minStock']).replace(',', '.'))
        except (TypeError, ValueError):
            return 'El stock mínimo debe ser un número válido'
        if min_stock != int(min_stock):
            return 'El stock mínimo debe ser un número entero, sin decimales'
        product.min_stock = min_stock

    if 'unitLabel' in data:
        unit_label = data['unitLabel']
        if unit_label not in VALID_UNITS:
            return 'Unidad de medida inválida'
        product.unit_label = unit_label

    if 'unitWeightKg' in data:
        if data['unitWeightKg'] in (None, ''):
            product.unit_weight_kg = None
        else:
            try:
                unit_weight_kg = float(str(data['unitWeightKg']).replace(',', '.'))
            except (TypeError, ValueError):
                return 'El peso por unidad debe ser un número válido'
            if unit_weight_kg <= 0:
                return 'El peso por unidad debe ser mayor a cero'
            product.unit_weight_kg = unit_weight_kg

    if 'taxRate' in data:
        try:
            tax_rate = float(str(data['taxRate']).replace(',', '.'))
        except (TypeError, ValueError):
            return 'El IVA debe ser un número válido'
        if tax_rate not in VALID_TAX_RATES:
            return 'El IVA debe ser 0%, 5% o 19%'
        product.tax_rate = tax_rate

    if 'isActive' in data:
        value = data['isActive']
        product.is_active = value if isinstance(value, bool) else str(value).lower() in ('true', '1', 'on')

    return None


@products_bp.route('', methods=['GET'])
def list_products():
    is_admin = _requesting_staff_with_product_access()

    query = Product.query
    status = request.args.get('status')
    if is_admin and status in VALID_STATUS_FILTERS:
        if status == 'active':
            query = query.filter_by(is_active=True)
        elif status == 'inactive':
            query = query.filter_by(is_active=False)
        # 'all' -> sin filtro de is_active
    else:
        query = query.filter_by(is_active=True)

    query = _apply_filters(query)

    sort = request.args.get('sort')
    query = query.order_by(SORT_OPTIONS.get(sort, Product.id.asc()))

    page = request.args.get('page', default=1, type=int)
    per_page = min(request.args.get('per_page', default=20, type=int), 100)

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'products': [_product_payload(p) for p in paginated.items],
        'total': paginated.total,
        'page': paginated.page,
        'per_page': paginated.per_page,
        'pages': paginated.pages,
    })


@products_bp.route('/filters', methods=['GET'])
def get_filters():
    base = Product.query.filter_by(is_active=True)

    categories = (
        db.session.query(Category.id, Category.name, func.count(Product.id))
        .join(Product, Product.category_id == Category.id)
        .filter(Product.is_active.is_(True))
        .group_by(Category.id, Category.name)
        .all()
    )

    species = (
        db.session.query(Species.id, Species.name, func.count(Product.id))
        .join(Product, Product.species_id == Species.id)
        .filter(Product.is_active.is_(True))
        .group_by(Species.id, Species.name)
        .all()
    )

    brands = (
        db.session.query(Product.brand, func.count(Product.id))
        .filter(Product.is_active.is_(True), Product.brand.isnot(None))
        .group_by(Product.brand)
        .all()
    )

    price_bounds = db.session.query(
        func.min(Product.selling_price), func.max(Product.selling_price)
    ).filter(Product.is_active.is_(True)).first()

    return jsonify({
        'categories': [{'id': c_id, 'name': name, 'count': count} for c_id, name, count in categories],
        'species': [{'id': s_id, 'name': name, 'count': count} for s_id, name, count in species],
        'brands': [{'name': name, 'count': count} for name, count in brands],
        'price_range': {
            'min': float(price_bounds[0]) if price_bounds[0] is not None else 0,
            'max': float(price_bounds[1]) if price_bounds[1] is not None else 0,
        },
    })


@products_bp.route('/suggest-sku', methods=['GET'])
@role_required('admin', 'bodeguero')
def suggest_sku():
    """Sugiere un SKU organizado por categoria (ej. MED-002) para
    precargar el formulario de producto nuevo - el admin lo puede editar
    antes de guardar, no queda bloqueado."""
    category_id = request.args.get('category_id', type=int)
    category = Category.query.get(category_id) if category_id else None
    if not category:
        return jsonify({'message': 'Selecciona una categoría para sugerir un SKU'}), 400

    prefix = _category_sku_prefix(category)
    number = _next_sku_for_prefix(prefix)
    return jsonify({'sku': f'{prefix}-{number:03d}'})


@products_bp.route('/featured', methods=['GET'])
def get_featured_products():
    """Top productos activos por unidades vendidas en ventas reales
    (Pagado/Entregado) - sobre todo el historial, sin ventana de tiempo
    (con el volumen real del negocio, un rango corto suele quedar vacio).
    Publico, sin jwt, mismo criterio que el resto del catalogo. Alimenta
    tanto el carrusel "Productos recomendados" del sitio publico como la
    seccion "Productos Destacados" del dashboard de personal."""
    limit = min(request.args.get('limit', default=5, type=int), 20)

    rows = (
        db.session.query(SalesOrderItem.product_id, func.sum(SalesOrderItem.quantity).label('sold'))
        .join(SalesOrder, SalesOrder.id == SalesOrderItem.order_id)
        .filter(SalesOrder.status.in_(['Pagado', 'Entregado']))
        .group_by(SalesOrderItem.product_id)
        .order_by(func.sum(SalesOrderItem.quantity).desc())
        .all()
    )

    products = []
    for product_id, sold in rows:
        product = Product.query.get(product_id)
        if not product or not product.is_active:
            continue
        payload = _product_payload(product)
        payload['unitsSold'] = float(sold)
        products.append(payload)
        if len(products) >= limit:
            break

    return jsonify({'products': products})


@products_bp.route('/random', methods=['GET'])
def get_random_products():
    """Seleccion aleatoria de productos activos, para la seccion "Podrían
    interesarte" del Home publico (debajo de Productos Destacados) - publico,
    sin jwt, mismo criterio que /featured. Acepta exclude= (ids separados por
    coma, ej. los que ya se muestran en Destacados justo arriba) para no
    repetir el mismo producto dos veces seguidas en la misma pantalla."""
    limit = min(request.args.get('limit', default=8, type=int), 20)

    exclude_raw = request.args.get('exclude', '')
    exclude_ids = {int(x) for x in exclude_raw.split(',') if x.strip().isdigit()}

    query = Product.query.filter_by(is_active=True)
    if exclude_ids:
        query = query.filter(~Product.id.in_(exclude_ids))

    candidates = query.all()
    chosen = random.sample(candidates, min(limit, len(candidates)))
    return jsonify({'products': [_product_payload(p) for p in chosen]})


@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(_product_payload(product))


@products_bp.route('', methods=['POST'])
@role_required('admin', 'bodeguero')
def create_product():
    is_multipart = (request.content_type or '').startswith('multipart/form-data')
    data = request.form if is_multipart else (request.get_json(silent=True) or {})
    files = request.files if is_multipart else {}

    if not data.get('sku'):
        return jsonify({'message': 'El SKU es requerido'}), 400
    if not data.get('name'):
        return jsonify({'message': 'El nombre del producto es requerido'}), 400
    if not data.get('categoryId'):
        return jsonify({'message': 'La categoría es requerida'}), 400

    if Product.query.filter_by(sku=data['sku']).first():
        return jsonify({'message': 'Ya existe un producto con ese SKU'}), 400

    product = Product()
    error = _apply_product_fields(product, data)
    if error:
        return jsonify({'message': error}), 400

    db.session.add(product)
    db.session.flush()  # asigna product.id, necesario para el nombre del archivo de la imagen y el proveedor

    photo = files.get('photo') if files else None
    if photo and photo.filename:
        error = _save_product_photo(product, photo)
        if error:
            db.session.rollback()
            return jsonify({'message': error}), 400

    if 'supplierId' in data:
        error = _sync_supplier(product, data.get('supplierId'))
        if error:
            db.session.rollback()
            return jsonify({'message': error}), 400

    _sync_stock_alert(product)
    log_audit(
        int(get_jwt_identity()), 'Inventario', 'create',
        f'Creó el producto "{product.name}"', entity_type='product', entity_id=product.id,
    )
    db.session.commit()
    return jsonify(_product_payload(product)), 201


@products_bp.route('/<int:product_id>', methods=['PUT'])
@role_required('admin', 'bodeguero')
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    before = snapshot_fields(product)

    is_multipart = (request.content_type or '').startswith('multipart/form-data')
    data = request.form if is_multipart else (request.get_json(silent=True) or {})
    files = request.files if is_multipart else {}

    if 'sku' in data and data['sku'] and data['sku'] != product.sku:
        if Product.query.filter_by(sku=data['sku']).first():
            return jsonify({'message': 'Ya existe un producto con ese SKU'}), 400

    error = _apply_product_fields(product, data)
    if error:
        return jsonify({'message': error}), 400

    photo = files.get('photo') if files else None
    if photo and photo.filename:
        error = _save_product_photo(product, photo)
        if error:
            return jsonify({'message': error}), 400
    elif str(data.get('removePhoto', '')).lower() == 'true':
        _remove_product_photo(product)

    if 'supplierId' in data:
        error = _sync_supplier(product, data.get('supplierId'))
        if error:
            return jsonify({'message': error}), 400

    _sync_stock_alert(product)

    # Activar/Desactivar es un PUT {isActive: ...} solo (decision 19) - se
    # distingue de una edicion normal para que el log de auditoria diga lo
    # que realmente paso, no "Editó" para las dos acciones mas comunes.
    if list(data.keys()) == ['isActive']:
        action = 'activate' if product.is_active else 'deactivate'
        description = f'{"Activó" if product.is_active else "Desactivó"} el producto "{product.name}"'
    else:
        action = 'update'
        description = f'Editó el producto "{product.name}"'
    log_audit(
        int(get_jwt_identity()), 'Inventario', action, description,
        entity_type='product', entity_id=product.id, changes=diff_snapshot(product, before),
    )

    db.session.commit()
    return jsonify(_product_payload(product))


@products_bp.route('/<int:product_id>', methods=['DELETE'])
@role_required('admin', 'bodeguero')
def delete_product(product_id):
    # Borrado permanente real. Solo se permite sobre productos ya inactivos
    # (flujo: primero desactivar via PUT isActive:false, luego eliminar) para
    # que un DELETE directo no se salte esa confirmacion de dos pasos.
    product = Product.query.get_or_404(product_id)
    if product.is_active:
        return jsonify({'message': 'Desactiva el producto antes de eliminarlo permanentemente'}), 400

    # Historial de negocio real - nunca se borra en cascada, se bloquea con
    # un mensaje claro (antes esto no se validaba y el DELETE se caia con
    # un 500 generico por la FK real de purchase_order_details/etc.).
    if PurchaseOrderDetail.query.filter_by(product_id=product.id).first():
        return jsonify({'message': 'No puedes eliminar un producto que está en una orden de compra'}), 400
    if SalesOrderItem.query.filter_by(product_id=product.id).first():
        return jsonify({'message': 'No puedes eliminar un producto que está en un pedido'}), 400
    if ReturnItem.query.filter_by(product_id=product.id).first():
        return jsonify({'message': 'No puedes eliminar un producto que está en una devolución'}), 400

    if product.image_path:
        full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product.image_path)
        if os.path.exists(full_path):
            os.remove(full_path)

    # carrito: si el producto sigue en el carrito de alguien, se limpia solo
    # - no es historial de negocio, es un estado transitorio del cliente.
    CartItem.query.filter_by(product_id=product.id).delete()
    SupplierProduct.query.filter_by(product_id=product.id).delete()
    StockAlert.query.filter_by(product_id=product.id).delete()
    product_name = product.name
    log_audit(
        int(get_jwt_identity()), 'Inventario', 'delete',
        f'Eliminó permanentemente el producto "{product_name}"', entity_type='product', entity_id=product_id,
    )
    db.session.delete(product)
    db.session.commit()
    return '', 204


@products_bp.route('/<int:product_id>/photo', methods=['GET'])
def get_product_photo(product_id):
    product = Product.query.get_or_404(product_id)
    if not product.image_path:
        abort(404)
    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product.image_path)
    if not os.path.exists(full_path):
        abort(404)
    return send_file(full_path, mimetype=product.image_mime or 'image/jpeg')
