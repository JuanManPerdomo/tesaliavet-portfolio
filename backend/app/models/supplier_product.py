from ..extensions import db


class SupplierProduct(db.Model):
    __tablename__ = 'supplier_products'

    id = db.Column(db.BigInteger, primary_key=True)
    supplier_id = db.Column(db.BigInteger, db.ForeignKey('suppliers.id'), nullable=False)
    product_id = db.Column(db.BigInteger, db.ForeignKey('products.id'), nullable=False)
    supplier_sku = db.Column(db.String(100))
    purchase_price = db.Column(db.Numeric(12, 2))
    lead_time_days = db.Column(db.SmallInteger)
    is_preferred = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    supplier = db.relationship('Supplier')
    product = db.relationship('Product')
