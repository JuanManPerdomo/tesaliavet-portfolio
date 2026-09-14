from datetime import datetime, timedelta, date

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity

from ..extensions import db
from ..models import User, StockAlert, Pqrs, Appointment, SalesOrder, StaffNotificationRead, Pet
from ..auth.decorators import role_required
from ..pets.routes import _vet_patient_ids, _next_vaccine_reminder

notifications_bp = Blueprint('notifications', __name__)

VALID_TYPES = {'stock', 'pqrs', 'cita', 'compra', 'entrega', 'vacuna'}

# Una vacuna "requiere atencion" si ya vencio o vence dentro de esta ventana -
# lo mismo que RF pedía "vacunas por vencer", pero acotado a lo realmente
# urgente (una vacuna que vence en 3 meses no necesita aparecer en
# Atencion Requerida, para eso ya existe el widget "Vacunas por Vencer" del
# dashboard del veterinario, que sí muestra todas sin ventana de tiempo).
VACCINE_ATTENTION_WINDOW_DAYS = 7


def _current_user_id():
    return int(get_jwt_identity())


def _gather_notifications(user):
    """Notificaciones calculadas en vivo sobre las tablas reales (sin
    materializar nada) - mismo criterio que Atencion Requerida/Alertas de
    stock. Admin ve TODAS las fuentes (incluidas las de Bodeguero y
    veterinario, decision "Atencion Requerida + vacunas", 2026-09-02);
    Bodeguero solo Stock (su terreno real, decision Bodeguero 2026-09-02);
    veterinario puro solo Citas y Vacunas de sus propios pacientes - nunca
    Stock/PQRS/Pedidos, que son terreno de admin/bodeguero."""
    is_admin = any(r.name == 'admin' for r in user.roles)
    is_bodeguero = any(r.name == 'bodeguero' for r in user.roles)
    is_vet = any(r.name == 'veterinario' for r in user.roles)

    items = []

    if is_admin or is_bodeguero:
        for alert in StockAlert.query.filter_by(status='Activa').all():
            if not alert.product:
                continue
            items.append({
                'key': f'stock:{alert.id}',
                'type': 'stock',
                'title': f'Stock crítico: {alert.product.name}',
                'description': (
                    f'Quedan {float(alert.current_stock):g} {alert.product.unit_label} '
                    f'(mínimo {float(alert.min_stock):g}).'
                ),
                'createdAt': alert.created_at,
                'action': {'label': 'Ver producto', 'to': {'name': 'staff-product-edit', 'params': {'id': alert.product_id}}},
            })

    if is_admin:
        for pqrs in Pqrs.query.filter_by(status='Abierto').all():
            items.append({
                'key': f'pqrs:{pqrs.id}',
                'type': 'pqrs',
                'title': f'Nueva PQRS: {pqrs.subject}',
                'description': f'De {pqrs.sender_name} ({pqrs.type}).',
                'createdAt': pqrs.created_at,
                'action': {'label': 'Ver detalle PQRS', 'to': {'name': 'staff-pqrs-detail', 'params': {'id': pqrs.id}}},
            })

        for order in SalesOrder.query.filter_by(status='Pendiente').all():
            items.append({
                'key': f'order:{order.id}',
                'type': 'compra',
                'title': f'Pedido #{order.id} pendiente de pago',
                'description': f'{order.shipping_name} · $ {order.total:,.0f}'.replace(',', '.'),
                'createdAt': order.created_at,
                'action': {'label': 'Ver pedido', 'to': {'name': 'staff-order-detail', 'params': {'id': order.id}}},
            })

        # Pagado pero no Entregado - gap real señalado por Juan Manuel: antes
        # solo se avisaba de pedidos sin pagar, un pedido ya pagado esperando
        # entrega en tienda quedaba sin ningun aviso. Key propia
        # (order-delivery, no order:) para que no colisione con la de arriba
        # ni herede su estado de "leido" cuando un pedido pasa de una a otra.
        for order in SalesOrder.query.filter_by(status='Pagado').all():
            items.append({
                'key': f'order-delivery:{order.id}',
                'type': 'entrega',
                'title': f'Pedido #{order.id} pagado, pendiente de entrega',
                'description': f'{order.shipping_name} · $ {order.total:,.0f}'.replace(',', '.'),
                'createdAt': order.created_at,
                'action': {'label': 'Ver pedido', 'to': {'name': 'staff-order-detail', 'params': {'id': order.id}}},
            })

    appt_query = Appointment.query.filter_by(status='Pendiente')
    if not is_admin:
        appt_query = appt_query.filter_by(veterinarian_id=user.id)
    for appt in appt_query.all():
        if not appt.pet:
            continue
        items.append({
            'key': f'appointment:{appt.id}',
            'type': 'cita',
            'title': f'Cita pendiente: {appt.pet.name}',
            'description': f'{appt.owner.first_name} {appt.owner.last_name} · {appt.reason or "Sin motivo especificado"}',
            'createdAt': appt.created_at,
            'action': {'label': 'Ver cita', 'to': {'name': 'staff-appointment-detail', 'params': {'id': appt.id}}},
        })

    if is_admin or is_vet:
        # Mismos "pacientes" que el dashboard del veterinario (decision
        # "Panel del veterinario", 2026-09-02): admin ve vacunas de TODAS
        # las mascotas, veterinario puro solo de las suyas.
        vaccine_query = Pet.query.filter_by(is_active=True)
        if not is_admin:
            pet_ids = _vet_patient_ids(user)
            vaccine_query = vaccine_query.filter(Pet.id.in_(pet_ids)) if pet_ids else None

        if vaccine_query is not None:
            attention_cutoff = date.today() + timedelta(days=VACCINE_ATTENTION_WINDOW_DAYS)
            for pet in vaccine_query.all():
                reminder = _next_vaccine_reminder(pet)
                if not reminder:
                    continue
                due_date = datetime.strptime(reminder['nextDueDate'], '%Y-%m-%d').date()
                if due_date > attention_cutoff:
                    continue
                items.append({
                    'key': f'vaccine:{pet.id}',
                    'type': 'vacuna',
                    'title': f'Vacuna {"vencida" if reminder["isOverdue"] else "por vencer"}: {pet.name}',
                    'description': f'{reminder["vaccineName"]} · {reminder["nextDueDate"]}',
                    'createdAt': datetime.now(),
                    'action': {'label': 'Ver mascota', 'to': {'name': 'staff-pet-detail', 'params': {'id': pet.id}}},
                })

    read_keys = {
        r.notification_key
        for r in StaffNotificationRead.query.filter_by(user_id=user.id).all()
    }
    for item in items:
        item['read'] = item['key'] in read_keys

    items.sort(key=lambda i: i['createdAt'], reverse=True)
    return items


def _notification_payload(item):
    return {
        'key': item['key'],
        'type': item['type'],
        'title': item['title'],
        'description': item['description'],
        'createdAt': item['createdAt'].isoformat() if item['createdAt'] else None,
        'read': item['read'],
        'action': item['action'],
    }


@notifications_bp.route('', methods=['GET'])
@role_required('admin', 'veterinario', 'bodeguero')
def list_notifications():
    user = User.query.get(_current_user_id())
    items = _gather_notifications(user)

    notif_type = request.args.get('type')
    if notif_type in VALID_TYPES:
        items = [i for i in items if i['type'] == notif_type]

    read_filter = request.args.get('read')
    if read_filter == 'read':
        items = [i for i in items if i['read']]
    elif read_filter == 'unread':
        items = [i for i in items if not i['read']]

    search = request.args.get('search', '').strip().lower()
    if search:
        items = [i for i in items if search in i['title'].lower() or search in i['description'].lower()]

    date_from = request.args.get('dateFrom')
    if date_from:
        items = [i for i in items if i['createdAt'] and i['createdAt'].date() >= datetime.strptime(date_from, '%Y-%m-%d').date()]

    date_to = request.args.get('dateTo')
    if date_to:
        items = [i for i in items if i['createdAt'] and i['createdAt'].date() <= datetime.strptime(date_to, '%Y-%m-%d').date()]

    page = request.args.get('page', default=1, type=int)
    per_page = min(request.args.get('perPage', default=10, type=int), 100)
    total = len(items)
    pages = max((total + per_page - 1) // per_page, 1)
    start = (page - 1) * per_page
    page_items = items[start:start + per_page]

    return jsonify({
        'items': [_notification_payload(i) for i in page_items],
        'total': total,
        'page': page,
        'perPage': per_page,
        'pages': pages,
    })


@notifications_bp.route('/summary', methods=['GET'])
@role_required('admin', 'veterinario', 'bodeguero')
def get_summary():
    user = User.query.get(_current_user_id())
    items = _gather_notifications(user)

    today = datetime.now().date()
    by_type = {t: 0 for t in VALID_TYPES}
    for item in items:
        by_type[item['type']] += 1

    return jsonify({
        'total': len(items),
        'unread': sum(1 for i in items if not i['read']),
        'receivedToday': sum(1 for i in items if i['createdAt'] and i['createdAt'].date() == today),
        'byType': by_type,
    })


@notifications_bp.route('/read', methods=['POST'])
@role_required('admin', 'veterinario', 'bodeguero')
def mark_as_read():
    data = request.get_json(silent=True) or {}
    key = data.get('key')
    if not key:
        return jsonify({'message': 'La notificación es requerida'}), 400

    uid = _current_user_id()
    existing = StaffNotificationRead.query.filter_by(user_id=uid, notification_key=key).first()
    if not existing:
        db.session.add(StaffNotificationRead(user_id=uid, notification_key=key))
        db.session.commit()

    return get_summary()
