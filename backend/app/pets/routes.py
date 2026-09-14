import os
from datetime import date, datetime

from flask import Blueprint, request, jsonify, send_file, abort, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import text, or_

from ..extensions import db
from ..models import Pet, PetVaccination, MedicalRecord, Vaccine, User, Appointment
from ..auth.decorators import role_required
from ..audit.service import diff_snapshot, log_audit, snapshot_fields

pets_bp = Blueprint('pets', __name__)

ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png'}
EXTENSION_BY_MIME = {'image/jpeg': 'jpg', 'image/png': 'png'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
VALID_GENDERS = {'Macho', 'Hembra', 'Desconocido'}

ALLOWED_ATTACHMENT_TYPES = {'application/pdf', 'image/jpeg', 'image/png'}
ATTACHMENT_EXTENSION_BY_MIME = {'application/pdf': 'pdf', 'image/jpeg': 'jpg', 'image/png': 'png'}
MAX_ATTACHMENT_SIZE = 5 * 1024 * 1024  # 5MB


def _is_staff(user):
    return any(r.name in ('admin', 'veterinario') for r in user.roles)


def _current_user_id():
    return int(get_jwt_identity())


def _get_owned_pet_or_404(pet_id):
    pet = Pet.query.filter_by(id=pet_id, owner_id=_current_user_id(), is_active=True).first()
    if not pet:
        abort(404, description='Mascota no encontrada')
    return pet


def _get_pet_or_404(pet_id):
    """Igual que _get_owned_pet_or_404 pero sin filtrar por owner_id, para uso
    del personal (admin/veterinario) que atiende mascotas de cualquier cliente."""
    pet = Pet.query.filter_by(id=pet_id, is_active=True).first()
    if not pet:
        abort(404, description='Mascota no encontrada')
    return pet


def _calc_age(birth_date):
    if not birth_date:
        return None
    today = date.today()
    years = today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )
    return max(years, 0)


def _latest_vaccinations_by_vaccine(pet):
    # Una mascota puede tener varias dosis historicas de la misma vacuna
    # (ej. un refuerzo que reemplaza uno vencido); el estado y el recordatorio
    # deben mirar solo la aplicacion mas reciente de cada vacuna, no todo el
    # historial - si no, una dosis vieja ya renovada sigue marcando
    # "pendiente" para siempre.
    vaccinations = PetVaccination.query.filter_by(pet_id=pet.id).all()
    latest = {}
    for v in vaccinations:
        current = latest.get(v.vaccine_id)
        if not current or v.application_date > current.application_date:
            latest[v.vaccine_id] = v
    return list(latest.values())


def _vaccine_status(pet):
    latest = _latest_vaccinations_by_vaccine(pet)
    if not latest:
        return 'sin_registro'
    today = date.today()
    if any(v.next_due_date and v.next_due_date < today for v in latest):
        return 'pendiente'
    return 'al_dia'


def _next_vaccine_reminder(pet):
    candidates = [v for v in _latest_vaccinations_by_vaccine(pet) if v.next_due_date]
    if not candidates:
        return None
    upcoming = min(candidates, key=lambda v: v.next_due_date)
    return {
        'id': upcoming.id,
        'vaccineName': upcoming.vaccine.name if upcoming.vaccine else None,
        'nextDueDate': upcoming.next_due_date.isoformat(),
        'isOverdue': upcoming.next_due_date < date.today(),
    }


def _pet_summary_payload(pet):
    return {
        'id': pet.id,
        'name': pet.name,
        'species': {'id': pet.species.id, 'name': pet.species.name} if pet.species else None,
        'breed': {'id': pet.breed.id, 'name': pet.breed.name} if pet.breed else None,
        'gender': pet.gender,
        'birthDate': pet.birth_date.isoformat() if pet.birth_date else None,
        'age': _calc_age(pet.birth_date),
        'weight': float(pet.weight) if pet.weight is not None else None,
        'color': pet.color,
        'photoUrl': f'/pets/{pet.id}/photo' if pet.image_path else None,
        'vaccineStatus': _vaccine_status(pet),
        'nextVaccine': _next_vaccine_reminder(pet),
    }


def _pet_detail_payload(pet):
    payload = _pet_summary_payload(pet)
    payload['notes'] = pet.notes
    return payload


def _owner_payload(pet):
    owner = pet.owner
    if not owner:
        return None
    return {
        'id': owner.id,
        'name': f'{owner.first_name} {owner.last_name}',
        'phone': owner.phone,
        'email': owner.email,
    }


def _medical_record_payload(r):
    return {
        'id': r.id,
        'visitDate': r.visit_date.isoformat(),
        'veterinarianName': (
            f'{r.veterinarian.first_name} {r.veterinarian.last_name}' if r.veterinarian else None
        ),
        'symptoms': r.symptoms,
        'diagnosis': r.diagnosis,
        'treatment': r.treatment,
        'observations': r.observations,
        'attachmentUrl': f'/pets/medical-records/{r.id}/attachment' if r.attachment_path else None,
        'attachmentName': os.path.basename(r.attachment_path) if r.attachment_path else None,
    }


def _vaccination_payload(v):
    return {
        'id': v.id,
        'vaccineName': v.vaccine.name if v.vaccine else None,
        'applicationDate': v.application_date.isoformat(),
        'nextDueDate': v.next_due_date.isoformat() if v.next_due_date else None,
        'veterinarianName': (
            f'{v.veterinarian.first_name} {v.veterinarian.last_name}' if v.veterinarian else None
        ),
        'notes': v.notes,
    }


def _pets_upload_dir():
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'pets')
    os.makedirs(path, exist_ok=True)
    return path


def _save_pet_photo(pet, photo_file):
    if photo_file.mimetype not in ALLOWED_IMAGE_TYPES:
        return 'La foto debe ser JPG o PNG'
    content = photo_file.read()
    if len(content) > MAX_IMAGE_SIZE:
        return 'La foto no debe superar 5MB'

    upload_dir = _pets_upload_dir()
    for existing in os.listdir(upload_dir):
        if existing.startswith(f'pet_{pet.id}.'):
            os.remove(os.path.join(upload_dir, existing))

    filename = f'pet_{pet.id}.{EXTENSION_BY_MIME[photo_file.mimetype]}'
    with open(os.path.join(upload_dir, filename), 'wb') as f:
        f.write(content)

    pet.image_path = f'pets/{filename}'
    pet.image_mime = photo_file.mimetype
    return None


def _remove_pet_photo(pet):
    """Deja la mascota sin foto (borra el archivo real de disco) - pedido
    explícito de Juan Manuel: poder quitar cualquier imagen, no solo
    reemplazarla."""
    if not pet.image_path:
        return
    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], pet.image_path)
    if os.path.exists(full_path):
        os.remove(full_path)
    pet.image_path = None
    pet.image_mime = None


def _medical_records_upload_dir():
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'medical_records')
    os.makedirs(path, exist_ok=True)
    return path


def _save_medical_record_attachment(record, attachment_file):
    if attachment_file.mimetype not in ALLOWED_ATTACHMENT_TYPES:
        return 'El adjunto debe ser PDF, JPG o PNG'
    content = attachment_file.read()
    if len(content) > MAX_ATTACHMENT_SIZE:
        return 'El adjunto no debe superar 5MB'

    filename = f'record_{record.id}.{ATTACHMENT_EXTENSION_BY_MIME[attachment_file.mimetype]}'
    with open(os.path.join(_medical_records_upload_dir(), filename), 'wb') as f:
        f.write(content)

    record.attachment_path = f'medical_records/{filename}'
    record.attachment_mime = attachment_file.mimetype
    return None


def _apply_pet_fields(pet, data):
    if 'name' in data:
        if not data['name']:
            return 'El nombre de la mascota es requerido'
        pet.name = data['name']

    if 'speciesId' in data:
        if not data['speciesId']:
            return 'La especie es requerida'
        try:
            pet.species_id = int(data['speciesId'])
        except ValueError:
            return 'Especie inválida'

    if 'breedId' in data:
        if data['breedId']:
            try:
                pet.breed_id = int(data['breedId'])
            except ValueError:
                return 'Raza inválida'
        else:
            pet.breed_id = None

    if 'gender' in data and data['gender']:
        if data['gender'] not in VALID_GENDERS:
            return 'Género inválido'
        pet.gender = data['gender']

    if 'birthDate' in data:
        if data['birthDate']:
            try:
                pet.birth_date = date.fromisoformat(data['birthDate'])
            except ValueError:
                return 'La fecha de nacimiento no es válida'
        else:
            pet.birth_date = None

    if 'weight' in data:
        if data['weight']:
            try:
                pet.weight = float(str(data['weight']).replace(',', '.'))
            except ValueError:
                return 'El peso debe ser un número válido'
        else:
            pet.weight = None

    if 'color' in data:
        pet.color = data['color'] or None

    if 'notes' in data:
        pet.notes = data['notes'] or None

    return None


@pets_bp.route('', methods=['GET'])
@jwt_required()
def list_pets():
    pets = (
        Pet.query.filter_by(owner_id=_current_user_id(), is_active=True)
        .order_by(Pet.created_at.asc())
        .all()
    )
    return jsonify([_pet_summary_payload(p) for p in pets])


@pets_bp.route('', methods=['POST'])
@jwt_required()
def create_pet():
    is_multipart = (request.content_type or '').startswith('multipart/form-data')
    data = request.form if is_multipart else (request.get_json(silent=True) or {})
    files = request.files if is_multipart else {}

    if not data.get('name'):
        return jsonify({'message': 'El nombre de la mascota es requerido'}), 400
    if not data.get('speciesId'):
        return jsonify({'message': 'La especie es requerida'}), 400

    pet = Pet(owner_id=_current_user_id())
    error = _apply_pet_fields(pet, data)
    if error:
        return jsonify({'message': error}), 400

    db.session.add(pet)
    db.session.flush()  # asigna pet.id, necesario para el nombre del archivo de la foto

    photo = files.get('photo') if files else None
    if photo and photo.filename:
        error = _save_pet_photo(pet, photo)
        if error:
            db.session.rollback()
            return jsonify({'message': error}), 400

    log_audit(
        _current_user_id(), 'Mascotas', 'create', f'Registró la mascota "{pet.name}"',
        entity_type='pet', entity_id=pet.id,
    )
    db.session.commit()

    return jsonify(_pet_detail_payload(pet)), 201


@pets_bp.route('/<int:pet_id>', methods=['GET'])
@jwt_required()
def get_pet(pet_id):
    pet = _get_owned_pet_or_404(pet_id)
    return jsonify(_pet_detail_payload(pet))


@pets_bp.route('/<int:pet_id>', methods=['PUT'])
@jwt_required()
def update_pet(pet_id):
    pet = _get_owned_pet_or_404(pet_id)
    before = snapshot_fields(pet)

    is_multipart = (request.content_type or '').startswith('multipart/form-data')
    data = request.form if is_multipart else (request.get_json(silent=True) or {})
    files = request.files if is_multipart else {}

    error = _apply_pet_fields(pet, data)
    if error:
        return jsonify({'message': error}), 400

    photo = files.get('photo') if files else None
    if photo and photo.filename:
        error = _save_pet_photo(pet, photo)
        if error:
            return jsonify({'message': error}), 400
    elif str(data.get('removePhoto', '')).lower() == 'true':
        _remove_pet_photo(pet)

    log_audit(
        _current_user_id(), 'Mascotas', 'update', f'Editó la mascota "{pet.name}"',
        entity_type='pet', entity_id=pet.id, changes=diff_snapshot(pet, before),
    )
    db.session.commit()
    return jsonify(_pet_detail_payload(pet))


@pets_bp.route('/<int:pet_id>', methods=['DELETE'])
@jwt_required()
def delete_pet(pet_id):
    pet = _get_owned_pet_or_404(pet_id)

    if pet.image_path:
        full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], pet.image_path)
        if os.path.exists(full_path):
            os.remove(full_path)

    MedicalRecord.query.filter_by(pet_id=pet.id).delete()
    PetVaccination.query.filter_by(pet_id=pet.id).delete()
    db.session.execute(text('DELETE FROM appointments WHERE pet_id = :pet_id'), {'pet_id': pet.id})

    pet_name = pet.name
    pet_id_for_log = pet.id
    log_audit(
        _current_user_id(), 'Mascotas', 'delete', f'Eliminó la mascota "{pet_name}"',
        entity_type='pet', entity_id=pet_id_for_log,
    )
    db.session.delete(pet)
    db.session.commit()
    return '', 204


@pets_bp.route('/<int:pet_id>/photo', methods=['GET'])
@jwt_required()
def get_pet_photo(pet_id):
    # Bug real corregido: antes solo el dueño podia ver la foto, asi que se
    # veia rota (icono generico) en las citas del panel de personal
    # (StaffAppointmentsPage/StaffAppointmentDetailPage ya la mostraban, solo
    # que el backend la bloqueaba con 404).
    user = User.query.get(_current_user_id())
    pet = _get_pet_or_404(pet_id) if _is_staff(user) else _get_owned_pet_or_404(pet_id)
    if not pet.image_path:
        abort(404)
    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], pet.image_path)
    if not os.path.exists(full_path):
        abort(404)
    return send_file(full_path, mimetype=pet.image_mime or 'image/jpeg')


@pets_bp.route('/staff', methods=['GET'])
@role_required('admin', 'veterinario')
def list_staff_pets():
    query = Pet.query.filter_by(is_active=True).join(User, Pet.owner_id == User.id)

    search = request.args.get('search')
    if search:
        like = f'%{search}%'
        query = query.filter(or_(
            Pet.name.ilike(like),
            User.first_name.ilike(like),
            User.last_name.ilike(like),
        ))

    pets = query.order_by(Pet.name.asc()).all()
    return jsonify([{
        **_pet_summary_payload(p),
        'owner': _owner_payload(p),
    } for p in pets])


def _vet_patient_ids(user):
    """IDs de mascota con al menos un registro medico, vacuna o cita
    atribuida a este veterinario - "sus pacientes" para el dashboard
    (panel del veterinario, pedido por Juan Manuel 2026-09-02)."""
    mr_ids = {r.pet_id for r in MedicalRecord.query.filter_by(veterinarian_id=user.id).all()}
    vac_ids = {v.pet_id for v in PetVaccination.query.filter_by(veterinarian_id=user.id).all()}
    appt_ids = {a.pet_id for a in Appointment.query.filter_by(veterinarian_id=user.id).all()}
    return mr_ids | vac_ids | appt_ids


@pets_bp.route('/staff/recent-patients', methods=['GET'])
@role_required('admin', 'veterinario')
def recent_patients():
    """Mascotas con actividad clinica reciente (registro medico o vacuna
    aplicada) - por este veterinario, o de todo el personal si es admin.
    Pensado para el dashboard del veterinario, que hoy solo tiene Inicio +
    Citas asignadas (decision 18) y quedaba muy vacio."""
    user = User.query.get(_current_user_id())
    is_admin = any(r.name == 'admin' for r in user.roles)
    limit = min(request.args.get('limit', default=6, type=int), 20)

    mr_query = MedicalRecord.query.filter_by(is_active=True)
    vac_query = PetVaccination.query
    if not is_admin:
        mr_query = mr_query.filter_by(veterinarian_id=user.id)
        vac_query = vac_query.filter_by(veterinarian_id=user.id)

    last_activity = {}
    for r in mr_query.all():
        d = r.visit_date.date() if r.visit_date else None
        if d and (r.pet_id not in last_activity or d > last_activity[r.pet_id]):
            last_activity[r.pet_id] = d
    for v in vac_query.all():
        if v.application_date and (
            v.pet_id not in last_activity or v.application_date > last_activity[v.pet_id]
        ):
            last_activity[v.pet_id] = v.application_date

    top_pet_ids = sorted(last_activity, key=lambda pid: last_activity[pid], reverse=True)[:limit]
    pets_by_id = {p.id: p for p in Pet.query.filter(Pet.id.in_(top_pet_ids), Pet.is_active.is_(True)).all()}

    items = []
    for pid in top_pet_ids:
        pet = pets_by_id.get(pid)
        if not pet:
            continue
        items.append({
            **_pet_summary_payload(pet),
            'owner': _owner_payload(pet),
            'lastVisitDate': last_activity[pid].isoformat(),
        })
    return jsonify(items)


@pets_bp.route('/staff/upcoming-vaccines', methods=['GET'])
@role_required('admin', 'veterinario')
def upcoming_vaccines():
    """Vacunas proximas a vencer o ya vencidas de los pacientes de este
    veterinario (o de todas las mascotas si es admin) - reusa el mismo
    calculo de _next_vaccine_reminder que ya usa el perfil de mascota,
    solo que aca se listan y ordenan por urgencia."""
    user = User.query.get(_current_user_id())
    is_admin = any(r.name == 'admin' for r in user.roles)
    limit = min(request.args.get('limit', default=6, type=int), 20)

    query = Pet.query.filter_by(is_active=True)
    if not is_admin:
        pet_ids = _vet_patient_ids(user)
        if not pet_ids:
            return jsonify([])
        query = query.filter(Pet.id.in_(pet_ids))

    with_reminder = []
    for pet in query.all():
        payload = _pet_summary_payload(pet)
        if payload['nextVaccine']:
            payload['owner'] = _owner_payload(pet)
            with_reminder.append(payload)

    with_reminder.sort(key=lambda p: p['nextVaccine']['nextDueDate'])
    return jsonify(with_reminder[:limit])


@pets_bp.route('/staff/<int:pet_id>', methods=['GET'])
@role_required('admin', 'veterinario')
def get_staff_pet(pet_id):
    pet = _get_pet_or_404(pet_id)
    payload = _pet_detail_payload(pet)
    payload['owner'] = _owner_payload(pet)
    return jsonify(payload)


@pets_bp.route('/staff/<int:pet_id>', methods=['PUT'])
@role_required('admin')
def update_staff_pet(pet_id):
    pet = _get_pet_or_404(pet_id)
    before = snapshot_fields(pet)

    is_multipart = (request.content_type or '').startswith('multipart/form-data')
    data = request.form if is_multipart else (request.get_json(silent=True) or {})
    files = request.files if is_multipart else {}

    error = _apply_pet_fields(pet, data)
    if error:
        return jsonify({'message': error}), 400

    photo = files.get('photo') if files else None
    if photo and photo.filename:
        error = _save_pet_photo(pet, photo)
        if error:
            return jsonify({'message': error}), 400
    elif str(data.get('removePhoto', '')).lower() == 'true':
        _remove_pet_photo(pet)

    # Gap real encontrado (2026-09-07): este endpoint nunca dejaba registro
    # de auditoria, a diferencia de update_pet (lado cliente) - una edicion
    # de perfil desde el panel quedaba invisible en Auditoria.
    log_audit(
        _current_user_id(), 'Mascotas', 'update', f'Editó la mascota "{pet.name}" desde el panel',
        entity_type='pet', entity_id=pet.id, changes=diff_snapshot(pet, before),
    )
    db.session.commit()
    payload = _pet_detail_payload(pet)
    payload['owner'] = _owner_payload(pet)
    return jsonify(payload)


@pets_bp.route('/staff/<int:pet_id>', methods=['DELETE'])
@role_required('admin')
def delete_staff_pet(pet_id):
    """Eliminar mascota desde el panel - antes exclusiva del cliente dueño
    (decisión 25 la dejó fuera a propósito, "te dejo esta decisión en tus
    manos"). Pedido explícito de Juan Manuel para cerrarla: mismo admin-only
    y misma cascada real que ya usa delete_pet (lado cliente) - borra foto en
    disco, historial médico, vacunas y citas de la mascota antes de la
    mascota misma, sin duplicar esa lógica en un helper nuevo."""
    pet = _get_pet_or_404(pet_id)

    if pet.image_path:
        full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], pet.image_path)
        if os.path.exists(full_path):
            os.remove(full_path)

    MedicalRecord.query.filter_by(pet_id=pet.id).delete()
    PetVaccination.query.filter_by(pet_id=pet.id).delete()
    db.session.execute(text('DELETE FROM appointments WHERE pet_id = :pet_id'), {'pet_id': pet.id})

    pet_name = pet.name
    owner_name = f'{pet.owner.first_name} {pet.owner.last_name}' if pet.owner else 'dueño desconocido'
    pet_id_for_log = pet.id
    log_audit(
        _current_user_id(), 'Mascotas', 'delete',
        f'Eliminó la mascota "{pet_name}" (de {owner_name}) desde el panel',
        entity_type='pet', entity_id=pet_id_for_log,
    )
    db.session.delete(pet)
    db.session.commit()
    return '', 204


@pets_bp.route('/staff/<int:pet_id>/medical-records', methods=['GET'])
@role_required('admin', 'veterinario')
def list_staff_medical_records(pet_id):
    pet = _get_pet_or_404(pet_id)
    records = (
        MedicalRecord.query.filter_by(pet_id=pet.id, is_active=True)
        .order_by(MedicalRecord.visit_date.desc())
        .all()
    )
    return jsonify([_medical_record_payload(r) for r in records])


@pets_bp.route('/staff/<int:pet_id>/vaccinations', methods=['GET'])
@role_required('admin', 'veterinario')
def list_staff_vaccinations(pet_id):
    pet = _get_pet_or_404(pet_id)
    vaccinations = (
        PetVaccination.query.filter_by(pet_id=pet.id)
        .order_by(PetVaccination.application_date.desc())
        .all()
    )
    return jsonify([_vaccination_payload(v) for v in vaccinations])


@pets_bp.route('/<int:pet_id>/medical-records', methods=['GET'])
@jwt_required()
def list_medical_records(pet_id):
    pet = _get_owned_pet_or_404(pet_id)
    records = (
        MedicalRecord.query.filter_by(pet_id=pet.id, is_active=True)
        .order_by(MedicalRecord.visit_date.desc())
        .all()
    )
    return jsonify([_medical_record_payload(r) for r in records])


@pets_bp.route('/<int:pet_id>/vaccinations', methods=['GET'])
@jwt_required()
def list_vaccinations(pet_id):
    pet = _get_owned_pet_or_404(pet_id)
    vaccinations = (
        PetVaccination.query.filter_by(pet_id=pet.id)
        .order_by(PetVaccination.application_date.desc())
        .all()
    )
    return jsonify([_vaccination_payload(v) for v in vaccinations])


@pets_bp.route('/<int:pet_id>/medical-records', methods=['POST'])
@role_required('admin', 'veterinario')
def create_medical_record(pet_id):
    pet = _get_pet_or_404(pet_id)

    is_multipart = (request.content_type or '').startswith('multipart/form-data')
    data = request.form if is_multipart else (request.get_json(silent=True) or {})
    files = request.files if is_multipart else {}

    if not data.get('diagnosis'):
        return jsonify({'message': 'El diagnóstico es requerido'}), 400

    visit_date = datetime.now()
    if data.get('visitDate'):
        try:
            visit_date = datetime.fromisoformat(data['visitDate'])
        except ValueError:
            return jsonify({'message': 'La fecha de visita no es válida'}), 400

    record = MedicalRecord(
        pet_id=pet.id,
        veterinarian_id=_current_user_id(),
        visit_date=visit_date,
        symptoms=data.get('symptoms') or None,
        diagnosis=data['diagnosis'],
        treatment=data.get('treatment') or None,
        observations=data.get('observations') or None,
    )
    db.session.add(record)
    db.session.flush()  # asigna record.id, necesario para el nombre del archivo del adjunto

    attachment = files.get('attachment') if files else None
    if attachment and attachment.filename:
        error = _save_medical_record_attachment(record, attachment)
        if error:
            db.session.rollback()
            return jsonify({'message': error}), 400

    log_audit(
        _current_user_id(), 'Mascotas', 'add_medical_record',
        f'Agregó un registro médico a "{pet.name}"', entity_type='medical_record', entity_id=record.id,
    )
    db.session.commit()
    return jsonify(_medical_record_payload(record)), 201


@pets_bp.route('/medical-records/<int:record_id>/attachment', methods=['GET'])
@jwt_required()
def get_medical_record_attachment(record_id):
    record = MedicalRecord.query.get_or_404(record_id)
    user = User.query.get(_current_user_id())
    pet = Pet.query.get(record.pet_id)
    is_owner = pet is not None and pet.owner_id == user.id
    if not (_is_staff(user) or is_owner):
        abort(404)
    if not record.attachment_path:
        abort(404)
    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], record.attachment_path)
    if not os.path.exists(full_path):
        abort(404)
    return send_file(full_path, mimetype=record.attachment_mime or 'application/pdf')


@pets_bp.route('/<int:pet_id>/vaccinations', methods=['POST'])
@role_required('admin', 'veterinario')
def create_vaccination(pet_id):
    pet = _get_pet_or_404(pet_id)
    data = request.get_json(silent=True) or {}

    if not data.get('vaccineId'):
        return jsonify({'message': 'La vacuna es requerida'}), 400
    if not data.get('applicationDate'):
        return jsonify({'message': 'La fecha de aplicación es requerida'}), 400

    vaccine = Vaccine.query.get(data['vaccineId'])
    if not vaccine:
        return jsonify({'message': 'Vacuna inválida'}), 400

    try:
        application_date = date.fromisoformat(data['applicationDate'])
        next_due_date = date.fromisoformat(data['nextDueDate']) if data.get('nextDueDate') else None
        expires_at = date.fromisoformat(data['expiresAt']) if data.get('expiresAt') else None
    except ValueError:
        return jsonify({'message': 'Alguna fecha no es válida'}), 400

    vaccination = PetVaccination(
        pet_id=pet.id,
        vaccine_id=vaccine.id,
        veterinarian_id=_current_user_id(),
        application_date=application_date,
        next_due_date=next_due_date,
        batch_number=data.get('batchNumber') or None,
        expires_at=expires_at,
        notes=data.get('notes') or None,
    )
    db.session.add(vaccination)
    db.session.flush()

    log_audit(
        _current_user_id(), 'Mascotas', 'add_vaccination',
        f'Aplicó la vacuna "{vaccine.name}" a "{pet.name}"', entity_type='vaccination', entity_id=vaccination.id,
    )
    db.session.commit()

    return jsonify({
        'id': vaccination.id,
        'vaccineName': vaccine.name,
        'applicationDate': vaccination.application_date.isoformat(),
    }), 201
