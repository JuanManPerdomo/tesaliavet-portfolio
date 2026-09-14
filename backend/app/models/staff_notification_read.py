from ..extensions import db


class StaffNotificationRead(db.Model):
    __tablename__ = 'staff_notification_reads'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    notification_key = db.Column(db.String(64), nullable=False)
    read_at = db.Column(db.DateTime, server_default=db.func.now())
