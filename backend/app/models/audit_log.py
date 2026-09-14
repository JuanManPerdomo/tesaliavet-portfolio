from ..extensions import db


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.BigInteger, primary_key=True)
    # SET NULL en la BD real (igual que registered_by/resolved_by) - pero a
    # diferencia de esos casos, user_name/user_email quedan como snapshot de
    # texto: el proposito de un log de auditoria es sobrevivir a que se
    # borre la cuenta, no perder la autoria como en un pago/devolucion.
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='SET NULL'))
    user_name = db.Column(db.String(200))
    user_email = db.Column(db.String(255))
    module = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.BigInteger)
    description = db.Column(db.String(255), nullable=False)
    # Diff campo-por-campo de una edicion real ({field, label, old, new}) -
    # None para create/delete/login/etc, donde la description ya lo dice
    # todo. Sin backfill, los registros viejos simplemente no lo tienen.
    changes = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User')
