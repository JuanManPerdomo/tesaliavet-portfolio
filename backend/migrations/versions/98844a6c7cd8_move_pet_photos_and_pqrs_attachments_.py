"""move pet photos and pqrs attachments from blob to filesystem

Revision ID: 98844a6c7cd8
Revises: 4088f6f5e491
Create Date: 2026-08-05 19:20:00.000000

Guardar imagenes/adjuntos como BLOB en MySQL infla la BD y los backups
sin necesidad. Se mueven a archivos en backend/uploads/ y las columnas
pasan de LONGBLOB a un VARCHAR con la ruta relativa del archivo.
"""
import os

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '98844a6c7cd8'
down_revision = '4088f6f5e491'
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


def upgrade():
    bind = op.get_bind()

    op.add_column('pets', sa.Column('image_path', sa.String(255), nullable=True))
    op.add_column('pqrs', sa.Column('attachment_path', sa.String(255), nullable=True))

    pets_dir = os.path.join(UPLOADS_DIR, 'pets')
    os.makedirs(pets_dir, exist_ok=True)
    for pet_id, image, image_mime in bind.execute(
        sa.text('SELECT id, image, image_mime FROM pets WHERE image IS NOT NULL')
    ):
        filename = f'pet_{pet_id}.{_extension_for(image_mime)}'
        with open(os.path.join(pets_dir, filename), 'wb') as f:
            f.write(image)
        bind.execute(
            sa.text('UPDATE pets SET image_path = :path WHERE id = :id'),
            {'path': f'pets/{filename}', 'id': pet_id},
        )

    pqrs_dir = os.path.join(UPLOADS_DIR, 'pqrs')
    os.makedirs(pqrs_dir, exist_ok=True)
    for pqrs_id, attachment, attachment_mime in bind.execute(
        sa.text('SELECT id, attachment, attachment_mime FROM pqrs WHERE attachment IS NOT NULL')
    ):
        filename = f'pqrs_{pqrs_id}.{_extension_for(attachment_mime)}'
        with open(os.path.join(pqrs_dir, filename), 'wb') as f:
            f.write(attachment)
        bind.execute(
            sa.text('UPDATE pqrs SET attachment_path = :path WHERE id = :id'),
            {'path': f'pqrs/{filename}', 'id': pqrs_id},
        )

    op.drop_column('pets', 'image')
    op.drop_column('pqrs', 'attachment')


def downgrade():
    op.add_column('pets', sa.Column('image', sa.LargeBinary, nullable=True))
    op.add_column('pqrs', sa.Column('attachment', sa.LargeBinary, nullable=True))

    bind = op.get_bind()
    for pet_id, image_path in bind.execute(
        sa.text('SELECT id, image_path FROM pets WHERE image_path IS NOT NULL')
    ):
        full_path = os.path.join(UPLOADS_DIR, image_path)
        if os.path.exists(full_path):
            with open(full_path, 'rb') as f:
                bind.execute(
                    sa.text('UPDATE pets SET image = :image WHERE id = :id'),
                    {'image': f.read(), 'id': pet_id},
                )

    for pqrs_id, attachment_path in bind.execute(
        sa.text('SELECT id, attachment_path FROM pqrs WHERE attachment_path IS NOT NULL')
    ):
        full_path = os.path.join(UPLOADS_DIR, attachment_path)
        if os.path.exists(full_path):
            with open(full_path, 'rb') as f:
                bind.execute(
                    sa.text('UPDATE pqrs SET attachment = :attachment WHERE id = :id'),
                    {'attachment': f.read(), 'id': pqrs_id},
                )

    op.drop_column('pets', 'image_path')
    op.drop_column('pqrs', 'attachment_path')
