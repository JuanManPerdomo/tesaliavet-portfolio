from ..extensions import db


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.SmallInteger, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255))
    parent_id = db.Column(db.SmallInteger, db.ForeignKey('categories.id'))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_pharmacy = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))
