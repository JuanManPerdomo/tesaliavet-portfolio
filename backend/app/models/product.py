from ..extensions import db


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.BigInteger, primary_key=True)
    category_id = db.Column(db.SmallInteger, db.ForeignKey('categories.id'), nullable=False)
    species_id = db.Column(db.SmallInteger, db.ForeignKey('species.id'))
    sku = db.Column(db.String(50), nullable=False, unique=True)
    barcode = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    brand = db.Column(db.String(100))
    purchase_price = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    selling_price = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    stock = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    min_stock = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    unit_label = db.Column(
        db.Enum('Unidad', 'Bulto', 'Caja', 'Kg', 'Gramo', 'Arroba', 'Litro', 'Mililitro', 'Onza'),
        nullable=False,
        default='Unidad',
    )
    unit_weight_kg = db.Column(db.Numeric(10, 3))
    tax_rate = db.Column(db.Numeric(5, 2), nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    image_path = db.Column(db.String(255))
    image_mime = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    category = db.relationship('Category')
    species = db.relationship('Species')
