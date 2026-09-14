"""agregar costos adicionales (transporte, impuestos) a purchase_orders

Revision ID: ead9ea991709
Revises: e083034eb060
Create Date: 2026-08-26 00:00:00.000000

RF40: hoy en la practica el proveedor factura todo incluido en el precio
del producto (confirmado con Juan Manuel), pero se implementa igual como
prevencion - dos columnas de orden a nivel de cabecera (no por linea),
sumadas al total junto con el subtotal de productos.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ead9ea991709'
down_revision = 'e083034eb060'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'purchase_orders',
        sa.Column('shipping_cost', sa.Numeric(12, 2), nullable=False, server_default='0'),
    )
    op.add_column(
        'purchase_orders',
        sa.Column('tax_amount', sa.Numeric(12, 2), nullable=False, server_default='0'),
    )


def downgrade():
    op.drop_column('purchase_orders', 'tax_amount')
    op.drop_column('purchase_orders', 'shipping_cost')
