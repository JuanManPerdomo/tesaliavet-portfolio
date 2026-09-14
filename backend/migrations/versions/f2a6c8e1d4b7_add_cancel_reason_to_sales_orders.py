"""agregar cancel_reason a sales_orders

Revision ID: f2a6c8e1d4b7
Revises: e7c4a1f9b3d6
Create Date: 2026-08-23 00:00:00.000000

RF25 (matriz de trazabilidad): anular una venta ya pagada/facturada exige
un motivo obligatorio. Mismo patron que appointments.cancel_reason
(VARCHAR(255) simple, no es PK/FK asi que no aplica la regla de
mysql.BIGINT(unsigned=True)).
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f2a6c8e1d4b7'
down_revision = 'e7c4a1f9b3d6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('sales_orders', sa.Column('cancel_reason', sa.String(255), nullable=True))


def downgrade():
    op.drop_column('sales_orders', 'cancel_reason')
