"""agregar reminder_sent_at a appointments y pet_vaccinations

Revision ID: f1a3c7e9b2d6
Revises: d8a2c6f4b9e3
Create Date: 2026-09-07 00:00:00.000000

Base para el job programado de recordatorios por correo (cita 24h antes,
vacuna por vencer) - un timestamp de "ya se mando este recordatorio" para
que `flask send-daily-reminders` no vuelva a mandar el mismo correo si se
corre mas de una vez el mismo dia. Sin backfill: NULL es el estado correcto
de arranque ("nunca se mando"), tanto para las filas ya existentes como
para una fila nueva despues de esta migracion.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f1a3c7e9b2d6'
down_revision = 'd8a2c6f4b9e3'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('appointments', sa.Column('reminder_sent_at', sa.DateTime(), nullable=True))
    op.add_column('pet_vaccinations', sa.Column('reminder_sent_at', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('pet_vaccinations', 'reminder_sent_at')
    op.drop_column('appointments', 'reminder_sent_at')
