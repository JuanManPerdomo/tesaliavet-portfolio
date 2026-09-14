from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity

from ..extensions import db
from ..models import Vaccine, PetVaccination
from ..auth.decorators import role_required
from ..audit.service import diff_snapshot, log_audit, snapshot_fields

vaccines_bp = Blueprint('vaccines', __name__)


def _vaccine_payload(vaccine):
    return {
        'id': vaccine.id,
        'name': vaccine.name,
        'description': vaccine.description,
    }


@vaccines_bp.route('', methods=['GET'])
@role_required('admin')
def list_vaccines():
    vaccines = Vaccine.query.order_by(Vaccine.name.asc()).all()
    return jsonify([_vaccine_payload(v) for v in vaccines])


@vaccines_bp.route('', methods=['POST'])
@role_required('admin')
def create_vaccine():
    data = request.get_json(silent=True) or {}

    if not data.get('name'):
        return jsonify({'message': 'El nombre de la vacuna es requerido'}), 400
    if Vaccine.query.filter_by(name=data['name']).first():
        return jsonify({'message': 'Ya existe una vacuna con ese nombre'}), 400

    vaccine = Vaccine(name=data['name'], description=data.get('description') or None)
    db.session.add(vaccine)
    db.session.flush()
    log_audit(
        int(get_jwt_identity()), 'Inventario', 'create',
        f'Creó la vacuna "{vaccine.name}" en el catálogo', entity_type='vaccine', entity_id=vaccine.id,
    )
    db.session.commit()
    return jsonify(_vaccine_payload(vaccine)), 201


@vaccines_bp.route('/<int:vaccine_id>', methods=['PUT'])
@role_required('admin')
def update_vaccine(vaccine_id):
    vaccine = Vaccine.query.get_or_404(vaccine_id)
    before = snapshot_fields(vaccine)
    data = request.get_json(silent=True) or {}

    if 'name' in data:
        if not data['name']:
            return jsonify({'message': 'El nombre de la vacuna es requerido'}), 400
        if data['name'] != vaccine.name and Vaccine.query.filter_by(name=data['name']).first():
            return jsonify({'message': 'Ya existe una vacuna con ese nombre'}), 400
        vaccine.name = data['name']

    if 'description' in data:
        vaccine.description = data['description'] or None

    log_audit(
        int(get_jwt_identity()), 'Inventario', 'update',
        f'Editó la vacuna "{vaccine.name}" del catálogo', entity_type='vaccine', entity_id=vaccine.id,
        changes=diff_snapshot(vaccine, before),
    )
    db.session.commit()
    return jsonify(_vaccine_payload(vaccine))


@vaccines_bp.route('/<int:vaccine_id>', methods=['DELETE'])
@role_required('admin')
def delete_vaccine(vaccine_id):
    # Sin is_active en este catalogo (a diferencia de Category/Supplier): es
    # un borrado permanente directo, bloqueado si ya tiene aplicaciones
    # registradas en pet_vaccinations (rompería esa FK).
    vaccine = Vaccine.query.get_or_404(vaccine_id)
    if PetVaccination.query.filter_by(vaccine_id=vaccine.id).first():
        return jsonify({'message': 'No puedes eliminar una vacuna que ya tiene aplicaciones registradas'}), 400

    vaccine_name = vaccine.name
    log_audit(
        int(get_jwt_identity()), 'Inventario', 'delete',
        f'Eliminó la vacuna "{vaccine_name}" del catálogo', entity_type='vaccine', entity_id=vaccine_id,
    )
    db.session.delete(vaccine)
    db.session.commit()
    return '', 204
