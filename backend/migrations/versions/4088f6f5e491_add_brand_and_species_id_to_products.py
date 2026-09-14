"""add brand and species_id to products

Revision ID: 4088f6f5e491
Revises: f4083011328c
Create Date: 2026-08-03 21:00:40.003691

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = '4088f6f5e491'
down_revision = 'f4083011328c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('products', sa.Column('brand', sa.String(100), nullable=True))
    op.add_column('products', sa.Column('species_id', mysql.SMALLINT(unsigned=True), nullable=True))
    op.create_foreign_key(
        'fk_products_species', 'products', 'species', ['species_id'], ['id']
    )

    # Datos ilustrativos para los 3 productos de prueba existentes
    op.execute("UPDATE products SET brand = 'Genfar' WHERE sku = 'MED-001'")
    op.execute("UPDATE products SET brand = 'Royal Canin', species_id = 1 WHERE sku = 'ALI-001'")
    op.execute("UPDATE products SET brand = 'Bayer', species_id = 1 WHERE sku = 'ACC-001'")


def downgrade():
    op.drop_constraint('fk_products_species', 'products', type_='foreignkey')
    op.drop_column('products', 'species_id')
    op.drop_column('products', 'brand')
