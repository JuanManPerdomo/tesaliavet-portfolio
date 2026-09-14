from ..extensions import db


class SalesOrder(db.Model):
    __tablename__ = 'sales_orders'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(
        db.Enum('Pendiente', 'Pagado', 'Entregado', 'Cancelado', name='sales_order_status'),
        nullable=False,
        default='Pendiente',
    )
    payment_method = db.Column(
        db.Enum('Efectivo', 'Tarjeta', 'Transferencia', name='sales_order_payment_method'),
        nullable=False,
    )
    shipping_name = db.Column(db.String(200), nullable=False)
    shipping_phone = db.Column(db.String(20))
    shipping_address = db.Column(db.String(255), nullable=False)
    shipping_city = db.Column(db.String(100), nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    tax_total = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    total = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    notes = db.Column(db.Text)
    cancel_reason = db.Column(db.String(255))
    # Distinto de updated_at (que se pisa con cualquier cambio del pedido,
    # como registrar el pago) - necesario para el plazo real de 8 dias de
    # Devoluciones. Se llena en update_order_staff al pasar a 'Entregado'.
    delivered_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    user = db.relationship('User')
    items = db.relationship(
        'SalesOrderItem', backref='order', cascade='all, delete-orphan', order_by='SalesOrderItem.id'
    )
    invoice = db.relationship('Invoice', backref='order', uselist=False)
    # Sin backref aca (Return ya declara su propio `order` del lado de
    # return_.py) - dos relationships independientes sobre el mismo FK
    # (Return.order_id) no chocan mientras ninguna use backref.
    returns = db.relationship('Return', order_by='Return.id')


class SalesOrderItem(db.Model):
    __tablename__ = 'sales_order_items'

    id = db.Column(db.BigInteger, primary_key=True)
    order_id = db.Column(db.BigInteger, db.ForeignKey('sales_orders.id'), nullable=False)
    product_id = db.Column(db.BigInteger, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Numeric(10, 2), nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    tax_rate = db.Column(db.Numeric(5, 2), nullable=False)
    # subtotal/tax_amount/total son columnas GENERATED ALWAYS ... STORED en MySQL
    # (quantity * unit_price, etc.) - la app nunca las escribe, MySQL las calcula
    # solas. server_default=FetchedValue() le dice a SQLAlchemy que no las mande
    # en el INSERT (fallaria: "no se permite valor para columna generada") y que
    # las refresque despues desde la BD.
    subtotal = db.Column(db.Numeric(12, 2), server_default=db.FetchedValue())
    tax_amount = db.Column(db.Numeric(12, 2), server_default=db.FetchedValue())
    total = db.Column(db.Numeric(12, 2), server_default=db.FetchedValue())
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    product = db.relationship('Product')
