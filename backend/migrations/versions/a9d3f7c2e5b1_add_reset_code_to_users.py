"""agregar codigo de recuperacion de 6 digitos a users

Revision ID: a9d3f7c2e5b1
Revises: f2a6c8e1d4b7
Create Date: 2026-08-23 00:00:00.000000

Reemplaza el enlace firmado (itsdangerous, decision 40) por un codigo
numerico de 6 digitos - pedido por Juan Manuel. El codigo se guarda
hasheado (mismo patron que password_hash, nunca en texto plano), con
vencimiento corto (10 min) y contador de intentos fallidos (bloquea tras 5,
obliga a pedir un codigo nuevo).
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a9d3f7c2e5b1'
down_revision = 'f2a6c8e1d4b7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('reset_code_hash', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('reset_code_expires_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('reset_code_attempts', sa.Integer(), nullable=False, server_default='0'))


def downgrade():
    op.drop_column('users', 'reset_code_attempts')
    op.drop_column('users', 'reset_code_expires_at')
    op.drop_column('users', 'reset_code_hash')
