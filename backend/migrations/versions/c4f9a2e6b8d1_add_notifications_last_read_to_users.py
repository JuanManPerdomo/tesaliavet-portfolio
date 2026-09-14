"""agregar notifications_last_read_at a users

Revision ID: c4f9a2e6b8d1
Revises: b7f1c3e8a2d4
Create Date: 2026-08-27 00:00:00.000000

Base para el "punto/numero rojo" de notificaciones del cliente en el
Navbar publico (mismo pedido que ya tenia el panel de personal, decision
51, pero mas simple: solo un timestamp de "ultima vez que revise" en vez
de una tabla de items marcados uno por uno - el cliente no necesita ver
que item especifico esta sin leer, solo si hay algo nuevo).

Backfill a NOW() para todos los usuarios existentes: evita que, el dia
del deploy, todo su historial de PQRS respondidas/pedidos/citas ya
resueltas aparezca de golpe como "no leido" (decision 7 - no se quiere
un numero que se sienta falso). Un usuario nuevo despues de esta
migracion arranca en NULL, que el backend trata como "todo es nuevo" -
correcto para una cuenta recien creada.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c4f9a2e6b8d1'
down_revision = 'b7f1c3e8a2d4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('notifications_last_read_at', sa.DateTime(), nullable=True))
    op.execute('UPDATE users SET notifications_last_read_at = NOW()')


def downgrade():
    op.drop_column('users', 'notifications_last_read_at')
