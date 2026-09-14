"""agregar staff_notification_reads

Revision ID: e7c4a1f9b3d6
Revises: d4e8b1a9c2f0
Create Date: 2026-08-21 00:00:00.000000

Centro de Notificaciones del personal (decision 51 en CLAUDE.md). Sin
tabla de "notificaciones" materializada - cada notificacion se calcula en
vivo sobre stock_alerts/pqrs/appointments/sales_orders (mismo criterio que
Atencion Requerida/Alertas de stock). Lo unico que se persiste es el
estado de lectura por usuario: notification_key es un string estable tipo
"stock:14"/"pqrs:9" (prefijo de tipo + id real de la fila fuente).

mysql.BIGINT(unsigned=True) explicito en id/user_id, nunca sa.BigInteger()
(regla de la decision 42/44/46/49 - el esquema real es unsigned de punta a
punta).
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = 'e7c4a1f9b3d6'
down_revision = 'd4e8b1a9c2f0'
branch_labels = None
depends_on = None

BIGINT_UNSIGNED = mysql.BIGINT(unsigned=True)


def upgrade():
    op.create_table(
        'staff_notification_reads',
        sa.Column('id', BIGINT_UNSIGNED, primary_key=True, autoincrement=True),
        sa.Column('user_id', BIGINT_UNSIGNED, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('notification_key', sa.String(64), nullable=False),
        sa.Column('read_at', sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint('user_id', 'notification_key', name='uq_staff_notification_read'),
    )
    op.create_index('ix_staff_notification_reads_user_id', 'staff_notification_reads', ['user_id'])


def downgrade():
    op.drop_index('ix_staff_notification_reads_user_id', table_name='staff_notification_reads')
    op.drop_table('staff_notification_reads')
