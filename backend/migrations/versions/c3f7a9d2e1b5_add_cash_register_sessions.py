"""add cash_register_sessions

Revision ID: c3f7a9d2e1b5
Revises: b2e9f3a7c5d1
Create Date: 2026-08-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'c3f7a9d2e1b5'
down_revision = 'b2e9f3a7c5d1'
branch_labels = None
depends_on = None

BIGINT_UNSIGNED = mysql.BIGINT(unsigned=True)


def upgrade():
    op.create_table(
        'cash_register_sessions',
        sa.Column('id', BIGINT_UNSIGNED, primary_key=True, autoincrement=True),
        sa.Column('responsible_user_id', BIGINT_UNSIGNED, sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('status', sa.Enum('Abierta', 'Cerrada', name='cash_register_session_status'), nullable=False, server_default='Abierta'),
        sa.Column('opening_amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('opening_notes', sa.String(255), nullable=True),
        sa.Column('opened_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('counted_cash', sa.Numeric(12, 2), nullable=True),
        sa.Column('expected_cash', sa.Numeric(12, 2), nullable=True),
        sa.Column('cash_difference', sa.Numeric(12, 2), nullable=True),
        sa.Column('difference_justification', sa.String(255), nullable=True),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_cash_register_sessions_status', 'cash_register_sessions', ['status'])

    op.add_column(
        'payments',
        sa.Column('cash_register_session_id', BIGINT_UNSIGNED,
                  sa.ForeignKey('cash_register_sessions.id'), nullable=True),
    )
    op.add_column(
        'returns',
        sa.Column('cash_register_session_id', BIGINT_UNSIGNED,
                  sa.ForeignKey('cash_register_sessions.id'), nullable=True),
    )


def downgrade():
    op.drop_column('returns', 'cash_register_session_id')
    op.drop_column('payments', 'cash_register_session_id')
    op.drop_index('ix_cash_register_sessions_status', table_name='cash_register_sessions')
    op.drop_table('cash_register_sessions')
