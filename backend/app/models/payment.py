from ..extensions import db


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.BigInteger, primary_key=True)
    invoice_id = db.Column(db.BigInteger, db.ForeignKey('invoices.id'), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    payment_method = db.Column(
        db.Enum('Efectivo', 'Tarjeta', 'Transferencia', name='payment_method'), nullable=False
    )
    reference = db.Column(db.String(100))
    paid_at = db.Column(db.DateTime, server_default=db.func.now())
    # SET NULL en la BD real (igual que resolved_by/responded_by, decision 30
    # en CLAUDE.md) - si se borra la cuenta del empleado, el pago sigue
    # existiendo, solo pierde la autoria.
    registered_by = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='SET NULL'))
    notes = db.Column(db.String(255))
    # Turno de caja en el que se registro (decision 46) - null en pagos previos a
    # esta feature, siempre presente en pagos nuevos (se exige caja abierta).
    cash_register_session_id = db.Column(db.BigInteger, db.ForeignKey('cash_register_sessions.id'))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    registered_by_user = db.relationship('User')
