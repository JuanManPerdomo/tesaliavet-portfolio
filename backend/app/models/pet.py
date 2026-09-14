from ..extensions import db


class Pet(db.Model):
    __tablename__ = 'pets'

    id = db.Column(db.BigInteger, primary_key=True)
    owner_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    species_id = db.Column(db.SmallInteger, db.ForeignKey('species.id'), nullable=False)
    breed_id = db.Column(db.Integer, db.ForeignKey('breeds.id'))
    gender = db.Column(
        db.Enum('Macho', 'Hembra', 'Desconocido', name='pet_gender'),
        nullable=False,
        default='Desconocido',
    )
    birth_date = db.Column(db.Date)
    weight = db.Column(db.Numeric(5, 2))
    color = db.Column(db.String(50))
    notes = db.Column(db.Text)
    image_path = db.Column(db.String(255))
    image_mime = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    owner = db.relationship('User', backref='pets')
    species = db.relationship('Species')
    breed = db.relationship('Breed')
