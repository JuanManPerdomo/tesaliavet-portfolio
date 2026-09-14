from ..extensions import db


class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'

    id = db.Column(db.BigInteger, primary_key=True)
    supplier_id = db.Column(db.BigInteger, db.ForeignKey('suppliers.id'), nullable=False)
    created_by = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    order_date = db.Column(db.DateTime, server_default=db.func.now())
    expected_delivery_date = db.Column(db.Date)
    received_at = db.Column(db.DateTime)
    status = db.Column(db.Enum('Borrador', 'Enviada', 'Recibida', 'Cancelada'), nullable=False, default='Borrador')
    total_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    shipping_cost = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    tax_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    notes = db.Column(db.Text)
    invoice_path = db.Column(db.String(255))
    invoice_mime = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    supplier = db.relationship('Supplier')
    created_by_user = db.relationship('User')
    details = db.relationship(
        'PurchaseOrderDetail', backref='purchase_order', cascade='all, delete-orphan', order_by='PurchaseOrderDetail.id'
    )
