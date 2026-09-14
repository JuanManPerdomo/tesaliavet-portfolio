from ..extensions import db


class StockAlert(db.Model):
    __tablename__ = 'stock_alerts'

    id = db.Column(db.BigInteger, primary_key=True)
    product_id = db.Column(db.BigInteger, db.ForeignKey('products.id'), nullable=False)
    current_stock = db.Column(db.Numeric(10, 2), nullable=False)
    min_stock = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum('Activa', 'Resuelta', name='stock_alert_status'), nullable=False, default='Activa')
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.BigInteger, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    product = db.relationship('Product')
    resolver = db.relationship('User')
