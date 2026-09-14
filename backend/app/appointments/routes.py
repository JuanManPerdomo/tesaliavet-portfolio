import calendar as calendar_module
from datetime import date, datetime, time, timedelta

from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models import Appointment, Pet, User
from ..auth.decorators import role_required
from ..audit.service import diff_snapshot, log_audit, snapshot_fields
from .mailer import send_appointment_cancelled, send_appointment_confirmed, send_appointment_created

appointments_bp = Blueprint('appointments', __name__)

STAFF_EDITABLE_STATUSES = {'Confirmada', 'Completada'}

# Horario de atencion: {weekday (0=lunes .. 6=domingo): (hora_apertura, hora_cierre)}
BUSINESS_HOURS = {
    0: (7, 19),
    1: (7, 19),
    2: (7, 19),
    3: (7, 19),
    4: (7, 19),
    5: (7, 19),
    6: (8, 19),
}
LUNCH_BREAK_HOURS = {12, 13}  # 12:00pm y 1:00pm, hora de almuerzo, sin citas
SLOT_CAPACITY = 1  # citas simultaneas permitidas por horario
CANCEL_CUTOFF_HOURS = 2  # no se puede cancelar a menos de 2 horas de la cita


def _current_user_id():
    return int(get_jwt_identity())


def _get_owned_appointment_or_404(appointment_id):
    appointment = Appointment.query.filter_by(
        id=appointment_id, owner_id=_current_user_id()
    ).first()
    if not appointment:
        abort(404, description='Cita no encontrada')
    return appointment


def _slot_hours_for(target_date):
    hours = BUSINESS_HOURS.get(target_date.weekday())
    if not hours:
        return []
    start_hour, end_hour = hours
    return [h for h in range(start_hour, end_hour) if h not in LUNCH_BREAK_HOURS]


def _appointment_payload(appointment):
    pet = appointment.pet
    return {
        'id': appointment.id,
        'pet': {
            'id': pet.id,
            'name': pet.name,
            'photoUrl': f'/pets/{pet.id}/photo' if pet.image_path else None,
        } if pet else None,
        'appointmentDatetime': appointment.appointment_datetime.isoformat(),
        'reason': appointment.reason,
        'status': appointment.status,
        'cancelReason': appointment.cancel_reason,
        'notes': appointment.notes,
        'veterinarianId': appointment.veterinarian_id,
        'veterinarianName': (
            f'{appointment.veterinarian.first_name} {appointment.veterinarian.last_name}'
            if appointment.veterinarian else None
        ),
        'ownerName': (
            f'{appointment.owner.first_name} {appointment.owner.last_name}' if appointment.owner else None
        ),
    }


@appointments_bp.route('', methods=['GET'])
@jwt_required()
def list_appointments():
    appointments = (
        Appointment.query.filter_by(owner_id=_current_user_id())
        .order_by(Appointment.appointment_datetime.desc())
        .all()
    )
    return jsonify([_appointment_payload(a) for a in appointments])


@appointments_bp.route('/availability', methods=['GET'])
@jwt_required()
def get_availability():
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({'message': 'La fecha es requerida'}), 400
    try:
        target_date = date.fromisoformat(date_str)
    except ValueError:
        return jsonify({'message': 'Fecha inválida'}), 400

    slot_hours = _slot_hours_for(target_date)

    day_start = datetime.combine(target_date, time.min)
    day_end = datetime.combine(target_date, time.max)
    booked_rows = (
        db.session.query(Appointment.appointment_datetime)
        .filter(
            Appointment.appointment_datetime >= day_start,
            Appointment.appointment_datetime <= day_end,
            Appointment.status != 'Cancelada',
        )
        .all()
    )
    booked_hours = {dt.hour for (dt,) in booked_rows}

    now = datetime.now()
    slots = []
    for hour in slot_hours:
        slot_dt = datetime.combine(target_date, time(hour=hour))
        available = slot_dt > now and hour not in booked_hours
        slots.append({'time': f'{hour:02d}:00', 'available': available})

    return jsonify({'date': date_str, 'slots': slots})


@appointments_bp.route('/availability-summary', methods=['GET'])
@jwt_required()
def get_availability_summary():
    month_str = request.args.get('month')
    try:
        year, month = (int(part) for part in month_str.split('-'))
        first_day = date(year, month, 1)
    except (ValueError, AttributeError, TypeError):
        return jsonify({'message': 'Mes inválido, usa el formato YYYY-MM'}), 400

    days_in_month = calendar_module.monthrange(year, month)[1]
    month_start = datetime.combine(first_day, time.min)
    month_end = datetime.combine(date(year, month, days_in_month), time.max)

    booked_rows = (
        db.session.query(Appointment.appointment_datetime)
        .filter(
            Appointment.appointment_datetime.between(month_start, month_end),
            Appointment.status != 'Cancelada',
        )
        .all()
    )
    booked_hours_by_day = {}
    for (dt,) in booked_rows:
        booked_hours_by_day.setdefault(dt.date(), set()).add(dt.hour)

    today = date.today()
    now = datetime.now()
    days = []
    for day_num in range(1, days_in_month + 1):
        current = date(year, month, day_num)
        if current < today:
            has_availability = False
        else:
            slot_hours = _slot_hours_for(current)
            if current == today:
                slot_hours = [h for h in slot_hours if datetime.combine(current, time(hour=h)) > now]
            booked_hours = booked_hours_by_day.get(current, set())
            has_availability = any(hour not in booked_hours for hour in slot_hours)
        days.append({'date': current.isoformat(), 'hasAvailability': has_availability})

    return jsonify({'month': month_str, 'days': days})


@appointments_bp.route('', methods=['POST'])
@jwt_required()
def create_appointment():
    data = request.get_json(silent=True) or {}

    required = ['petId', 'date', 'time', 'reason']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'message': f'Faltan campos requeridos: {", ".join(missing)}'}), 400

    pet = Pet.query.filter_by(id=data['petId'], owner_id=_current_user_id(), is_active=True).first()
    if not pet:
        return jsonify({'message': 'Mascota no encontrada'}), 404

    try:
        target_date = date.fromisoformat(data['date'])
        hour = int(str(data['time']).split(':')[0])
    except (ValueError, IndexError):
        return jsonify({'message': 'Fecha u hora inválida'}), 400

    if hour not in _slot_hours_for(target_date):
        return jsonify({'message': 'Ese horario está fuera de la atención de la veterinaria'}), 400

    appointment_dt = datetime.combine(target_date, time(hour=hour))
    if appointment_dt <= datetime.now():
        return jsonify({'message': 'No puedes agendar una cita en el pasado'}), 400

    booked_count = Appointment.query.filter(
        Appointment.appointment_datetime == appointment_dt,
        Appointment.status != 'Cancelada',
    ).count()
    if booked_count >= SLOT_CAPACITY:
        return jsonify({'message': 'Ese horario ya no está disponible, elige otro'}), 409

    appointment = Appointment(
        pet_id=pet.id,
        owner_id=_current_user_id(),
        appointment_datetime=appointment_dt,
        reason=data['reason'],
        notes=data.get('notes') or None,
    )
    db.session.add(appointment)
    db.session.flush()

    log_audit(
        _current_user_id(), 'Citas', 'create',
        f'Agendó una cita para "{pet.name}" el {appointment_dt.strftime("%Y-%m-%d %H:%M")}',
        entity_type='appointment', entity_id=appointment.id,
    )
    db.session.commit()
    send_appointment_created(appointment)

    return jsonify(_appointment_payload(appointment)), 201


@appointments_bp.route('/<int:appointment_id>', methods=['GET'])
@jwt_required()
def get_appointment(appointment_id):
    user = User.query.get(_current_user_id())
    staff_roles = {r.name for r in user.roles} & {'admin', 'veterinario'}
    if staff_roles:
        appointment = Appointment.query.get_or_404(appointment_id)
    else:
        appointment = _get_owned_appointment_or_404(appointment_id)
    return jsonify(_appointment_payload(appointment))


@appointments_bp.route('/<int:appointment_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_appointment(appointment_id):
    appointment = _get_owned_appointment_or_404(appointment_id)
    before = snapshot_fields(appointment)

    if appointment.status in ('Cancelada', 'Completada'):
        return jsonify({'message': 'Esta cita ya no se puede cancelar'}), 400

    if appointment.appointment_datetime - datetime.now() < timedelta(hours=CANCEL_CUTOFF_HOURS):
        return jsonify({
            'message': f'Solo puedes cancelar hasta {CANCEL_CUTOFF_HOURS} horas antes de la cita'
        }), 400

    data = request.get_json(silent=True) or {}

    appointment.status = 'Cancelada'
    appointment.cancel_reason = data.get('cancelReason') or None
    appointment.is_active = False

    pet_name = appointment.pet.name if appointment.pet else None
    log_audit(
        _current_user_id(), 'Citas', 'cancel',
        f'Canceló la cita de "{pet_name}"' if pet_name else f'Canceló la cita #{appointment.id}',
        entity_type='appointment', entity_id=appointment.id, changes=diff_snapshot(appointment, before),
    )
    db.session.commit()
    send_appointment_cancelled(appointment)

    return jsonify(_appointment_payload(appointment))


@appointments_bp.route('/staff', methods=['GET'])
@role_required('admin', 'veterinario')
def list_staff_appointments():
    user = User.query.get(_current_user_id())
    is_admin = any(r.name == 'admin' for r in user.roles)
    assigned_to_me = request.args.get('assigned_to_me') == 'true'

    query = Appointment.query
    if assigned_to_me or not is_admin:
        # assigned_to_me fuerza el filtro incluso para admin: una cuenta con
        # ambos roles (decision 16) puede pedir explicitamente solo sus
        # propias citas asignadas, ademas de la vista de "todas".
        query = query.filter_by(veterinarian_id=user.id)

    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)

    owner_id = request.args.get('owner_id', type=int)
    if owner_id:
        # Usado desde el detalle de un cliente en /panel/clientes para ver
        # su historial de citas.
        query = query.filter_by(owner_id=owner_id)

    pet_id = request.args.get('pet_id', type=int)
    if pet_id:
        # Usado desde la ficha de una mascota en /panel/mascotas.
        query = query.filter_by(pet_id=pet_id)

    appointments = query.order_by(Appointment.appointment_datetime.asc()).all()
    return jsonify([_appointment_payload(a) for a in appointments])


@appointments_bp.route('/<int:appointment_id>', methods=['PUT'])
@role_required('admin', 'veterinario')
def update_appointment_staff(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    before = snapshot_fields(appointment)
    data = request.get_json(silent=True) or {}

    pet_name = appointment.pet.name if appointment.pet else None
    pet_label = f'de "{pet_name}"' if pet_name else f'#{appointment.id}'
    changes = []

    if 'status' in data:
        status = data['status']
        if status not in STAFF_EDITABLE_STATUSES:
            return jsonify({'message': 'Estado inválido'}), 400
        appointment.status = status
        if status == 'Completada':
            # cierra el gap de la decision 13: is_active pasa a False al cerrar la cita
            appointment.is_active = False
        changes.append(f'estado a "{status}"')

    if 'veterinarianId' in data:
        vet_id = data['veterinarianId']
        if vet_id:
            vet = User.query.get(vet_id)
            if not vet or not any(r.name == 'veterinario' for r in vet.roles):
                return jsonify({'message': 'Veterinario inválido'}), 400
            appointment.veterinarian_id = vet_id
            changes.append(f'veterinario a "{vet.first_name} {vet.last_name}"')
        else:
            appointment.veterinarian_id = None
            changes.append('veterinario a ninguno')

    if changes:
        log_audit(
            _current_user_id(), 'Citas', 'update',
            f'Actualizó la cita {pet_label} ({", ".join(changes)})',
            entity_type='appointment', entity_id=appointment.id, changes=diff_snapshot(appointment, before),
        )

    db.session.commit()
    if data.get('status') == 'Confirmada':
        send_appointment_confirmed(appointment)
    return jsonify(_appointment_payload(appointment))
