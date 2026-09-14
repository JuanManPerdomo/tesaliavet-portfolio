"""agregar is_pharmacy a categories

Revision ID: b7f1c3e8a2d4
Revises: ead9ea991709
Create Date: 2026-08-27 00:00:00.000000

Antes "Farmacia Veterinaria" (AnimalCarePharmacy.vue) filtraba por una
lista fija de IDs (1=Medicamentos, 4=Antiparasitarios) escrita a mano en
el frontend. Se agrega esta columna para que el admin pueda marcar/
desmarcar categorias desde /panel/categorias sin tocar codigo - el
backfill mantiene el comportamiento actual exacto (esas mismas 2).
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b7f1c3e8a2d4'
down_revision = 'ead9ea991709'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'categories',
        sa.Column('is_pharmacy', sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.execute("UPDATE categories SET is_pharmacy = TRUE WHERE id IN (1, 4)")


def downgrade():
    op.drop_column('categories', 'is_pharmacy')
