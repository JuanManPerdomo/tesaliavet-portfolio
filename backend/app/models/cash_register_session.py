from ..extensions import db


class CashRegisterSession(db.Model):
    __tablename__ = 'cash_register_sessions'

    id = db.Column(db.BigInteger, primary_key=True)
    # SET NULL en la BD real (igual que registered_by/resolved_by, decision 30) - si
    # se borra la cuenta del responsable, la sesion sigue existiendo como historial.
    responsible_user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='SET NULL'))
    status = db.Column(db.Enum('Abierta', 'Cerrada', name='cash_register_session_status'),
                        nullable=False, default='Abierta')
    opening_amount = db.Column(db.Numeric(12, 2), nullable=False)
    opening_notes = db.Column(db.String(255))
    opened_at = db.Column(db.DateTime, server_default=db.func.now())
    # Snapshot al momento del cierre - no se recalcula despues aunque cambien los
    # pagos/devoluciones asociados (no deberia pasar, pero un reporte cerrado no
    # deberia moverse solo).
    counted_cash = db.Column(db.Numeric(12, 2))
    expected_cash = db.Column(db.Numeric(12, 2))
    cash_difference = db.Column(db.Numeric(12, 2))
    difference_justification = db.Column(db.String(255))
    closed_at = db.Column(db.DateTime)

    responsible_user = db.relationship('User')
    payments = db.relationship('Payment', backref='cash_register_session')
    returns = db.relationship('Return', backref='cash_register_session')
