from datetime import datetime

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models import User, Pqrs, SalesOrder, Appointment

client_notifications_bp = Blueprint('client_notifications', __name__)

# Estados que de verdad son "novedad" para el cliente - una cita/pedido
# recien creado en Pendiente es su propia accion, no algo que el negocio
# le informe.
NOTIFY_ORDER_STATUSES = {'Pagado', 'Entregado', 'Cancelado'}
NOTIFY_APPOINTMENT_STATUSES = {'Confirmada', 'Completada', 'Cancelada'}


def _unread_count(user):
    # Sin visita previa registrada, todo lo que ya exista cuenta como
    # nuevo - correcto para una cuenta recien creada (ver migracion
    # c4f9a2e6b8d1: las cuentas ya existentes se backfillearon a NOW()
    # para no mostrarles de golpe todo su historial como "sin leer").
    last_read = user.notifications_last_read_at or datetime(2000, 1, 1)

    pqrs_count = Pqrs.query.filter(
        Pqrs.user_id == user.id,
        Pqrs.responded_at.isnot(None),
        Pqrs.responded_at > last_read,
    ).count()

    order_count = SalesOrder.query.filter(
        SalesOrder.user_id == user.id,
        SalesOrder.status.in_(NOTIFY_ORDER_STATUSES),
        SalesOrder.updated_at > last_read,
    ).count()

    appointment_count = Appointment.query.filter(
        Appointment.owner_id == user.id,
        Appointment.status.in_(NOTIFY_APPOINTMENT_STATUSES),
        Appointment.updated_at > last_read,
    ).count()

    return pqrs_count + order_count + appointment_count


@client_notifications_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_summary():
    user = User.query.get_or_404(int(get_jwt_identity()))
    return jsonify({'unread': _unread_count(user)})


@client_notifications_bp.route('/read', methods=['POST'])
@jwt_required()
def mark_as_read():
    user = User.query.get_or_404(int(get_jwt_identity()))
    user.notifications_last_read_at = datetime.now()
    db.session.commit()
    return jsonify({'unread': 0})
