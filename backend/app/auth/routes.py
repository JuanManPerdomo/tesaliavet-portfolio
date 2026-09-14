import os
import re
import secrets
from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify, current_app, send_file, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)

from ..extensions import db
from ..models import User, Role
from .mailer import send_password_reset_code, send_welcome
from ..audit.service import log_audit

auth_bp = Blueprint('auth', __name__)

RESET_CODE_VALID_MINUTES = 10
RESET_CODE_MAX_ATTEMPTS = 5

DEFAULT_ROLE = 'cliente'


def validate_password_strength(password):
    """Devuelve un mensaje de error si la contraseña no cumple la
    política, o None si es válida. Aplica solo a contraseñas NUEVAS
    (registro/cambio/reseteo/creación desde el panel) - las cuentas ya
    existentes no se fuerzan a actualizar la suya (decisión del
    2026-08-25, confirmada con Juan Manuel)."""
    if len(password) < 8:
        return 'La contraseña debe tener al menos 8 caracteres'
    if not re.search(r'[A-Z]', password):
        return 'La contraseña debe incluir al menos una letra mayúscula'
    if not re.search(r'[0-9]', password):
        return 'La contraseña debe incluir al menos un número'
    if not re.search(r'[^A-Za-z0-9]', password):
        return 'La contraseña debe incluir al menos un carácter especial (ej. !@#$%)'
    return None

ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png'}
EXTENSION_BY_MIME = {'image/jpeg': 'jpg', 'image/png': 'png'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


def _user_payload(user):
    return {
        'id': user.id,
        'firstName': user.first_name,
        'lastName': user.last_name,
        'email': user.email,
        'documentType': user.tipo_documento,
        'documentNumber': user.numero_documento,
        'phone': user.phone,
        'direccion': user.direccion,
        'ciudad': user.ciudad,
        'departamento': user.departamento,
        'roles': [role.name for role in user.roles],
        'createdAt': user.created_at.isoformat() if user.created_at else None,
        'profileImageUrl': '/auth/me/photo' if user.profile_image_path else None,
    }


def _users_upload_dir():
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'users')
    os.makedirs(path, exist_ok=True)
    return path


def _save_profile_photo(user, photo_file):
    if photo_file.mimetype not in ALLOWED_IMAGE_TYPES:
        return 'La foto debe ser JPG o PNG'
    content = photo_file.read()
    if len(content) > MAX_IMAGE_SIZE:
        return 'La foto no debe superar 5MB'

    upload_dir = _users_upload_dir()
    for existing in os.listdir(upload_dir):
        if existing.startswith(f'user_{user.id}.'):
            os.remove(os.path.join(upload_dir, existing))

    filename = f'user_{user.id}.{EXTENSION_BY_MIME[photo_file.mimetype]}'
    with open(os.path.join(upload_dir, filename), 'wb') as f:
        f.write(content)

    user.profile_image_path = f'users/{filename}'
    user.profile_image_mime = photo_file.mimetype
    return None


def _remove_profile_photo(user):
    """Deja al usuario sin foto de perfil (borra el archivo real de disco) -
    pedido explícito de Juan Manuel: poder quitar cualquier imagen, no solo
    reemplazarla."""
    if not user.profile_image_path:
        return
    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], user.profile_image_path)
    if os.path.exists(full_path):
        os.remove(full_path)
    user.profile_image_path = None
    user.profile_image_mime = None


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}

    required = ['firstName', 'lastName', 'documentType', 'documentNumber', 'email', 'phone', 'password']
    missing = [field for field in required if not data.get(field)]
    if missing:
        return jsonify({'message': f'Faltan campos requeridos: {", ".join(missing)}'}), 400

    password_error = validate_password_strength(data['password'])
    if password_error:
        return jsonify({'message': password_error}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Ya existe una cuenta con este correo'}), 409

    if User.query.filter_by(numero_documento=data['documentNumber']).first():
        return jsonify({'message': 'Ya existe una cuenta con este número de documento'}), 409

    role = Role.query.filter_by(name=DEFAULT_ROLE).first()
    if not role:
        role = Role(name=DEFAULT_ROLE, description='Cliente registrado desde la plataforma')
        db.session.add(role)

    user = User(
        tipo_documento=data['documentType'],
        numero_documento=data['documentNumber'],
        first_name=data['firstName'],
        last_name=data['lastName'],
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        phone=data.get('phone'),
    )
    user.roles.append(role)

    db.session.add(user)
    db.session.flush()
    log_audit(
        user.id, 'Usuarios', 'create',
        f'Se registró como cliente ("{user.first_name} {user.last_name}")',
        entity_type='user', entity_id=user.id,
    )
    db.session.commit()
    send_welcome(user)

    token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    return jsonify({'token': token, 'refreshToken': refresh_token, 'user': _user_payload(user)}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Correo y contraseña son requeridos'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'message': 'Correo o contraseña incorrectos'}), 401

    if not user.is_active:
        return jsonify({'message': 'Cuenta inactiva'}), 403

    log_audit(user.id, 'Sesión', 'login', f'Inició sesión ("{user.first_name} {user.last_name}")')
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    return jsonify({'token': token, 'refreshToken': refresh_token, 'user': _user_payload(user)}), 200


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json(silent=True) or {}
    email = data.get('email')
    if not email:
        return jsonify({'message': 'El correo es requerido'}), 400

    # Mismo mensaje exista o no la cuenta - no revela si un correo esta
    # registrado (evitaria que este endpoint sirva para enumerar cuentas).
    user = User.query.filter_by(email=email).first()
    if user and user.is_active:
        code = f'{secrets.randbelow(1_000_000):06d}'
        user.reset_code_hash = generate_password_hash(code)
        user.reset_code_expires_at = datetime.now() + timedelta(minutes=RESET_CODE_VALID_MINUTES)
        user.reset_code_attempts = 0
        db.session.commit()
        send_password_reset_code(user.email, code)

    return jsonify({
        'message': 'Si existe una cuenta asociada a ese correo, te enviamos un código de verificación'
    })


def _validate_reset_code(email, code):
    """Devuelve el User si el codigo es valido, o None si no lo es
    (invalido, vencido, sin intentos disponibles, o cuenta inexistente/
    inactiva) - incrementa el contador de intentos fallidos cuando el
    codigo no coincide. Compartido por /verify-reset-code y
    /reset-password para no duplicar la validacion."""
    user = User.query.filter_by(email=email).first()
    if not user or not user.is_active or not user.reset_code_hash or not user.reset_code_expires_at:
        return None
    if user.reset_code_expires_at < datetime.now() or user.reset_code_attempts >= RESET_CODE_MAX_ATTEMPTS:
        return None
    if not check_password_hash(user.reset_code_hash, code):
        user.reset_code_attempts += 1
        db.session.commit()
        return None
    return user


@auth_bp.route('/verify-reset-code', methods=['POST'])
def verify_reset_code():
    # Paso intermedio (2026-08-25): confirma el codigo ANTES de mostrar el
    # formulario de nueva contraseña, sin gastar/limpiar el codigo todavia
    # - reset-password lo vuelve a validar cuando el usuario ya eligio su
    # nueva clave.
    data = request.get_json(silent=True) or {}
    email = data.get('email')
    code = (data.get('code') or '').strip()
    if not email or not code:
        return jsonify({'message': 'El correo y el código son requeridos'}), 400

    if not _validate_reset_code(email, code):
        return jsonify({'message': 'Código inválido o vencido'}), 400
    return jsonify({'valid': True})


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json(silent=True) or {}
    email = data.get('email')
    code = (data.get('code') or '').strip()
    new_password = data.get('newPassword')

    if not email or not code or not new_password:
        return jsonify({'message': 'El correo, el código y la nueva contraseña son requeridos'}), 400
    password_error = validate_password_strength(new_password)
    if password_error:
        return jsonify({'message': password_error}), 400

    user = _validate_reset_code(email, code)
    if not user:
        return jsonify({'message': 'Código inválido o vencido'}), 400

    user.password_hash = generate_password_hash(new_password)
    user.reset_code_hash = None
    user.reset_code_expires_at = None
    user.reset_code_attempts = 0
    db.session.commit()
    return jsonify({'message': 'Contraseña actualizada correctamente'})


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # No invalida nada del lado del servidor (decision 8: sin blacklist de
    # tokens todavia) - existe solo para dejar el registro de auditoria,
    # el cierre de sesion real sigue siendo 100% del frontend (borra
    # localStorage).
    user = User.query.get(int(get_jwt_identity()))
    if user:
        log_audit(user.id, 'Sesión', 'logout', f'Cerró sesión ("{user.first_name} {user.last_name}")')
        db.session.commit()
    return jsonify({'message': 'Sesión cerrada'})


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    # Requiere el refresh token (no el access token) en el header - lo marca
    # el claim interno que created_refresh_token agrega, jwt_required(refresh=True)
    # lo valida solo. No hay blacklist/revocacion de refresh tokens todavia
    # (fuera de alcance de esta iteracion): "cerrar sesion" sigue siendo solo
    # del lado del frontend (borra los tokens de localStorage), un refresh
    # token robado sigue siendo valido hasta que expire por si solo (30 dias).
    user = User.query.get(int(get_jwt_identity()))
    if not user or not user.is_active:
        return jsonify({'message': 'Cuenta inactiva o inexistente'}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({'token': token})


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user = User.query.get_or_404(int(get_jwt_identity()))
    return jsonify(_user_payload(user))


@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_me():
    # El cliente autoreporta ciudad/direccion/telefono (gap real: el registro
    # nunca los pide) y puede corregir nombre/correo - mismo patron de
    # validacion que update_client en staff/routes.py, pero sobre la propia
    # cuenta (JWT identity) en vez de un client_id de la URL. Documento e
    # is_active no son editables aqui - documento es dato de identidad,
    # is_active lo gestiona el personal.
    user = User.query.get_or_404(int(get_jwt_identity()))
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

    db.session.commit()
    return jsonify(_user_payload(user))


@auth_bp.route('/me/photo', methods=['PUT'])
@jwt_required()
def update_my_photo():
    user = User.query.get_or_404(int(get_jwt_identity()))
    photo = request.files.get('photo')
    if not photo or not photo.filename:
        return jsonify({'message': 'La foto es requerida'}), 400

    error = _save_profile_photo(user, photo)
    if error:
        return jsonify({'message': error}), 400

    db.session.commit()
    return jsonify(_user_payload(user))


@auth_bp.route('/me/photo', methods=['DELETE'])
@jwt_required()
def delete_my_photo():
    user = User.query.get_or_404(int(get_jwt_identity()))
    _remove_profile_photo(user)
    db.session.commit()
    return jsonify(_user_payload(user))


@auth_bp.route('/me/photo', methods=['GET'])
@jwt_required()
def get_my_photo():
    user = User.query.get_or_404(int(get_jwt_identity()))
    if not user.profile_image_path:
        abort(404)
    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], user.profile_image_path)
    if not os.path.exists(full_path):
        abort(404)
    return send_file(full_path, mimetype=user.profile_image_mime or 'image/jpeg')


@auth_bp.route('/password', methods=['PUT'])
@jwt_required()
def change_password():
    user = User.query.get_or_404(int(get_jwt_identity()))
    data = request.get_json(silent=True) or {}

    current_password = data.get('currentPassword')
    new_password = data.get('newPassword')

    if not current_password or not new_password:
        return jsonify({'message': 'La contraseña actual y la nueva son requeridas'}), 400

    if not check_password_hash(user.password_hash, current_password):
        return jsonify({'message': 'La contraseña actual no es correcta'}), 400

    password_error = validate_password_strength(new_password)
    if password_error:
        return jsonify({'message': password_error}), 400

    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({'message': 'Contraseña actualizada correctamente'})
