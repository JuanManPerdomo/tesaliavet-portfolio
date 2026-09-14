import os
from datetime import datetime

from flask import Blueprint, jsonify, request, abort, current_app
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import or_, extract, func, text
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from ..extensions import db
from ..auth.decorators import role_required
from ..auth.routes import validate_password_strength
from ..models import User, Role, Pet, Appointment, MedicalRecord, PetVaccination, SalesOrder, Species
from ..audit.service import diff_snapshot, log_audit, snapshot_fields

staff_bp = Blueprint('staff', __name__)

CLIENT_STATUS_FILTERS = {'active', 'inactive', 'all'}


def _user_payload(user):
    return {
        'id': user.id,
        'firstName': user.first_name,
        'lastName': user.last_name,
        'email': user.email,
        'phone': user.phone,
        'isActive': user.is_active,
        'roles': [role.name for role in user.roles],
    }


@staff_bp.route('/me', methods=['GET'])
@role_required('admin', 'veterinario', 'bodeguero')
def get_staff_profile():
    user = User.query.get(int(get_jwt_identity()))
    return jsonify({
        'id': user.id,
        'firstName': user.first_name,
        'lastName': user.last_name,
        'email': user.email,
        'roles': [role.name for role in user.roles],
    })


@staff_bp.route('/roles', methods=['GET'])
@role_required('admin')
def list_roles():
    roles = Role.query.order_by(Role.name.asc()).all()
    return jsonify([{'id': r.id, 'name': r.name} for r in roles])


@staff_bp.route('/users', methods=['GET'])
@role_required('admin')
def list_users():
    query = User.query
    role_name = request.args.get('role')
    if role_name:
        query = query.join(User.roles).filter(Role.name == role_name)

    search = request.args.get('search')
    if search:
        like = f'%{search}%'
        # func.concat cubre "Nombre Apellido" completo - antes solo matcheaba
        # first_name/last_name por separado, asi que buscar el nombre completo
        # de un cliente real (el caso mas comun al buscarlo) daba "no encontrado".
        query = query.filter(or_(
            User.first_name.ilike(like),
            User.last_name.ilike(like),
            User.email.ilike(like),
            User.numero_documento.ilike(like),
            func.concat(User.first_name, ' ', User.last_name).ilike(like),
        ))

    query = query.order_by(User.first_name.asc())

    page = request.args.get('page', default=1, type=int)
    per_page = min(request.args.get('per_page', default=10, type=int), 100)
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'users': [_user_payload(u) for u in paginated.items],
        'total': paginated.total,
        'page': paginated.page,
        'per_page': paginated.per_page,
        'pages': paginated.pages,
    })


@staff_bp.route('/users', methods=['POST'])
@role_required('admin')
def create_user():
    # Para clientes que compran en la tienda fisica de Tesalia (decision 28):
    # el personal necesita poder crear la cuenta ahi mismo, no solo asignar
    # roles a cuentas que ya se registraron solas (register publico).
    data = request.get_json(silent=True) or {}

    required = ['firstName', 'lastName', 'documentType', 'documentNumber', 'email', 'password']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'message': f'Faltan campos requeridos: {", ".join(missing)}'}), 400

    password_error = validate_password_strength(data['password'])
    if password_error:
        return jsonify({'message': password_error}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Ya existe una cuenta con ese correo'}), 400

    if User.query.filter_by(numero_documento=data['documentNumber']).first():
        return jsonify({'message': 'Ya existe una cuenta con ese número de documento'}), 400

    role_names = data.get('roles')
    if not isinstance(role_names, list) or not role_names:
        return jsonify({'message': 'Selecciona al menos un rol'}), 400

    roles = Role.query.filter(Role.name.in_(role_names)).all()
    if len(roles) != len(set(role_names)):
        return jsonify({'message': 'Uno o más roles no existen'}), 400

    user = User(
        tipo_documento=data['documentType'],
        numero_documento=data['documentNumber'],
        first_name=data['firstName'],
        last_name=data['lastName'],
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        phone=data.get('phone') or None,
    )
    user.roles = roles

    db.session.add(user)
    db.session.flush()
    log_audit(
        int(get_jwt_identity()), 'Usuarios', 'create',
        f'Creó la cuenta "{user.first_name} {user.last_name}" ({", ".join(role_names)})',
        entity_type='user', entity_id=user.id,
    )
    db.session.commit()
    return jsonify(_user_payload(user)), 201


@staff_bp.route('/users/<int:user_id>', methods=['PUT'])
@role_required('admin')
def update_user(user_id):
    # Edita datos basicos de CUALQUIER cuenta (cliente o personal) - a
    # diferencia de update_client (solo cuentas con rol 'cliente'), este
    # endpoint nuevo no tiene esa restriccion, para poder editar tambien
    # admin/veterinario/bodeguero desde Usuarios y roles. Documento no es
    # editable (mismo criterio que /mi-perfil, decision 34 - dato de
    # identidad) ni la contraseña (eso lo cambia cada quien desde su
    # propio perfil).
    user = User.query.get_or_404(user_id)
    before = snapshot_fields(user)
    data = request.get_json(silent=True) or {}

    if 'firstName' in data:
        if not data['firstName']:
            return jsonify({'message': 'El nombre es requerido'}), 400
        user.first_name = data['firstName']

    if 'lastName' in data:
        if not data['lastName']:
            return jsonify({'message': 'El apellido es requerido'}), 400
        user.last_name = data['lastName']

    if 'email' in data:
        if not data['email']:
            return jsonify({'message': 'El correo es requerido'}), 400
        if data['email'] != user.email and User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Ya existe una cuenta con ese correo'}), 400
        user.email = data['email']

    if 'phone' in data:
        user.phone = data['phone'] or None

    log_audit(
        int(get_jwt_identity()), 'Usuarios', 'update',
        f'Editó la cuenta "{user.first_name} {user.last_name}"', entity_type='user', entity_id=user.id,
        changes=diff_snapshot(user, before),
    )
    db.session.commit()
    return jsonify(_user_payload(user))


@staff_bp.route('/users/<int:user_id>/roles', methods=['PUT'])
@role_required('admin')
def update_user_roles(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json(silent=True) or {}
    role_names = data.get('roles')
    if not isinstance(role_names, list):
        return jsonify({'message': 'roles debe ser una lista de nombres de rol'}), 400

    roles = Role.query.filter(Role.name.in_(role_names)).all()
    if len(roles) != len(set(role_names)):
        return jsonify({'message': 'Uno o más roles no existen'}), 400

    user.roles = roles
    log_audit(
        int(get_jwt_identity()), 'Usuarios', 'role_change',
        f'Cambió los roles de "{user.first_name} {user.last_name}" a ({", ".join(role_names) or "ninguno"})',
        entity_type='user', entity_id=user.id,
    )
    db.session.commit()
    return jsonify(_user_payload(user))


@staff_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@role_required('admin')
def update_user_status(user_id):
    if user_id == int(get_jwt_identity()):
        return jsonify({'message': 'No puedes desactivar tu propia cuenta'}), 400

    user = User.query.get_or_404(user_id)
    before = snapshot_fields(user)
    data = request.get_json(silent=True) or {}
    if 'isActive' not in data:
        return jsonify({'message': 'isActive es requerido'}), 400

    value = data['isActive']
    user.is_active = value if isinstance(value, bool) else str(value).lower() in ('true', '1', 'on')
    log_audit(
        int(get_jwt_identity()), 'Usuarios', 'activate' if user.is_active else 'deactivate',
        f'{"Activó" if user.is_active else "Desactivó"} la cuenta "{user.first_name} {user.last_name}"',
        entity_type='user', entity_id=user.id, changes=diff_snapshot(user, before),
    )
    db.session.commit()
    return jsonify(_user_payload(user))


@staff_bp.route('/users/<int:user_id>', methods=['DELETE'])
@role_required('admin')
def delete_user(user_id):
    # Borrado permanente real, mismo patron de dos pasos que Productos/
    # Proveedores/Categorias: solo sobre cuentas ya inactivas. Decision 30
    # (revisada con Juan Manuel): se borra en cascada TODO lo que el usuario
    # posee como dueno (mascotas + su historial medico/vacunas/citas, mismo
    # criterio que "Eliminar mascota" del lado cliente) - pero NO se toca lo
    # que haya autorado como personal (registros medicos/vacunas/citas de
    # mascotas ajenas, respuestas de PQRS, alertas de stock resueltas): esas
    # columnas son SET NULL en la BD, se pierde quien lo hizo pero nunca se
    # borra el historial clinico real de un tercero.
    if user_id == int(get_jwt_identity()):
        return jsonify({'message': 'No puedes eliminar tu propia cuenta'}), 400

    user = User.query.get_or_404(user_id)
    if user.is_active:
        return jsonify({'message': 'Desactiva la cuenta antes de eliminarla permanentemente'}), 400

    for pet in Pet.query.filter_by(owner_id=user.id).all():
        if pet.image_path:
            full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], pet.image_path)
            if os.path.exists(full_path):
                os.remove(full_path)
        MedicalRecord.query.filter_by(pet_id=pet.id).delete()
        PetVaccination.query.filter_by(pet_id=pet.id).delete()
        db.session.execute(text('DELETE FROM appointments WHERE pet_id = :pet_id'), {'pet_id': pet.id})
        db.session.delete(pet)

    Appointment.query.filter_by(owner_id=user.id).delete()

    deleted_name = f'{user.first_name} {user.last_name}'
    deleted_id = user.id
    log_audit(
        int(get_jwt_identity()), 'Usuarios', 'delete',
        f'Eliminó permanentemente la cuenta "{deleted_name}"', entity_type='user', entity_id=deleted_id,
    )

    try:
        db.session.delete(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'message': 'No puedes eliminar esta cuenta: tiene registros asociados en el sistema '
                       '(ej. pedidos o compras) que deben conservarse'
        }), 400

    return '', 204


def _client_payload(user):
    return {
        'id': user.id,
        'firstName': user.first_name,
        'lastName': user.last_name,
        'email': user.email,
        'phone': user.phone,
        'tipoDocumento': user.tipo_documento,
        'numeroDocumento': user.numero_documento,
        'direccion': user.direccion,
        'ciudad': user.ciudad,
        'departamento': user.departamento,
        'isActive': user.is_active,
        'createdAt': user.created_at.isoformat() if user.created_at else None,
    }


def _client_query():
    return User.query.join(User.roles).filter(Role.name == 'cliente')


def _get_client_or_404(client_id):
    user = User.query.get_or_404(client_id)
    if not any(r.name == 'cliente' for r in user.roles):
        abort(404, description='Cliente no encontrado')
    return user


@staff_bp.route('/clients', methods=['GET'])
@role_required('admin', 'bodeguero')
def list_clients():
    # Bodeguero no tiene la seccion "Clientes" del panel (sigue fuera de su
    # alcance, decision Bodeguero ampliada 2026-09-02) pero SI necesita
    # buscar un cliente al registrar una venta de mostrador (Punto de
    # venta, decision 81) - ese formulario reusa este mismo endpoint de
    # busqueda. El resto de endpoints de /clients (detalle, stats, editar)
    # se quedan admin-only a proposito.
    query = _client_query()

    status = request.args.get('status')
    if status not in CLIENT_STATUS_FILTERS:
        status = 'active'
    if status == 'active':
        query = query.filter(User.is_active.is_(True))
    elif status == 'inactive':
        query = query.filter(User.is_active.is_(False))
    # 'all' -> sin filtro de is_active

    city = request.args.get('city')
    if city:
        query = query.filter(User.ciudad == city)

    search = request.args.get('search')
    if search:
        like = f'%{search}%'
        # func.concat cubre "Nombre Apellido" completo - antes solo matcheaba
        # first_name/last_name por separado, asi que buscar el nombre completo
        # de un cliente real (el caso mas comun al buscarlo, ej. desde Punto
        # de venta, decision 81) daba "no encontrado".
        query = query.filter(or_(
            User.first_name.ilike(like),
            User.last_name.ilike(like),
            User.email.ilike(like),
            func.concat(User.first_name, ' ', User.last_name).ilike(like),
        ))

    query = query.order_by(User.first_name.asc())

    page = request.args.get('page', default=1, type=int)
    per_page = min(request.args.get('per_page', default=10, type=int), 100)
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'clients': [_client_payload(u) for u in paginated.items],
        'total': paginated.total,
        'page': paginated.page,
        'per_page': paginated.per_page,
        'pages': paginated.pages,
    })


@staff_bp.route('/clients/stats', methods=['GET'])
@role_required('admin')
def client_stats():
    # KPIs y datos de graficas para /panel/clientes - solo cuenta lo que
    # existe de verdad (ver decision 7 en CLAUDE.md): sin Pedidos/Facturacion
    # no hay "gasto total" ni "ultima compra" que mostrar aqui.
    base = _client_query()
    total = base.count()
    active = base.filter(User.is_active.is_(True)).count()
    inactive = base.filter(User.is_active.is_(False)).count()

    now = datetime.now()
    new_this_month = base.filter(
        extract('year', User.created_at) == now.year,
        extract('month', User.created_at) == now.month,
    ).count()

    by_month_rows = (
        db.session.query(
            extract('year', User.created_at),
            extract('month', User.created_at),
            func.count(User.id),
        )
        .join(User.roles).filter(Role.name == 'cliente')
        .group_by(extract('year', User.created_at), extract('month', User.created_at))
        .order_by(extract('year', User.created_at), extract('month', User.created_at))
        .all()
    )
    by_month = [{'year': int(y), 'month': int(m), 'count': c} for y, m, c in by_month_rows]

    by_city_rows = (
        db.session.query(User.ciudad, func.count(User.id))
        .join(User.roles).filter(Role.name == 'cliente', User.ciudad.isnot(None))
        .group_by(User.ciudad)
        .order_by(func.count(User.id).desc())
        .all()
    )
    by_city = [{'city': city, 'count': c} for city, c in by_city_rows]

    # Mascotas por especie (decision 47, dashboard de Inicio) - Perro/Gato ya
    # tienen productos/citas reales, el resto de especies (Ganaderia, decision
    # 20) se agrupan como "Otros" en el frontend.
    pets_by_species_rows = (
        db.session.query(Species.name, func.count(Pet.id))
        .join(Pet, Pet.species_id == Species.id)
        .filter(Pet.is_active.is_(True))
        .group_by(Species.name)
        .all()
    )
    pets_by_species = [{'species': name, 'count': c} for name, c in pets_by_species_rows]
    total_active_pets = sum(row['count'] for row in pets_by_species)

    return jsonify({
        'total': total,
        'active': active,
        'inactive': inactive,
        'newThisMonth': new_this_month,
        'byMonth': by_month,
        'byCity': by_city,
        'petsBySpecies': pets_by_species,
        'totalActivePets': total_active_pets,
    })


def _client_detail_payload(user):
    payload = _client_payload(user)
    payload['petsCount'] = Pet.query.filter_by(owner_id=user.id, is_active=True).count()
    payload['appointmentsCount'] = Appointment.query.filter_by(owner_id=user.id).count()
    payload['ordersCount'] = SalesOrder.query.filter_by(user_id=user.id).count()
    return payload


@staff_bp.route('/clients/<int:client_id>', methods=['GET'])
@role_required('admin')
def get_client(client_id):
    user = _get_client_or_404(client_id)
    return jsonify(_client_detail_payload(user))


@staff_bp.route('/clients/<int:client_id>', methods=['PUT'])
@role_required('admin')
def update_client(client_id):
    user = _get_client_or_404(client_id)
    before = snapshot_fields(user)
    data = request.get_json(silent=True) or {}

    if 'firstName' in data:
        if not data['firstName']:
            return jsonify({'message': 'El nombre es requerido'}), 400
        user.first_name = data['firstName']

    if 'lastName' in data:
        if not data['lastName']:
            return jsonify({'message': 'El apellido es requerido'}), 400
        user.last_name = data['lastName']

    if 'email' in data:
        if not data['email']:
            return jsonify({'message': 'El correo es requerido'}), 400
        if data['email'] != user.email and User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Ya existe una cuenta con ese correo'}), 400
        user.email = data['email']

    if 'phone' in data:
        user.phone = data['phone'] or None

    if 'direccion' in data:
        user.direccion = data['direccion'] or None

    if 'ciudad' in data:
        user.ciudad = data['ciudad'] or None

    if 'departamento' in data:
        user.departamento = data['departamento'] or None

    if 'isActive' in data:
        value = data['isActive']
        user.is_active = value if isinstance(value, bool) else str(value).lower() in ('true', '1', 'on')

    log_audit(
        int(get_jwt_identity()), 'Usuarios', 'update',
        f'Editó el cliente "{user.first_name} {user.last_name}"', entity_type='user', entity_id=user.id,
        changes=diff_snapshot(user, before),
    )
    db.session.commit()
    return jsonify(_client_detail_payload(user))


@staff_bp.route('/clients/<int:client_id>/pets', methods=['GET'])
@role_required('admin')
def list_client_pets(client_id):
    user = _get_client_or_404(client_id)
    pets = Pet.query.filter_by(owner_id=user.id, is_active=True).order_by(Pet.name.asc()).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'species': p.species.name if p.species else None,
        'breed': p.breed.name if p.breed else None,
        'photoUrl': f'/pets/{p.id}/photo' if p.image_path else None,
    } for p in pets])
