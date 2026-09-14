"""add category_id to species

Revision ID: ed625001e600
Revises: 27fb19c12663
Create Date: 2026-08-07 00:11:29.902493

Enlaza species con la categoria padre (Mascotas/Ganaderia, ver decision 19)
para que el formulario de productos pueda filtrar la especie segun la
categoria elegida. Perro/Gato quedan bajo Mascotas; se agregan 6 especies
de ganaderia bajo Ganaderia (catalogo no existia todavia).
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = 'ed625001e600'
down_revision = '27fb19c12663'
branch_labels = None
depends_on = None

LIVESTOCK_SPECIES = ['Bovino', 'Porcino', 'Equino', 'Ovino', 'Caprino', 'Aves']


def upgrade():
    op.add_column('species', sa.Column('category_id', mysql.SMALLINT(unsigned=True), nullable=True))
    op.create_foreign_key(
        'fk_species_category', 'species', 'categories', ['category_id'], ['id']
    )

    op.execute("""
        UPDATE species
        SET category_id = (SELECT id FROM categories WHERE name = 'Mascotas')
        WHERE name IN ('Perro', 'Gato')
    """)

    connection = op.get_bind()
    ganaderia_id = connection.execute(
        sa.text("SELECT id FROM categories WHERE name = 'Ganadería'")
    ).scalar()

    for name in LIVESTOCK_SPECIES:
        connection.execute(
            sa.text('INSERT INTO species (name, category_id) VALUES (:name, :category_id)'),
            {'name': name, 'category_id': ganaderia_id},
        )


def downgrade():
    op.execute(f"DELETE FROM species WHERE name IN ({','.join(repr(n) for n in LIVESTOCK_SPECIES)})")
    op.drop_constraint('fk_species_category', 'species', type_='foreignkey')
    op.drop_column('species', 'category_id')
