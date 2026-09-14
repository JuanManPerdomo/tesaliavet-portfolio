from ..extensions import db


class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.BigInteger, primary_key=True)
    pet_id = db.Column(db.BigInteger, db.ForeignKey('pets.id'), nullable=False)
    owner_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    veterinarian_id = db.Column(db.BigInteger, db.ForeignKey('users.id'))
    appointment_datetime = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.String(255))
    status = db.Column(
        db.Enum('Pendiente', 'Confirmada', 'Cancelada', 'Completada', name='appointment_status'),
        nullable=False,
        default='Pendiente',
    )
    cancel_reason = db.Column(db.String(255))
    reminder_sent_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    pet = db.relationship('Pet')
    owner = db.relationship('User', foreign_keys=[owner_id])
    veterinarian = db.relationship('User', foreign_keys=[veterinarian_id])
