from ..extensions import db


class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'

    id = db.Column(db.BigInteger, primary_key=True)
    pet_id = db.Column(db.BigInteger, db.ForeignKey('pets.id'), nullable=False)
    veterinarian_id = db.Column(db.BigInteger, db.ForeignKey('users.id'))
    visit_date = db.Column(db.DateTime, nullable=False)
    symptoms = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    treatment = db.Column(db.Text)
    observations = db.Column(db.Text)
    attachment_path = db.Column(db.String(255))
    attachment_mime = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    veterinarian = db.relationship('User')
