from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..models import User


def role_required(*allowed_roles):
    """Requiere sesion valida (JWT) y que el usuario tenga alguno de los roles dados."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = User.query.get(int(get_jwt_identity()))
            user_roles = {r.name for r in user.roles} if user else set()
            if not user_roles & set(allowed_roles):
                return jsonify({'message': 'No tienes permiso para acceder a este recurso'}), 403
            return fn(*args, **kwargs)

        return jwt_required()(wrapper)

    return decorator
