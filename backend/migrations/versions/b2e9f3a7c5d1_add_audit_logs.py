"""agregar audit_logs

Revision ID: b2e9f3a7c5d1
Revises: a1f8d2c4b6e0
Create Date: 2026-08-20 00:00:00.000000

Auditoria (ultima pieza sin tabla del mapa original del panel, decision 17
en CLAUDE.md). Alcance amplio pedido por Juan Manuel: todas las acciones
relevantes en todos los modulos, filtrables por usuario y por modulo,
guardando solo la accion (sin diff de valores antes/despues).

`user_id` es SET NULL (mismo patron que registered_by/resolved_by), pero a
diferencia de esos casos se guarda ademas `user_name`/`user_email` como
snapshot de texto - el proposito de un log de auditoria es justamente
sobrevivir a que se borre la cuenta, a diferencia de un pago o una
devolucion donde perder la autoria es aceptable.

IMPORTANTE (lección del incidente de la migración de Devoluciones,
a1f8d2c4b6e0): todo ID/FK en mysql.BIGINT(unsigned=True) explícito, nunca
sa.BigInteger() (genera signed) - el esquema real es unsigned de punta a
punta y un mismatch signed/unsigned en un FK falla con error 1005.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = 'b2e9f3a7c5d1'
down_revision = 'a1f8d2c4b6e0'
branch_labels = None
depends_on = None

BIGINT_UNSIGNED = mysql.BIGINT(unsigned=True)


def upgrade():
    op.create_table(
        'audit_logs',
        sa.Column('id', BIGINT_UNSIGNED, primary_key=True, autoincrement=True),
        sa.Column('user_id', BIGINT_UNSIGNED, sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('user_name', sa.String(200), nullable=True),
        sa.Column('user_email', sa.String(255), nullable=True),
        sa.Column('module', sa.String(50), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=True),
        sa.Column('entity_id', BIGINT_UNSIGNED, nullable=True),
        sa.Column('description', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_module', 'audit_logs', ['module'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])


def downgrade():
    op.drop_index('ix_audit_logs_created_at', table_name='audit_logs')
    op.drop_index('ix_audit_logs_module', table_name='audit_logs')
    op.drop_index('ix_audit_logs_user_id', table_name='audit_logs')
    op.drop_table('audit_logs')
