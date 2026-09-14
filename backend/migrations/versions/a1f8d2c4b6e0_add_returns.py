"""agregar devoluciones (returns/return_items) y sales_orders.delivered_at

Revision ID: a1f8d2c4b6e0
Revises: 91c130a74ca8
Create Date: 2026-08-18 00:00:00.000000

Devoluciones (decision del roadmap del panel, ver CLAUDE.md) - a diferencia
de Carrito y checkout, el esquema original nunca tuvo tabla para esto, asi
que se disena desde cero. Reglas de negocio reales acordadas con Juan
Manuel antes de escribir esto: devolucion parcial (no siempre el pedido
completo), plazo real de 8 dias desde la entrega, y solo admin la
registra - el acto de registrarla ya es la aprobacion, sin flujo de
revision aparte (misma logica que "registrar pago").

`sales_orders.delivered_at` es necesario para validar el plazo de 8 dias
de verdad: `updated_at` no sirve porque se pisa con cualquier cambio del
pedido (registrar pago, por ejemplo), no solo con la entrega. Backfill:
los pedidos que ya estan 'Entregado' se aproximan con su `updated_at`
actual (no hay forma de saber la fecha real de entrega retroactivamente
sin inventarla).

`return_items.amount` se calcula en Python al crear la devolucion
(quantity * unit_price * (1 + tax_rate/100), mismo calculo que
sales_order_items.total) - a diferencia de esa tabla, aca no hace falta
una columna GENERATED porque es una tabla nueva sin ese patron heredado.

IMPORTANTE: todas las columnas BIGINT del esquema real son
`bigint(20) unsigned` (verificado con SHOW COLUMNS) - un FK contra una
columna signed vs. unsigned falla con error 1005 "Foreign key constraint
is incorrectly formed" en MySQL, asi que aca se usa
mysql.BIGINT(unsigned=True) explicito en vez de sa.BigInteger() (que
genera signed) en cualquier columna que sea PK o FK.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = 'a1f8d2c4b6e0'
down_revision = '91c130a74ca8'
branch_labels = None
depends_on = None

BIGINT_UNSIGNED = mysql.BIGINT(unsigned=True)


def upgrade():
    op.add_column('sales_orders', sa.Column('delivered_at', sa.DateTime(), nullable=True))
    op.execute("UPDATE sales_orders SET delivered_at = updated_at WHERE status = 'Entregado'")

    op.create_table(
        'returns',
        sa.Column('id', BIGINT_UNSIGNED, primary_key=True, autoincrement=True),
        sa.Column('order_id', BIGINT_UNSIGNED, sa.ForeignKey('sales_orders.id'), nullable=False),
        sa.Column('registered_by', BIGINT_UNSIGNED, sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('reason', sa.String(255), nullable=False),
        sa.Column('refund_method', sa.Enum('Efectivo', 'Transferencia', name='return_refund_method'), nullable=False),
        sa.Column('refund_reference', sa.String(100), nullable=True),
        sa.Column('refund_amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        'return_items',
        sa.Column('id', BIGINT_UNSIGNED, primary_key=True, autoincrement=True),
        sa.Column('return_id', BIGINT_UNSIGNED, sa.ForeignKey('returns.id', ondelete='CASCADE'), nullable=False),
        sa.Column(
            'sales_order_item_id', BIGINT_UNSIGNED, sa.ForeignKey('sales_order_items.id'), nullable=False
        ),
        sa.Column('product_id', BIGINT_UNSIGNED, sa.ForeignKey('products.id'), nullable=False),
        sa.Column('quantity', sa.Numeric(10, 2), nullable=False),
        sa.Column('unit_price', sa.Numeric(12, 2), nullable=False),
        sa.Column('tax_rate', sa.Numeric(5, 2), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('return_items')
    op.drop_table('returns')
    op.drop_column('sales_orders', 'delivered_at')
