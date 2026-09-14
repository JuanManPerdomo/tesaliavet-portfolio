"""add departamento to users

Revision ID: d4e8b1a9c2f0
Revises: c3f7a9d2e1b5
Create Date: 2026-08-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd4e8b1a9c2f0'
down_revision = 'c3f7a9d2e1b5'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('departamento', sa.String(100), nullable=True))


def downgrade():
    op.drop_column('users', 'departamento')
