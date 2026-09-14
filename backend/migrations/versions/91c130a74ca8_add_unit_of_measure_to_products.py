"""add unit of measure to products

Revision ID: 91c130a74ca8
Revises: ed625001e600
Create Date: 2026-08-13 00:00:00.000000

Catalogo fijo de unidades (unit_label), pedido por Juan Manuel para poder
distinguir "2 Bultos" de "2 Kg" al mostrar cantidades (Ordenes de compra,
Alertas de stock, Productos) - sobre todo relevante para Ganaderia. Se
agrega tambien unit_weight_kg (opcional) para casos donde una "unidad" es
en realidad un empaque con un peso conocido (ej. Bulto de 40kg) y el
sistema pueda calcular el total en kg = cantidad x unit_weight_kg.

No hay forma de inferir la unidad real de los 5 productos existentes sin
inventar el dato (decision 7 del CLAUDE.md) - todos quedan en 'Unidad' por
defecto, pendiente de que Juan Manuel los actualice desde el formulario de
producto.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '91c130a74ca8'
down_revision = 'ed625001e600'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'products',
        sa.Column(
            'unit_label',
            sa.Enum('Unidad', 'Bulto', 'Caja', 'Kg', 'Gramo', 'Arroba', 'Litro', 'Mililitro'),
            nullable=False,
            server_default='Unidad',
        ),
    )
    op.add_column('products', sa.Column('unit_weight_kg', sa.Numeric(10, 3), nullable=True))


def downgrade():
    op.drop_column('products', 'unit_weight_kg')
    op.drop_column('products', 'unit_label')
