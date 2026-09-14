from ..extensions import db


class PetVaccination(db.Model):
    __tablename__ = 'pet_vaccinations'

    id = db.Column(db.BigInteger, primary_key=True)
    pet_id = db.Column(db.BigInteger, db.ForeignKey('pets.id'), nullable=False)
    vaccine_id = db.Column(db.Integer, db.ForeignKey('vaccines.id'), nullable=False)
    application_date = db.Column(db.Date, nullable=False)
    next_due_date = db.Column(db.Date)
    batch_number = db.Column(db.String(100))
    expires_at = db.Column(db.Date)
    veterinarian_id = db.Column(db.BigInteger, db.ForeignKey('users.id'))
    reminder_sent_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    vaccine = db.relationship('Vaccine')
    veterinarian = db.relationship('User')
