from ..extensions import db


class Return(db.Model):
    __tablename__ = 'returns'

    id = db.Column(db.BigInteger, primary_key=True)
    order_id = db.Column(db.BigInteger, db.ForeignKey('sales_orders.id'), nullable=False)
    # SET NULL en la BD real (igual que payments.registered_by, decision 41) - si se
    # borra la cuenta del admin, la devolucion sigue existiendo, solo pierde autoria.
    registered_by = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='SET NULL'))
    reason = db.Column(db.String(255), nullable=False)
    refund_method = db.Column(db.Enum('Efectivo', 'Transferencia', name='return_refund_method'), nullable=False)
    refund_reference = db.Column(db.String(100))
    refund_amount = db.Column(db.Numeric(12, 2), nullable=False)
    # Turno de caja en el que se registro (decision 46) - mismo criterio que Payment.
    cash_register_session_id = db.Column(db.BigInteger, db.ForeignKey('cash_register_sessions.id'))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    order = db.relationship('SalesOrder')
    registered_by_user = db.relationship('User')
    items = db.relationship('ReturnItem', backref='return_', cascade='all, delete-orphan', order_by='ReturnItem.id')


class ReturnItem(db.Model):
    __tablename__ = 'return_items'

    id = db.Column(db.BigInteger, primary_key=True)
    return_id = db.Column(db.BigInteger, db.ForeignKey('returns.id'), nullable=False)
    sales_order_item_id = db.Column(db.BigInteger, db.ForeignKey('sales_order_items.id'), nullable=False)
    product_id = db.Column(db.BigInteger, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Numeric(10, 2), nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    tax_rate = db.Column(db.Numeric(5, 2), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    product = db.relationship('Product')
    sales_order_item = db.relationship('SalesOrderItem')
