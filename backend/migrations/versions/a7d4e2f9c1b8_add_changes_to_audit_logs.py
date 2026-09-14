"""agregar changes (JSON) a audit_logs

Revision ID: a7d4e2f9c1b8
Revises: f1a3c7e9b2d6
Create Date: 2026-09-07 00:00:00.000000

Detalle campo-por-campo de una edicion real (ej. "Precio de venta: $25.000
-> $27.000") - antes la auditoria solo guardaba una description generica de
una linea ("Editó el producto X"), sin decir que cambio. Columna JSON
(primer uso de este tipo en el proyecto, pero es el ajuste correcto para
una lista estructurada de {field, label, old, new} - evita serializar a
mano como con TEXT). Sin backfill: los registros viejos quedan sin detalle,
solo con su description ya existente.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a7d4e2f9c1b8'
down_revision = 'f1a3c7e9b2d6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('audit_logs', sa.Column('changes', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('audit_logs', 'changes')
