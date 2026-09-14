from ..extensions import db


class Species(db.Model):
    __tablename__ = 'species'

    id = db.Column(db.SmallInteger, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    category_id = db.Column(db.SmallInteger, db.ForeignKey('categories.id'))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    category = db.relationship('Category')
