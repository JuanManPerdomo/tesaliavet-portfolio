from ..extensions import db


class Invoice(db.Model):
    __tablename__ = 'invoices'

    id = db.Column(db.BigInteger, primary_key=True)
    order_id = db.Column(db.BigInteger, db.ForeignKey('sales_orders.id'), nullable=False)
    invoice_number = db.Column(db.String(50), nullable=False)
    # Factura electronica real (envio a la DIAN) fuera de alcance - decision 28
    # en CLAUDE.md. Este es un recibo/factura interna, cufe siempre queda NULL.
    cufe = db.Column(db.String(100))
    issue_date = db.Column(db.DateTime, server_default=db.func.now())
    client_name = db.Column(db.String(200), nullable=False)
    client_document = db.Column(db.String(50), nullable=False)
    client_doc_type = db.Column(db.String(10), nullable=False)
    client_email = db.Column(db.String(255))
    client_address = db.Column(db.String(255))
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)
    tax_total = db.Column(db.Numeric(12, 2), nullable=False)
    total = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(db.Enum('Emitida', 'Anulada', name='invoice_status'), nullable=False, default='Emitida')
    cancellation_reason = db.Column(db.String(255))
    pdf_path = db.Column(db.String(255))
    pdf_mime = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    payment = db.relationship('Payment', backref='invoice', uselist=False)
