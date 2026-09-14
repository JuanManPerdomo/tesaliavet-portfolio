from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity

from ..extensions import db
from ..models import Species, Category, Pet, Breed, Product
from ..auth.decorators import role_required
from ..audit.service import diff_snapshot, log_audit, snapshot_fields

species_bp = Blueprint('species', __name__)


def _species_payload(species):
    return {
        'id': species.id,
        'name': species.name,
        'categoryId': species.category_id,
        'categoryName': species.category.name if species.category else None,
    }


@species_bp.route('', methods=['GET'])
@role_required('admin')
def list_species():
    species = Species.query.order_by(Species.name.asc()).all()
    return jsonify([_species_payload(s) for s in species])


@species_bp.route('', methods=['POST'])
@role_required('admin')
def create_species():
    data = request.get_json(silent=True) or {}

    if not data.get('name'):
        return jsonify({'message': 'El nombre de la especie es requerido'}), 400
    if Species.query.filter_by(name=data['name']).first():
        return jsonify({'message': 'Ya existe una especie con ese nombre'}), 400

    category_id = data.get('categoryId')
    if not category_id:
        return jsonify({'message': 'La categoría (Mascotas o Ganadería) es requerida'}), 400
    category = Category.query.get(category_id)
    # Especie siempre cuelga de un pilar de nivel 1 (Mascotas/Ganaderia,
    # decision 20 en CLAUDE.md) - nunca de una subcategoria.
    if not category or category.parent_id is not None:
        return jsonify({'message': 'Categoría inválida'}), 400

    species = Species(name=data['name'], category_id=category.id)
    db.session.add(species)
    db.session.flush()
    log_audit(
        int(get_jwt_identity()), 'Inventario', 'create',
        f'Creó la especie "{species.name}" en el catálogo', entity_type='species', entity_id=species.id,
    )
    db.session.commit()
    return jsonify(_species_payload(species)), 201


@species_bp.route('/<int:species_id>', methods=['PUT'])
@role_required('admin')
def update_species(species_id):
    species = Species.query.get_or_404(species_id)
    before = snapshot_fields(species)
    data = request.get_json(silent=True) or {}

    if 'name' in data:
        if not data['name']:
            return jsonify({'message': 'El nombre de la especie es requerido'}), 400
        if data['name'] != species.name and Species.query.filter_by(name=data['name']).first():
            return jsonify({'message': 'Ya existe una especie con ese nombre'}), 400
        species.name = data['name']

    if 'categoryId' in data:
        category = Category.query.get(data['categoryId'])
        if not category or category.parent_id is not None:
            return jsonify({'message': 'Categoría inválida'}), 400
        species.category_id = category.id

    log_audit(
        int(get_jwt_identity()), 'Inventario', 'update',
        f'Editó la especie "{species.name}" del catálogo', entity_type='species', entity_id=species.id,
        changes=diff_snapshot(species, before),
    )
    db.session.commit()
    return jsonify(_species_payload(species))


@species_bp.route('/<int:species_id>', methods=['DELETE'])
@role_required('admin')
def delete_species(species_id):
    # Sin is_active en este catalogo (igual que Vacunas) - borrado permanente
    # directo, bloqueado si alguna mascota, raza o producto ya la usa (las 3
    # tienen FK real contra species.id).
    species = Species.query.get_or_404(species_id)
    if Pet.query.filter_by(species_id=species.id).first():
        return jsonify({'message': 'No puedes eliminar una especie que ya tiene mascotas registradas'}), 400
    if Breed.query.filter_by(species_id=species.id).first():
        return jsonify({'message': 'No puedes eliminar una especie que tiene razas asociadas'}), 400
    if Product.query.filter_by(species_id=species.id).first():
        return jsonify({'message': 'No puedes eliminar una especie que tiene productos asociados'}), 400

    species_name = species.name
    log_audit(
        int(get_jwt_identity()), 'Inventario', 'delete',
        f'Eliminó la especie "{species_name}" del catálogo', entity_type='species', entity_id=species_id,
    )
    db.session.delete(species)
    db.session.commit()
    return '', 204
