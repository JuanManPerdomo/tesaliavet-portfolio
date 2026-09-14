from flask import Blueprint, request, jsonify

from ..models import Species, Breed, Vaccine, Category, Supplier, User, Role, Product
from ..auth.decorators import role_required

catalog_bp = Blueprint('catalog', __name__)


@catalog_bp.route('/categories', methods=['GET'])
def list_categories():
    categories = Category.query.filter_by(is_active=True).order_by(Category.name.asc()).all()
    return jsonify([{'id': c.id, 'name': c.name, 'parentId': c.parent_id} for c in categories])


@catalog_bp.route('/pharmacy-categories', methods=['GET'])
def list_pharmacy_categories():
    # Categorias marcadas por el admin desde /panel/categorias (checkbox
    # "Mostrar en Farmacia Veterinaria") - antes era una lista fija de IDs
    # escrita a mano en AnimalCarePharmacy.vue.
    categories = (
        Category.query.filter_by(is_active=True, is_pharmacy=True)
        .order_by(Category.name.asc())
        .all()
    )
    return jsonify([{'id': c.id, 'name': c.name} for c in categories])


@catalog_bp.route('/suppliers', methods=['GET'])
@role_required('admin')
def list_suppliers():
    suppliers = Supplier.query.filter_by(is_active=True).order_by(Supplier.name.asc()).all()
    return jsonify([{'id': s.id, 'name': s.name} for s in suppliers])


@catalog_bp.route('/species', methods=['GET'])
def list_species():
    query = Species.query
    category_id = request.args.get('category_id', type=int)
    if category_id:
        query = query.filter_by(category_id=category_id)
    species = query.order_by(Species.name.asc()).all()
    return jsonify([{'id': s.id, 'name': s.name, 'categoryId': s.category_id} for s in species])


@catalog_bp.route('/breeds', methods=['GET'])
def list_breeds():
    query = Breed.query
    species_id = request.args.get('species_id', type=int)
    if species_id:
        query = query.filter_by(species_id=species_id)
    breeds = query.order_by(Breed.name.asc()).all()
    return jsonify([{'id': b.id, 'name': b.name, 'speciesId': b.species_id} for b in breeds])


@catalog_bp.route('/vaccines', methods=['GET'])
def list_vaccines():
    vaccines = Vaccine.query.order_by(Vaccine.name.asc()).all()
    return jsonify([{'id': v.id, 'name': v.name} for v in vaccines])


@catalog_bp.route('/stats', methods=['GET'])
def public_stats():
    # Conteos reales para el Home publico (decision 7: nada de numeros
    # inventados como "+5K"/"+800") - solo agregados, sin datos personales.
    active_clients = (
        User.query.join(User.roles)
        .filter(Role.name == 'cliente', User.is_active.is_(True))
        .count()
    )
    active_products = Product.query.filter_by(is_active=True).count()
    return jsonify({'activeClients': active_clients, 'activeProducts': active_products})
