from ..extensions import db
from .role import user_roles


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.BigInteger, primary_key=True)
    tipo_documento = db.Column(db.String(10), nullable=False)
    numero_documento = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    reset_code_hash = db.Column(db.String(255))
    reset_code_expires_at = db.Column(db.DateTime)
    reset_code_attempts = db.Column(db.Integer, nullable=False, default=0)
    phone = db.Column(db.String(20))
    direccion = db.Column(db.String(255))
    ciudad = db.Column(db.String(100))
    departamento = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    profile_image_path = db.Column(db.String(255))
    profile_image_mime = db.Column(db.String(50))
    notifications_last_read_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    roles = db.relationship('Role', secondary=user_roles, backref='users')
