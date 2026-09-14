from ..extensions import db


class Supplier(db.Model):
    __tablename__ = 'suppliers'

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    document_type = db.Column(db.String(10))
    document_number = db.Column(db.String(50))
    primary_contact_name = db.Column(db.String(150))
    primary_contact_phone = db.Column(db.String(20))
    primary_contact_email = db.Column(db.String(255))
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    notes = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
