from flask import Blueprint, request, jsonify

from ..models import StockAlert
from ..auth.decorators import role_required

stock_alerts_bp = Blueprint('stock_alerts', __name__)

VALID_STATUS_FILTERS = {'Activa', 'Resuelta', 'all'}


def _alert_payload(alert):
    return {
        'id': alert.id,
        'productId': alert.product_id,
        'productName': alert.product.name if alert.product else None,
        'sku': alert.product.sku if alert.product else None,
        'unitLabel': alert.product.unit_label if alert.product else None,
        'currentStock': float(alert.current_stock),
        'minStock': float(alert.min_stock),
        'status': alert.status,
        'createdAt': alert.created_at.isoformat() if alert.created_at else None,
        'resolvedAt': alert.resolved_at.isoformat() if alert.resolved_at else None,
        'resolvedBy': (
            f'{alert.resolver.first_name} {alert.resolver.last_name}' if alert.resolver else None
        ),
    }


@stock_alerts_bp.route('', methods=['GET'])
@role_required('admin', 'bodeguero')
def list_stock_alerts():
    # stock_alerts se mantiene sincronizada sola desde products/routes.py
    # (_sync_stock_alert) cada vez que cambia el stock de un producto - este
    # endpoint es de solo lectura, no hay create/update/delete manual.
    status = request.args.get('status', 'Activa')
    query = StockAlert.query
    if status in ('Activa', 'Resuelta'):
        query = query.filter_by(status=status)
    # 'all' -> sin filtro

    alerts = query.order_by(StockAlert.created_at.desc()).all()
    return jsonify([_alert_payload(a) for a in alerts])
