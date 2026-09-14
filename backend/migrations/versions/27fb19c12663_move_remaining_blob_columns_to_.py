"""move remaining blob columns to filesystem

Revision ID: 27fb19c12663
Revises: 98844a6c7cd8
Create Date: 2026-08-05 20:10:00.000000

Mismo patron aplicado a pets/pqrs (ver migracion 98844a6c7cd8), extendido
al resto de columnas binarias del esquema original: products.image,
product_images.image, medical_records.attachment, users.profile_image e
invoices.pdf_file. Todas estaban vacias o casi vacias y sin modelo/ruta
todavia escribiendo en ellas (excepto invoices.pdf_file, que ya tenia
una fila de prueba). invoices ya traia una columna pdf_path sin usar en
el diseno original — aqui se termina de aprovechar en vez de duplicarla.
"""
import os

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27fb19c12663'
down_revision = '98844a6c7cd8'
branch_labels = None
depends_on = None

UPLOADS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'uploads'))

EXTENSION_BY_MIME = {
    'image/jpeg': 'jpg',
    'image/png': 'png',
    'application/pdf': 'pdf',
}


def _extension_for(mime):
    return EXTENSION_BY_MIME.get(mime, 'bin')


def _migrate_blob_column(bind, table, id_col, blob_col, mime_col, path_col, subdir, name_prefix):
    target_dir = os.path.join(UPLOADS_DIR, subdir)
    os.makedirs(target_dir, exist_ok=True)
    rows = bind.execute(
        sa.text(f'SELECT {id_col}, {blob_col}, {mime_col} FROM {table} WHERE {blob_col} IS NOT NULL')
    )
    for row_id, blob, mime in rows:
        filename = f'{name_prefix}_{row_id}.{_extension_for(mime)}'
        with open(os.path.join(target_dir, filename), 'wb') as f:
            f.write(blob)
        bind.execute(
            sa.text(f'UPDATE {table} SET {path_col} = :path WHERE {id_col} = :id'),
            {'path': f'{subdir}/{filename}', 'id': row_id},
        )


def upgrade():
    bind = op.get_bind()

    op.add_column('products', sa.Column('image_path', sa.String(255), nullable=True))
    _migrate_blob_column(bind, 'products', 'id', 'image', 'image', 'image_path', 'products', 'product')
    op.drop_column('products', 'image')

    op.add_column('product_images', sa.Column('image_path', sa.String(255), nullable=True))
    _migrate_blob_column(
        bind, 'product_images', 'id', 'image', 'image_mime', 'image_path', 'product_images', 'product_image'
    )
    op.drop_column('product_images', 'image')
    op.alter_column('product_images', 'image_path', existing_type=sa.String(255), nullable=False)

    op.add_column('medical_records', sa.Column('attachment_path', sa.String(255), nullable=True))
    _migrate_blob_column(
        bind, 'medical_records', 'id', 'attachment', 'attachment_mime', 'attachment_path',
        'medical_records', 'medical_record',
    )
    op.drop_column('medical_records', 'attachment')

    op.add_column('users', sa.Column('profile_image_path', sa.String(255), nullable=True))
    _migrate_blob_column(
        bind, 'users', 'id', 'profile_image', 'profile_image', 'profile_image_path', 'users', 'user'
    )
    op.drop_column('users', 'profile_image')

    _migrate_blob_column(
        bind, 'invoices', 'id', 'pdf_file', 'pdf_mime', 'pdf_path', 'invoices', 'invoice'
    )
    op.drop_column('invoices', 'pdf_file')


def downgrade():
    op.add_column('products', sa.Column('image', sa.LargeBinary, nullable=True))
    op.add_column('product_images', sa.Column('image', sa.LargeBinary, nullable=True))
    op.add_column('medical_records', sa.Column('attachment', sa.LargeBinary, nullable=True))
    op.add_column('users', sa.Column('profile_image', sa.LargeBinary, nullable=True))
    op.add_column('invoices', sa.Column('pdf_file', sa.LargeBinary, nullable=True))

    op.drop_column('products', 'image_path')
    op.alter_column('product_images', 'image_path', existing_type=sa.String(255), nullable=True)
    op.drop_column('product_images', 'image_path')
    op.drop_column('medical_records', 'attachment_path')
    op.drop_column('users', 'profile_image_path')
    # invoices.pdf_path se deja intacto: ya existia en el diseno original
