from flask import Blueprint, request, jsonify
from sqlalchemy import or_

from ..models import AuditLog, User, Role
from ..auth.decorators import role_required

audit_bp = Blueprint('audit', __name__)

# Auditoria muestra solo actividad del personal (admin/veterinario/
# bodeguero), nunca de clientes - pedido explicito de Juan Manuel
# (2026-09-02): antes "Sesión" (login/logout) y el registro de una cuenta
# nueva se guardaban para CUALQUIER usuario, incluidos clientes comprando
# en la tienda, mezclados con la actividad real del personal.
STAFF_ROLES = ('admin', 'veterinario', 'bodeguero')


def _staff_only_filter():
    # user_id NULL = cuenta ya borrada (SET NULL, decision 44) - se deja
    # pasar a proposito: no hay forma de saber que rol tenia, y el
    # proposito del snapshot es sobrevivir al borrado, no perder ese
    # historial. Solo se excluye a un usuario que TODAVIA existe y cuyo
    # unico rol es 'cliente' (o ninguno).
    return or_(
        AuditLog.user_id.is_(None),
        AuditLog.user.has(User.roles.any(Role.name.in_(STAFF_ROLES))),
    )


def _log_payload(log):
    return {
        'id': log.id,
        'userId': log.user_id,
        'userName': log.user_name,
        'userEmail': log.user_email,
        'module': log.module,
        'action': log.action,
        'entityType': log.entity_type,
        'entityId': log.entity_id,
        'description': log.description,
        'changes': log.changes or [],
        'createdAt': log.created_at.isoformat() if log.created_at else None,
    }


@audit_bp.route('', methods=['GET'])
@role_required('admin')
def list_logs():
    query = AuditLog.query.filter(_staff_only_filter())

    user_id = request.args.get('userId', type=int)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)

    module = request.args.get('module')
    if module:
        query = query.filter(AuditLog.module == module)

    action = request.args.get('action')
    if action:
        query = query.filter(AuditLog.action == action)

    date_from = request.args.get('dateFrom')
    if date_from:
        query = query.filter(AuditLog.created_at >= date_from)

    date_to = request.args.get('dateTo')
    if date_to:
        query = query.filter(AuditLog.created_at < f'{date_to} 23:59:59')

    query = query.order_by(AuditLog.created_at.desc())

    page = request.args.get('page', default=1, type=int)
    per_page = min(request.args.get('perPage', default=20, type=int), 100)
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items': [_log_payload(log) for log in paginated.items],
        'total': paginated.total,
        'page': paginated.page,
        'perPage': paginated.per_page,
        'pages': paginated.pages,
    })


@audit_bp.route('/users', methods=['GET'])
@role_required('admin')
def list_logged_users():
    # Solo usuarios que de verdad tienen entradas - no tiene sentido ofrecer
    # en el filtro a alguien que nunca hizo nada auditable. Mismo filtro de
    # "solo personal" que list_logs, para no ofrecer en el desplegable a un
    # cliente cuyas entradas de todos modos no se van a mostrar.
    rows = (
        AuditLog.query.with_entities(AuditLog.user_id, AuditLog.user_name, AuditLog.user_email)
        .filter(AuditLog.user_id.isnot(None))
        .filter(_staff_only_filter())
        .distinct()
        .all()
    )
    seen = {}
    for user_id, name, email in rows:
        seen[user_id] = {'id': user_id, 'name': name, 'email': email}
    return jsonify(sorted(seen.values(), key=lambda u: u['name'] or ''))
