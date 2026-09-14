from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity

from ..extensions import db
from ..models import Category, Product
from ..auth.decorators import role_required
from ..audit.service import diff_snapshot, log_audit, snapshot_fields

categories_bp = Blueprint('categories', __name__)

VALID_STATUS_FILTERS = {'active', 'inactive', 'all'}


def _category_payload(category):
    return {
        'id': category.id,
        'name': category.name,
        'description': category.description,
        'parentId': category.parent_id,
        'parentName': category.parent.name if category.parent else None,
        'isActive': category.is_active,
        'isPharmacy': category.is_pharmacy,
    }


def _apply_category_fields(category, data):
    if 'name' in data:
        if not data['name']:
            return 'El nombre de la categoría es requerido'
        category.name = data['name']

    if 'description' in data:
        category.description = data['description'] or None

    if 'parentId' in data:
        parent_id = data['parentId']
        if not parent_id:
            category.parent_id = None
        else:
            try:
                parent_id = int(parent_id)
            except (TypeError, ValueError):
                return 'Categoría padre inválida'
            if category.id and parent_id == category.id:
                return 'Una categoría no puede ser su propia categoría padre'
            parent = Category.query.get(parent_id)
            if not parent:
                return 'Categoría padre no encontrada'
            if parent.parent_id is not None:
                # Jerarquia de solo 2 niveles (ver decision 19/20 en CLAUDE.md):
                # una subcategoria no puede a su vez ser categoria padre.
                return 'No se permiten más de dos niveles de categorías'
            if category.id and Category.query.filter_by(parent_id=category.id).first():
                return 'No puedes convertir en subcategoría una categoría que ya tiene subcategorías propias'
            category.parent_id = parent.id

    if 'isActive' in data:
        value = data['isActive']
        category.is_active = value if isinstance(value, bool) else str(value).lower() in ('true', '1', 'on')

    if 'isPharmacy' in data:
        value = data['isPharmacy']
        category.is_pharmacy = value if isinstance(value, bool) else str(value).lower() in ('true', '1', 'on')

    return None


@categories_bp.route('', methods=['GET'])
@role_required('admin', 'bodeguero')
def list_categories():
    query = Category.query

    status = request.args.get('status')
    if status not in VALID_STATUS_FILTERS:
        status = 'active'
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)
    # 'all' -> sin filtro de is_active

    categories = query.order_by(Category.name.asc()).all()
    return jsonify([_category_payload(c) for c in categories])


@categories_bp.route('', methods=['POST'])
@role_required('admin', 'bodeguero')
def create_category():
    data = request.get_json(silent=True) or {}

    if not data.get('name'):
        return jsonify({'message': 'El nombre de la categoría es requerido'}), 400
    if Category.query.filter_by(name=data['name']).first():
        return jsonify({'message': 'Ya existe una categoría con ese nombre'}), 400

    category = Category()
    error = _apply_category_fields(category, data)
    if error:
        return jsonify({'message': error}), 400

    db.session.add(category)
    db.session.flush()
    log_audit(
        int(get_jwt_identity()), 'Inventario', 'create',
        f'Creó la categoría "{category.name}"', entity_type='category', entity_id=category.id,
    )
    db.session.commit()
    return jsonify(_category_payload(category)), 201


@categories_bp.route('/<int:category_id>', methods=['PUT'])
@role_required('admin', 'bodeguero')
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    before = snapshot_fields(category)
    data = request.get_json(silent=True) or {}

    if 'name' in data and data['name'] and data['name'] != category.name:
        if Category.query.filter_by(name=data['name']).first():
            return jsonify({'message': 'Ya existe una categoría con ese nombre'}), 400

    error = _apply_category_fields(category, data)
    if error:
        return jsonify({'message': error}), 400

    if list(data.keys()) == ['isActive']:
        action = 'activate' if category.is_active else 'deactivate'
        description = f'{"Activó" if category.is_active else "Desactivó"} la categoría "{category.name}"'
    else:
        action = 'update'
        description = f'Editó la categoría "{category.name}"'
    log_audit(
        int(get_jwt_identity()), 'Inventario', action, description,
        entity_type='category', entity_id=category.id, changes=diff_snapshot(category, before),
    )

    db.session.commit()
    return jsonify(_category_payload(category))


@categories_bp.route('/<int:category_id>', methods=['DELETE'])
@role_required('admin', 'bodeguero')
def delete_category(category_id):
    # Mismo patron de dos pasos que products/suppliers: borrado permanente
    # real, solo sobre categorias ya inactivas. Ademas, una categoria con
    # productos o subcategorias no se puede borrar (rompería la FK de
    # products.category_id / categories.parent_id).
    category = Category.query.get_or_404(category_id)
    if category.is_active:
        return jsonify({'message': 'Desactiva la categoría antes de eliminarla permanentemente'}), 400
    if Product.query.filter_by(category_id=category.id).first():
        return jsonify({'message': 'No puedes eliminar una categoría con productos asignados'}), 400
    if Category.query.filter_by(parent_id=category.id).first():
        return jsonify({'message': 'No puedes eliminar una categoría que tiene subcategorías'}), 400

    category_name = category.name
    log_audit(
        int(get_jwt_identity()), 'Inventario', 'delete',
        f'Eliminó permanentemente la categoría "{category_name}"', entity_type='category', entity_id=category_id,
    )
    db.session.delete(category)
    db.session.commit()
    return '', 204
