from ..extensions import db


class Pqrs(db.Model):
    __tablename__ = 'pqrs'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'))
    sender_name = db.Column(db.String(150), nullable=False)
    sender_email = db.Column(db.String(255), nullable=False)
    sender_phone = db.Column(db.String(20))
    type = db.Column(
        db.Enum('Peticion', 'Queja', 'Reclamo', 'Sugerencia', name='pqrs_type'), nullable=False
    )
    subject = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(
        db.Enum('Abierto', 'En Proceso', 'Resuelto', 'Cerrado', name='pqrs_status'),
        nullable=False,
        default='Abierto',
    )
    response = db.Column(db.Text)
    responded_by = db.Column(db.BigInteger, db.ForeignKey('users.id'))
    attachment_path = db.Column(db.String(255))
    attachment_mime = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    responded_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    responder = db.relationship('User', foreign_keys=[responded_by])
