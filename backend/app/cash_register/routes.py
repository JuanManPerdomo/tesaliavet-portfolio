from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity

from ..extensions import db
from ..models import CashRegisterSession, User
from ..auth.decorators import role_required
from ..audit.service import diff_snapshot, log_audit, snapshot_fields
from .service import get_open_session

cash_register_bp = Blueprint('cash_register', __name__)


def _session_totals(session):
    # Solo Efectivo/Transferencia son metodos reales del negocio (decision 28: sin
    # datafono, Tarjeta nunca se uso) - el cuadre fisico solo aplica al efectivo, las
    # transferencias no estan fisicamente en la caja.
    payments_efectivo = sum(
        (p.amount for p in session.payments if p.payment_method == 'Efectivo'), Decimal('0')
    )
    payments_transferencia = sum(
        (p.amount for p in session.payments if p.payment_method == 'Transferencia'), Decimal('0')
    )
    returns_efectivo = sum(
        (r.refund_amount for r in session.returns if r.refund_method == 'Efectivo'), Decimal('0')
    )
    returns_transferencia = sum(
        (r.refund_amount for r in session.returns if r.refund_method == 'Transferencia'), Decimal('0')
    )
    net_efectivo = payments_efectivo - returns_efectivo
    net_transferencia = payments_transferencia - returns_transferencia
    return {
        'paymentsEfectivo': float(payments_efectivo),
        'paymentsTransferencia': float(payments_transferencia),
        'returnsEfectivo': float(returns_efectivo),
        'returnsTransferencia': float(returns_transferencia),
        'netEfectivo': float(net_efectivo),
        'netTransferencia': float(net_transferencia),
        # Total recaudado NO incluye el fondo base - el fondo base es el vuelto
        # inicial, no dinero que haya entrado por ventas de este turno.
        'totalRecaudado': float(net_efectivo + net_transferencia),
        # Efectivo que deberia haber fisicamente en la caja ahora mismo (o al
        # momento del cierre, si ya esta cerrada y se uso para el snapshot).
        'expectedCashLive': float(session.opening_amount + net_efectivo),
        'paymentsCount': len(session.payments),
        'returnsCount': len(session.returns),
    }


def _session_movements(session):
    entries = []
    for p in session.payments:
        entries.append({
            'kind': 'in',
            'id': p.id,
            'orderId': p.invoice.order_id if p.invoice else None,
            'invoiceNumber': p.invoice.invoice_number if p.invoice else None,
            'amount': float(p.amount),
            'method': p.payment_method,
            'time': p.paid_at.isoformat() if p.paid_at else None,
        })
    for r in session.returns:
        entries.append({
            'kind': 'out',
            'id': r.id,
            'orderId': r.order_id,
            'reason': r.reason,
            'amount': float(r.refund_amount),
            'method': r.refund_method,
            'time': r.created_at.isoformat() if r.created_at else None,
        })
    entries.sort(key=lambda e: e['time'] or '')
    return entries


def _session_payload(session, include_movements=False):
    payload = {
        'id': session.id,
        'status': session.status,
        'responsibleUserId': session.responsible_user_id,
        'responsibleUserName': (
            f'{session.responsible_user.first_name} {session.responsible_user.last_name}'
            if session.responsible_user else None
        ),
        'openingAmount': float(session.opening_amount),
        'openingNotes': session.opening_notes,
        'openedAt': session.opened_at.isoformat() if session.opened_at else None,
        'countedCash': float(session.counted_cash) if session.counted_cash is not None else None,
        'expectedCash': float(session.expected_cash) if session.expected_cash is not None else None,
        'cashDifference': float(session.cash_difference) if session.cash_difference is not None else None,
        'differenceJustification': session.difference_justification,
        'closedAt': session.closed_at.isoformat() if session.closed_at else None,
        'totals': _session_totals(session),
    }
    if include_movements:
        payload['movements'] = _session_movements(session)
    return payload


@cash_register_bp.route('/current', methods=['GET'])
@role_required('admin', 'bodeguero')
def get_current_session():
    session = get_open_session()
    if not session:
        return jsonify({'session': None})
    return jsonify({'session': _session_payload(session, include_movements=True)})


@cash_register_bp.route('/open', methods=['POST'])
@role_required('admin', 'bodeguero')
def open_session():
    if get_open_session():
        return jsonify({'message': 'Ya hay una caja abierta'}), 400

    data = request.get_json(silent=True) or {}

    # El responsable es siempre quien abre la caja - no es elegible por el
    # usuario (riesgo de seguridad/auditoria: cualquiera podria asignarsela a
    # otra persona por error o a proposito). Ya esta garantizado que es admin
    # por el @role_required de arriba.
    responsible = User.query.get(int(get_jwt_identity()))

    try:
        opening_amount = Decimal(str(data.get('openingAmount')))
    except (InvalidOperation, TypeError):
        return jsonify({'message': 'El monto base es requerido'}), 400
    if opening_amount < 0:
        return jsonify({'message': 'El monto base no puede ser negativo'}), 400

    session = CashRegisterSession(
        responsible_user_id=responsible.id,
        opening_amount=opening_amount,
        opening_notes=(data.get('notes') or '').strip() or None,
        status='Abierta',
    )
    db.session.add(session)
    db.session.flush()  # asigna session.id para el log de auditoria

    log_audit(
        int(get_jwt_identity()), 'Caja', 'open_session',
        f'Abrió la caja #{session.id} (base $ {opening_amount:,.0f}, responsable: '
        f'{responsible.first_name} {responsible.last_name})',
        entity_type='cash_register_session', entity_id=session.id,
    )
    db.session.commit()
    return jsonify(_session_payload(session)), 201


@cash_register_bp.route('/<int:session_id>/close', methods=['PUT'])
@role_required('admin', 'bodeguero')
def close_session(session_id):
    session = CashRegisterSession.query.get_or_404(session_id)
    before = snapshot_fields(session)
    if session.status != 'Abierta':
        return jsonify({'message': 'Esta caja ya está cerrada'}), 400

    # Solo quien la abrió (responsible_user_id) o un admin puede cerrarla -
    # antes cualquier admin/bodeguero podía cerrar la caja de otra persona
    # sin restricción (gap real señalado por Juan Manuel, 2026-09-02).
    current_user_id = int(get_jwt_identity())
    if session.responsible_user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        is_admin = bool(current_user) and any(r.name == 'admin' for r in current_user.roles)
        if not is_admin:
            return jsonify({'message': 'Solo quien abrió esta caja o un administrador puede cerrarla'}), 403

    data = request.get_json(silent=True) or {}
    try:
        counted_cash = Decimal(str(data.get('countedCash')))
    except (InvalidOperation, TypeError):
        return jsonify({'message': 'El efectivo contado es requerido'}), 400
    if counted_cash < 0:
        return jsonify({'message': 'El efectivo contado no puede ser negativo'}), 400

    totals = _session_totals(session)
    expected_cash = Decimal(str(totals['expectedCashLive']))
    difference = counted_cash - expected_cash

    justification = (data.get('justification') or '').strip()
    if difference != 0 and not justification:
        return jsonify({'message': 'La diferencia de cuadre requiere una justificación'}), 400

    session.counted_cash = counted_cash
    session.expected_cash = expected_cash
    session.cash_difference = difference
    session.difference_justification = justification or None
    session.status = 'Cerrada'
    session.closed_at = datetime.now()

    log_audit(
        int(get_jwt_identity()), 'Caja', 'close_session',
        f'Cerró la caja #{session.id} (recaudado $ {totals["totalRecaudado"]:,.0f}, '
        f'diferencia $ {difference:,.0f})',
        entity_type='cash_register_session', entity_id=session.id, changes=diff_snapshot(session, before),
    )
    db.session.commit()
    return jsonify(_session_payload(session, include_movements=True))


@cash_register_bp.route('/sessions', methods=['GET'])
@role_required('admin', 'bodeguero')
def list_sessions():
    query = CashRegisterSession.query.order_by(CashRegisterSession.opened_at.desc())

    page = request.args.get('page', default=1, type=int)
    per_page = min(request.args.get('per_page', default=10, type=int), 100)
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'sessions': [_session_payload(s) for s in paginated.items],
        'total': paginated.total,
        'page': paginated.page,
        'per_page': paginated.per_page,
        'pages': paginated.pages,
    })


@cash_register_bp.route('/sessions/<int:session_id>', methods=['GET'])
@role_required('admin', 'bodeguero')
def get_session_detail(session_id):
    session = CashRegisterSession.query.get_or_404(session_id)
    return jsonify(_session_payload(session, include_movements=True))
