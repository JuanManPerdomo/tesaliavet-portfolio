"""agregar factura del proveedor a purchase_orders

Revision ID: e083034eb060
Revises: a9d3f7c2e5b1
Create Date: 2026-08-26 00:00:00.000000

RF39: la orden de compra puede llevar adjunta la factura/remision real que
entrega el proveedor (PDF/JPG/PNG, mismo patron de disco + columna *_path
que el resto del proyecto, decision 11) - no tiene nada que ver con
facturacion electronica DIAN (eso sigue fuera de alcance, decision 28/41),
es solo el respaldo documental de una compra que TesaliaVet le hace a un
proveedor.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e083034eb060'
down_revision = 'a9d3f7c2e5b1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('purchase_orders', sa.Column('invoice_path', sa.String(255), nullable=True))
    op.add_column('purchase_orders', sa.Column('invoice_mime', sa.String(50), nullable=True))


def downgrade():
    op.drop_column('purchase_orders', 'invoice_mime')
    op.drop_column('purchase_orders', 'invoice_path')
