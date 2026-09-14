"""add Onza to products.unit_label

Revision ID: d8a2c6f4b9e3
Revises: c4f9a2e6b8d1
Create Date: 2026-08-28 00:00:00.000000

Catalogo fijo de unidades de medida (decision 33 en CLAUDE.md) - Juan Manuel
pidio agregar "Onza" como opcion adicional para productos que se venden por
onzas. Solo agrega el valor nuevo al ENUM existente, no toca los productos
reales (ninguno queda reasignado).
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd8a2c6f4b9e3'
down_revision = 'c4f9a2e6b8d1'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'products',
        'unit_label',
        existing_type=sa.Enum('Unidad', 'Bulto', 'Caja', 'Kg', 'Gramo', 'Arroba', 'Litro', 'Mililitro'),
        type_=sa.Enum('Unidad', 'Bulto', 'Caja', 'Kg', 'Gramo', 'Arroba', 'Litro', 'Mililitro', 'Onza'),
        existing_nullable=False,
        existing_server_default='Unidad',
    )


def downgrade():
    op.alter_column(
        'products',
        'unit_label',
        existing_type=sa.Enum('Unidad', 'Bulto', 'Caja', 'Kg', 'Gramo', 'Arroba', 'Litro', 'Mililitro', 'Onza'),
        type_=sa.Enum('Unidad', 'Bulto', 'Caja', 'Kg', 'Gramo', 'Arroba', 'Litro', 'Mililitro'),
        existing_nullable=False,
        existing_server_default='Unidad',
    )
