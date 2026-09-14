import os
from datetime import datetime

from flask import Blueprint, request, jsonify, current_app, send_file, abort
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import or_

from ..extensions import db
from ..models import Pqrs
from ..auth.decorators import role_required
from ..audit.service import diff_snapshot, log_audit, snapshot_fields
from .mailer import send_pqrs_responded

pqrs_bp = Blueprint('pqrs', __name__)

TYPE_MAP = {
    'peticion': 'Peticion',
    'queja': 'Queja',
    'reclamo': 'Reclamo',
    'sugerencia': 'Sugerencia',
}

VALID_STATUSES = {'Abierto', 'En Proceso', 'Resuelto', 'Cerrado'}


def _pqrs_payload(pqrs):
    return {
        'id': pqrs.id,
        'senderName': pqrs.sender_name,
        'senderEmail': pqrs.sender_email,
        'senderPhone': pqrs.sender_phone,
        'type': pqrs.type,
        'subject': pqrs.subject,
        'message': pqrs.message,
        'status': pqrs.status,
        'response': pqrs.response,
        'respondedBy': (
            f'{pqrs.responder.first_name} {pqrs.responder.last_name}' if pqrs.responder else None
        ),
        'attachmentUrl': f'/pqrs/{pqrs.id}/attachment' if pqrs.attachment_path else None,
        'createdAt': pqrs.created_at.isoformat() if pqrs.created_at else None,
        'respondedAt': pqrs.responded_at.isoformat() if pqrs.responded_at else None,
    }

ALLOWED_ATTACHMENT_TYPES = {'application/pdf', 'image/jpeg', 'image/png'}
EXTENSION_BY_MIME = {'application/pdf': 'pdf', 'image/jpeg': 'jpg', 'image/png': 'png'}
MAX_ATTACHMENT_SIZE = 5 * 1024 * 1024  # 5MB


def _save_pqrs_attachment(pqrs, attachment_file):
    content = attachment_file.read()
    valid_type = attachment_file.mimetype in ALLOWED_ATTACHMENT_TYPES
    valid_size = len(content) <= MAX_ATTACHMENT_SIZE
    if not (valid_type and valid_size):
        return False

    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'pqrs')
    os.makedirs(upload_dir, exist_ok=True)

    filename = f'pqrs_{pqrs.id}.{EXTENSION_BY_MIME[attachment_file.mimetype]}'
    with open(os.path.join(upload_dir, filename), 'wb') as f:
        f.write(content)

    pqrs.attachment_path = f'pqrs/{filename}'
    pqrs.attachment_mime = attachment_file.mimetype
    return True


@pqrs_bp.route('', methods=['POST'])
@role_required('cliente')
def create_pqrs():
    is_multipart = (request.content_type or '').startswith('multipart/form-data')
    data = request.form if is_multipart else (request.get_json(silent=True) or {})
    attachment_file = request.files.get('attachment') if is_multipart else None

    required = ['type', 'subject', 'message', 'senderName', 'senderEmail']
    missing = [field for field in required if not data.get(field)]
    if missing:
        return jsonify({'message': f'Faltan campos requeridos: {", ".join(missing)}'}), 400

    pqrs_type = TYPE_MAP.get(data['type'])
    if not pqrs_type:
        return jsonify({'message': 'Tipo de solicitud inválido'}), 400

    pqrs = Pqrs(
        user_id=int(get_jwt_identity()),
        sender_name=data['senderName'],
        sender_email=data['senderEmail'],
        sender_phone=data.get('senderPhone'),
        type=pqrs_type,
        subject=data['subject'],
        message=data['message'],
    )

    db.session.add(pqrs)
    db.session.flush()  # asigna pqrs.id, necesario para el nombre del archivo adjunto

    attachment_saved = False
    if attachment_file and attachment_file.filename:
        # Si no cumple formato o peso, simplemente no se adjunta -
        # la solicitud PQRS se sigue creando con normalidad.
        attachment_saved = _save_pqrs_attachment(pqrs, attachment_file)

    db.session.commit()

    return jsonify({'id': pqrs.id, 'status': pqrs.status, 'attachmentSaved': attachment_saved}), 201


@pqrs_bp.route('/mine', methods=['GET'])
@jwt_required()
def list_my_pqrs():
    # Solo las que se enviaron con sesion iniciada (user_id se guarda al
    # crear, decision 5/32) - una PQRS enviada como invitado antes de
    # loguearse no aparece aca, es el comportamiento correcto.
    user_id = int(get_jwt_identity())
    items = Pqrs.query.filter_by(user_id=user_id).order_by(Pqrs.created_at.desc()).all()
    return jsonify([_pqrs_payload(p) for p in items])


@pqrs_bp.route('', methods=['GET'])
@role_required('admin')
def list_pqrs():
    query = Pqrs.query
    status = request.args.get('status')
    if status:
        if status not in VALID_STATUSES:
            return jsonify({'message': 'Estado inválido'}), 400
        query = query.filter_by(status=status)

    search = request.args.get('search')
    if search:
        like = f'%{search}%'
        query = query.filter(or_(
            Pqrs.subject.ilike(like),
            Pqrs.sender_name.ilike(like),
            Pqrs.sender_email.ilike(like),
        ))

    query = query.order_by(Pqrs.created_at.desc())

    page = request.args.get('page', default=1, type=int)
    per_page = min(request.args.get('perPage', default=10, type=int), 100)
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items': [_pqrs_payload(p) for p in paginated.items],
        'total': paginated.total,
        'page': paginated.page,
        'perPage': paginated.per_page,
        'pages': paginated.pages,
    })


@pqrs_bp.route('/<int:pqrs_id>', methods=['GET'])
@role_required('admin')
def get_pqrs(pqrs_id):
    pqrs = Pqrs.query.get_or_404(pqrs_id)
    return jsonify(_pqrs_payload(pqrs))


@pqrs_bp.route('/<int:pqrs_id>/respond', methods=['PUT'])
@role_required('admin')
def respond_pqrs(pqrs_id):
    pqrs = Pqrs.query.get_or_404(pqrs_id)
    before = snapshot_fields(pqrs)

    # "Cerrado" es un estado final de verdad - una vez ahí no se puede volver
    # a responder ni cambiar de estado desde este endpoint (mismo criterio que
    # Ordenes de compra, decision 31). Para seguir trabajandola hay que
    # reabrirla primero via /reopen, una accion explicita y separada.
    if pqrs.status == 'Cerrado':
        return jsonify({'message': 'La PQRS está cerrada. Reábrela antes de responder.'}), 400

    data = request.get_json(silent=True) or {}

    if not data.get('response'):
        return jsonify({'message': 'La respuesta es requerida'}), 400

    status = data.get('status', 'Resuelto')
    if status not in VALID_STATUSES:
        return jsonify({'message': 'Estado inválido'}), 400

    pqrs.response = data['response']
    pqrs.status = status
    pqrs.responded_by = int(get_jwt_identity())
    pqrs.responded_at = datetime.now()

    log_audit(
        int(get_jwt_identity()), 'PQRS', 'respond',
        f'Respondió la PQRS #{pqrs.id} ("{pqrs.subject}") con estado "{status}"',
        entity_type='pqrs', entity_id=pqrs.id, changes=diff_snapshot(pqrs, before),
    )
    db.session.commit()
    send_pqrs_responded(pqrs)
    return jsonify(_pqrs_payload(pqrs))


@pqrs_bp.route('/<int:pqrs_id>/reopen', methods=['PUT'])
@role_required('admin')
def reopen_pqrs(pqrs_id):
    pqrs = Pqrs.query.get_or_404(pqrs_id)
    before = snapshot_fields(pqrs)

    if pqrs.status != 'Cerrado':
        return jsonify({'message': 'Solo se puede reabrir una PQRS cerrada'}), 400

    pqrs.status = 'En Proceso'

    log_audit(
        int(get_jwt_identity()), 'PQRS', 'reopen',
        f'Reabrió la PQRS #{pqrs.id} ("{pqrs.subject}")',
        entity_type='pqrs', entity_id=pqrs.id, changes=diff_snapshot(pqrs, before),
    )
    db.session.commit()
    return jsonify(_pqrs_payload(pqrs))


@pqrs_bp.route('/<int:pqrs_id>/attachment', methods=['GET'])
@role_required('admin')
def get_pqrs_attachment(pqrs_id):
    pqrs = Pqrs.query.get_or_404(pqrs_id)
    if not pqrs.attachment_path:
        abort(404)
    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], pqrs.attachment_path)
    if not os.path.exists(full_path):
        abort(404)
    return send_file(full_path, mimetype=pqrs.attachment_mime or 'application/pdf')
