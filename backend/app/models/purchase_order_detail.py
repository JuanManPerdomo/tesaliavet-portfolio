from ..extensions import db


class PurchaseOrderDetail(db.Model):
    __tablename__ = 'purchase_order_details'

    id = db.Column(db.BigInteger, primary_key=True)
    purchase_order_id = db.Column(db.BigInteger, db.ForeignKey('purchase_orders.id'), nullable=False)
    product_id = db.Column(db.BigInteger, db.ForeignKey('products.id'), nullable=False)
    quantity_ordered = db.Column(db.Numeric(10, 2), nullable=False)
    quantity_received = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    unit_cost = db.Column(db.Numeric(12, 2), nullable=False)
    subtotal = db.Column(db.Numeric(12, 2))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    product = db.relationship('Product')
