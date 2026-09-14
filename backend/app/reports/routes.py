from datetime import datetime, timedelta
from decimal import Decimal

from flask import Blueprint, request, jsonify, Response
from sqlalchemy import func, extract, or_

from ..extensions import db
from ..models import (
    Product, Invoice, Payment, Return, SalesOrder, SalesOrderItem,
    Appointment, User, Role, CashRegisterSession,
)
from ..auth.decorators import role_required
from ..orders.routes import _net_income_between, _percent_change, _month_bounds, MONTH_LABELS
from ..cash_register.routes import _session_payload
from ..cash_register.service import get_open_session
from ..staff.routes import _client_query
from ..products.routes import _product_payload
from .exporters import build_csv, build_pdf

reports_bp = Blueprint('reports', __name__)

VALID_FORMATS = {'csv', 'pdf'}


def _parse_date_range():
    """Sin fechas, default al mes actual (no una pantalla vacia)."""
    date_from = request.args.get('dateFrom')
    date_to = request.args.get('dateTo')
    now = datetime.now()
    if date_from:
        start = datetime.strptime(date_from, '%Y-%m-%d')
    else:
        start = datetime(now.year, now.month, 1)
    if date_to:
        end = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
    else:
        end = datetime(now.year, now.month, now.day) + timedelta(days=1)
    return start, end


def _previous_period(start, end):
    duration = end - start
    return start - duration, start


def _get_format():
    fmt = request.args.get('format', 'csv')
    return fmt if fmt in VALID_FORMATS else 'csv'


def _export_response(filename, fmt, title, kpis, headers, rows, charts=None):
    if fmt == 'csv':
        content = build_csv(title, kpis, headers, rows)
        return Response(
            content, mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename="{filename}.csv"'},
        )
    content = build_pdf(title, kpis, headers, rows, charts=charts)
    return Response(
        content, mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment; filename="{filename}.pdf"'},
    )


def _bucket_income_series(start, end):
    """Por dia si el rango es <=31 dias, por mes si es <=366, si no por anio -
    mismo patron de bucketing que el dashboard de Inicio (decision 47), pero
    sobre un rango libre en vez de siempre 'hoy'."""
    duration_days = (end - start).days
    series = []
    if duration_days <= 31:
        cursor = start
        while cursor < end:
            nxt = cursor + timedelta(days=1)
            series.append({'label': cursor.strftime('%d/%m'), 'value': float(_net_income_between(cursor, nxt))})
            cursor = nxt
    elif duration_days <= 366:
        cursor = datetime(start.year, start.month, 1)
        while cursor < end:
            b_start, b_end = _month_bounds(cursor.year, cursor.month)
            value = _net_income_between(max(b_start, start), min(b_end, end))
            series.append({'label': f'{MONTH_LABELS[cursor.month - 1]} {cursor.year}', 'value': float(value)})
            cursor = b_end
    else:
        year = start.year
        while datetime(year, 1, 1) < end:
            y_start, y_end = datetime(year, 1, 1), datetime(year + 1, 1, 1)
            value = _net_income_between(max(y_start, start), min(y_end, end))
            series.append({'label': str(year), 'value': float(value)})
            year += 1
    return series


# ---------------------------------------------------------------------------
# Financiero
# ---------------------------------------------------------------------------

def _invoice_row(inv):
    return {
        'invoiceNumber': inv.invoice_number,
        'clientName': inv.client_name,
        'issueDate': inv.issue_date.isoformat() if inv.issue_date else None,
        'method': inv.payment.payment_method if inv.payment else None,
        'total': float(inv.total),
        'status': inv.status,
    }


def _financial_kpis(start, end):
    prev_start, prev_end = _previous_period(start, end)
    income = _net_income_between(start, end)
    income_prev = _net_income_between(prev_start, prev_end)

    invoices_q = Invoice.query.filter(Invoice.issue_date >= start, Invoice.issue_date < end)
    emitted_count = invoices_q.filter(Invoice.status == 'Emitida').count()
    voided_count = invoices_q.filter(Invoice.status == 'Anulada').count()

    avg_ticket = db.session.query(func.avg(Invoice.total)).filter(
        Invoice.issue_date >= start, Invoice.issue_date < end, Invoice.status == 'Emitida'
    ).scalar() or 0

    returns_in_range = Return.query.filter(Return.created_at >= start, Return.created_at < end).all()
    returns_total = sum((r.refund_amount for r in returns_in_range), Decimal('0'))

    return {
        'incomeTotal': float(income),
        'incomeChangePercent': _percent_change(income, income_prev),
        'invoicesEmitted': emitted_count,
        'invoicesVoided': voided_count,
        'averageTicket': float(avg_ticket),
        'returnsTotal': float(returns_total),
        'returnsCount': len(returns_in_range),
    }


def _net_payment_methods(start, end):
    """Pagos - devoluciones por metodo (mismo criterio 'neto' que ya usa
    Caja - netEfectivo/netTransferencia en cash_register/routes.py), con la
    cantidad de pagos aparte - el monto neto y la cantidad de transacciones
    miden cosas distintas (ej. 2 pagos chicos en Transferencia pueden pesar
    menos en dinero que 1 pago grande en Efectivo), mostrar ambos evita
    confundirlos."""
    payment_rows = (
        db.session.query(Payment.payment_method, func.sum(Payment.amount), func.count(Payment.id))
        .filter(Payment.paid_at >= start, Payment.paid_at < end,
                Payment.payment_method.in_(['Efectivo', 'Transferencia']))
        .group_by(Payment.payment_method)
        .all()
    )
    gross = {method: float(total) for method, total, _ in payment_rows}
    counts = {method: count for method, _, count in payment_rows}

    return_rows = (
        db.session.query(Return.refund_method, func.sum(Return.refund_amount))
        .filter(Return.created_at >= start, Return.created_at < end,
                Return.refund_method.in_(['Efectivo', 'Transferencia']))
        .group_by(Return.refund_method)
        .all()
    )
    refunded = {method: float(total) for method, total in return_rows}

    return {
        method: {
            'amount': max(0.0, gross.get(method, 0.0) - refunded.get(method, 0.0)),
            'count': counts.get(method, 0),
        }
        for method in ('Efectivo', 'Transferencia')
    }


@reports_bp.route('/financial', methods=['GET'])
@role_required('admin')
def financial_report():
    start, end = _parse_date_range()
    kpis = _financial_kpis(start, end)
    payment_methods = _net_payment_methods(start, end)

    invoices_q = Invoice.query.filter(Invoice.issue_date >= start, Invoice.issue_date < end)
    page = request.args.get('page', default=1, type=int)
    per_page = min(request.args.get('perPage', default=10, type=int), 100)
    paginated = invoices_q.order_by(Invoice.issue_date.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'kpis': kpis,
        'chart': _bucket_income_series(start, end),
        'paymentMethods': payment_methods,
        'invoices': {
            'items': [_invoice_row(i) for i in paginated.items],
            'total': paginated.total, 'page': paginated.page, 'perPage': paginated.per_page, 'pages': paginated.pages,
        },
    })


@reports_bp.route('/financial/export', methods=['GET'])
@role_required('admin')
def financial_report_export():
    start, end = _parse_date_range()
    kpis = _financial_kpis(start, end)
    income_series = _bucket_income_series(start, end)
    payment_methods = _net_payment_methods(start, end)
    invoices = Invoice.query.filter(
        Invoice.issue_date >= start, Invoice.issue_date < end
    ).order_by(Invoice.issue_date.desc()).all()

    headers = ['N° Factura', 'Cliente', 'Fecha', 'Método', 'Total', 'Estado']
    rows = [
        [i.invoice_number, i.client_name, i.issue_date.strftime('%d/%m/%Y') if i.issue_date else '',
         i.payment.payment_method if i.payment else '', f'{float(i.total):,.0f}', i.status]
        for i in invoices
    ]
    kpi_list = [
        ('Ingresos Netos', f'$ {kpis["incomeTotal"]:,.0f}'),
        ('Facturas Emitidas', kpis['invoicesEmitted']),
        ('Facturas Anuladas', kpis['invoicesVoided']),
        ('Ticket Promedio', f'$ {kpis["averageTicket"]:,.0f}'),
        ('Devoluciones', f'$ {kpis["returnsTotal"]:,.0f} ({kpis["returnsCount"]} procesadas)'),
    ]
    charts = [
        {
            'type': 'bar', 'format': 'currency', 'title': 'Ingresos netos por período',
            'labels': [p['label'] for p in income_series], 'values': [p['value'] for p in income_series],
        },
        {
            'type': 'pie', 'title': 'Métodos de pago',
            'labels': ['Efectivo', 'Transferencia'],
            'values': [payment_methods['Efectivo']['amount'], payment_methods['Transferencia']['amount']],
        },
    ]
    return _export_response('reporte_financiero', _get_format(), 'Reporte Financiero', kpi_list, headers, rows, charts)


# ---------------------------------------------------------------------------
# Inventario
# ---------------------------------------------------------------------------

def _top_category_name(category):
    if category is None:
        return 'Sin categoría'
    return category.parent.name if category.parent else category.name


def _stock_status(product):
    if product.stock <= 0:
        return 'Sin stock'
    if product.stock <= product.min_stock:
        return 'Bajo'
    return 'Óptimo'


def _inventory_data():
    products = Product.query.all()
    active = [p for p in products if p.is_active]
    inactive_count = len(products) - len(active)
    inventory_value = sum((p.stock * p.purchase_price for p in active), Decimal('0'))
    out_of_stock = [p for p in active if p.stock <= 0]

    top_rows = (
        db.session.query(SalesOrderItem.product_id, func.sum(SalesOrderItem.quantity).label('sold'))
        .join(SalesOrder, SalesOrder.id == SalesOrderItem.order_id)
        .filter(SalesOrder.status.in_(['Pagado', 'Entregado']))
        .group_by(SalesOrderItem.product_id)
        .order_by(func.sum(SalesOrderItem.quantity).desc())
        .limit(5)
        .all()
    )
    top_products = []
    for product_id, sold in top_rows:
        product = Product.query.get(product_id)
        if product and product.is_active:
            top_products.append({'name': product.name, 'unitsSold': float(sold)})

    by_category = {}
    for p in active:
        key = _top_category_name(p.category)
        by_category[key] = by_category.get(key, 0) + 1

    return {
        'kpis': {
            'activeProducts': len(active),
            'inactiveProducts': inactive_count,
            'inventoryValue': float(inventory_value),
            'outOfStock': len(out_of_stock),
            'topProduct': top_products[0]['name'] if top_products else None,
        },
        'topProducts': top_products,
        'byCategory': [{'category': k, 'count': v} for k, v in by_category.items()],
        'products': sorted(active, key=lambda p: p.name),
    }


@reports_bp.route('/inventory', methods=['GET'])
@role_required('admin', 'bodeguero')
def inventory_report():
    data = _inventory_data()
    products = data['products']

    page = request.args.get('page', default=1, type=int)
    per_page = min(request.args.get('perPage', default=10, type=int), 100)
    total = len(products)
    pages = max((total + per_page - 1) // per_page, 1)
    start_idx = (page - 1) * per_page
    page_items = products[start_idx:start_idx + per_page]

    return jsonify({
        'kpis': data['kpis'],
        'topProducts': data['topProducts'],
        'byCategory': data['byCategory'],
        'products': {
            'items': [{**_product_payload(p), 'status': _stock_status(p)} for p in page_items],
            'total': total, 'page': page, 'perPage': per_page, 'pages': pages,
        },
    })


@reports_bp.route('/inventory/export', methods=['GET'])
@role_required('admin', 'bodeguero')
def inventory_report_export():
    data = _inventory_data()

    headers = ['Producto', 'Categoría', 'Stock', 'Mínimo', 'Valor', 'Estado']
    rows = [
        [p.name, p.category.name if p.category else '', float(p.stock), float(p.min_stock),
         f'{float(p.stock * p.purchase_price):,.0f}', _stock_status(p)]
        for p in data['products']
    ]
    kpi_list = [
        ('Productos Activos', data['kpis']['activeProducts']),
        ('Productos Inactivos', data['kpis']['inactiveProducts']),
        ('Valor del Inventario', f'$ {data["kpis"]["inventoryValue"]:,.0f}'),
        ('Sin Stock', data['kpis']['outOfStock']),
        ('Alta Rotación', data['kpis']['topProduct'] or '—'),
    ]
    charts = [
        {
            'type': 'bar', 'format': 'number', 'title': 'Productos más vendidos',
            'labels': [p['name'] for p in data['topProducts']], 'values': [p['unitsSold'] for p in data['topProducts']],
        },
        {
            'type': 'pie', 'title': 'Productos activos por categoría',
            'labels': [c['category'] for c in data['byCategory']], 'values': [c['count'] for c in data['byCategory']],
        },
    ]
    return _export_response('reporte_inventario', _get_format(), 'Reporte de Inventario', kpi_list, headers, rows, charts)


# ---------------------------------------------------------------------------
# Clientes
# ---------------------------------------------------------------------------

def _clients_kpis(start, end):
    base = _client_query()
    total = base.count()
    active = base.filter(User.is_active.is_(True)).count()
    new_count = base.filter(User.created_at >= start, User.created_at < end).count()
    return {
        'total': total,
        'active': active,
        'inactive': total - active,
        'activePercent': round(active / total * 100, 1) if total else 0,
        'newInPeriod': new_count,
    }


def _clients_charts():
    by_month_rows = (
        db.session.query(extract('year', User.created_at), extract('month', User.created_at), func.count(User.id))
        .join(User.roles).filter(Role.name == 'cliente')
        .group_by(extract('year', User.created_at), extract('month', User.created_at))
        .order_by(extract('year', User.created_at), extract('month', User.created_at))
        .all()
    )
    by_month = [{'year': int(y), 'month': int(m), 'count': c} for y, m, c in by_month_rows]

    by_city_rows = (
        db.session.query(User.ciudad, func.count(User.id))
        .join(User.roles).filter(Role.name == 'cliente', User.ciudad.isnot(None))
        .group_by(User.ciudad)
        .order_by(func.count(User.id).desc())
        .all()
    )
    by_city = [{'city': city, 'count': c} for city, c in by_city_rows]
    return by_month, by_city


def _frequent_clients(limit=5):
    # Todo el historial, sin fecha de corte - mismo criterio que "Productos
    # mas vendidos" (decision 50): con el volumen real de ventas del
    # negocio, limitar a un rango dejaria el ranking vacio la mayoria del
    # tiempo. Solo cuenta pedidos ya pagados (Pagado/Entregado), no
    # Pendiente/Cancelado.
    rows = (
        db.session.query(
            User.id, User.first_name, User.last_name,
            func.count(SalesOrder.id), func.sum(SalesOrder.total),
        )
        .join(SalesOrder, SalesOrder.user_id == User.id)
        .filter(SalesOrder.status.in_(['Pagado', 'Entregado']))
        .group_by(User.id, User.first_name, User.last_name)
        .order_by(func.count(SalesOrder.id).desc())
        .limit(limit)
        .all()
    )
    return [
        {
            'id': user_id,
            'name': f'{first_name} {last_name}',
            'ordersCount': orders_count,
            'totalSpent': float(total_spent or 0),
        }
        for user_id, first_name, last_name, orders_count, total_spent in rows
    ]


def _client_row(user):
    last_order = (
        SalesOrder.query.filter_by(user_id=user.id)
        .order_by(SalesOrder.created_at.desc())
        .first()
    )
    return {
        'id': user.id,
        'name': f'{user.first_name} {user.last_name}',
        'email': user.email,
        'phone': user.phone,
        'ciudad': user.ciudad,
        'isActive': user.is_active,
        'lastPurchaseAt': last_order.created_at.isoformat() if last_order else None,
    }


@reports_bp.route('/clients', methods=['GET'])
@role_required('admin')
def clients_report():
    start, end = _parse_date_range()
    kpis = _clients_kpis(start, end)
    by_month, by_city = _clients_charts()
    frequent_clients = _frequent_clients()

    query = _client_query()
    search = request.args.get('search')
    if search:
        like = f'%{search}%'
        query = query.filter(or_(User.first_name.ilike(like), User.last_name.ilike(like), User.email.ilike(like)))
    status = request.args.get('status')
    if status == 'active':
        query = query.filter(User.is_active.is_(True))
    elif status == 'inactive':
        query = query.filter(User.is_active.is_(False))
    city = request.args.get('city')
    if city:
        query = query.filter(User.ciudad == city)

    query = query.order_by(User.first_name.asc())
    page = request.args.get('page', default=1, type=int)
    per_page = min(request.args.get('perPage', default=10, type=int), 100)
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'kpis': kpis,
        'byMonth': by_month,
        'byCity': by_city,
        'frequentClients': frequent_clients,
        'clients': {
            'items': [_client_row(u) for u in paginated.items],
            'total': paginated.total, 'page': paginated.page, 'perPage': paginated.per_page, 'pages': paginated.pages,
        },
    })


@reports_bp.route('/clients/export', methods=['GET'])
@role_required('admin')
def clients_report_export():
    start, end = _parse_date_range()
    kpis = _clients_kpis(start, end)
    by_month, by_city = _clients_charts()
    frequent_clients = _frequent_clients()
    clients = _client_query().order_by(User.first_name.asc()).all()
    top_frequent = frequent_clients[:1]

    headers = ['Nombre', 'Correo', 'Teléfono', 'Ciudad', 'Estado', 'Última compra']
    rows = []
    for u in clients:
        row = _client_row(u)
        rows.append([
            row['name'], row['email'], row['phone'] or '', row['ciudad'] or '',
            'Activo' if row['isActive'] else 'Inactivo',
            row['lastPurchaseAt'][:10] if row['lastPurchaseAt'] else 'Sin compras',
        ])
    kpi_list = [
        ('Clientes Totales', kpis['total']),
        ('Activos', f'{kpis["active"]} ({kpis["activePercent"]}%)'),
        ('Inactivos', kpis['inactive']),
        ('Nuevos en el período', kpis['newInPeriod']),
        (
            'Cliente más frecuente',
            (
                f'{top_frequent[0]["name"]} '
                f'({top_frequent[0]["ordersCount"]} {"pedido" if top_frequent[0]["ordersCount"] == 1 else "pedidos"})'
            ) if top_frequent else '—',
        ),
    ]
    charts = [
        {
            'type': 'bar', 'format': 'number', 'title': 'Registros por mes',
            'labels': [f'{MONTH_LABELS[b["month"] - 1]} {b["year"]}' for b in by_month],
            'values': [b['count'] for b in by_month],
        },
        {
            'type': 'pie', 'title': 'Distribución por ciudad',
            'labels': [c['city'] for c in by_city], 'values': [c['count'] for c in by_city],
        },
        {
            'type': 'bar', 'format': 'number', 'title': 'Clientes frecuentes (por pedidos)',
            'labels': [c['name'] for c in frequent_clients], 'values': [c['ordersCount'] for c in frequent_clients],
        },
    ]
    return _export_response('reporte_clientes', _get_format(), 'Reporte de Clientes', kpi_list, headers, rows, charts)


# ---------------------------------------------------------------------------
# Citas
# ---------------------------------------------------------------------------

def _appointments_data(start, end):
    appts = Appointment.query.filter(
        Appointment.appointment_datetime >= start, Appointment.appointment_datetime < end
    ).all()

    status_counts = {'Completada': 0, 'Confirmada': 0, 'Pendiente': 0, 'Cancelada': 0}
    for a in appts:
        if a.status in status_counts:
            status_counts[a.status] += 1

    completadas = status_counts['Completada']
    canceladas = status_counts['Cancelada']
    resolved = completadas + canceladas
    attendance_rate = round(completadas / resolved * 100, 1) if resolved else None

    by_vet = {}
    for a in appts:
        if not a.veterinarian_id:
            continue
        key = a.veterinarian_id
        if key not in by_vet:
            name = (
                f'{a.veterinarian.first_name} {a.veterinarian.last_name}' if a.veterinarian else 'Sin asignar'
            )
            by_vet[key] = {'name': name, 'total': 0, 'completadas': 0, 'canceladas': 0}
        by_vet[key]['total'] += 1
        if a.status == 'Completada':
            by_vet[key]['completadas'] += 1
        elif a.status == 'Cancelada':
            by_vet[key]['canceladas'] += 1

    vet_rows = []
    for v in by_vet.values():
        resolved_v = v['completadas'] + v['canceladas']
        v['effectiveness'] = round(v['completadas'] / resolved_v * 100, 1) if resolved_v else None
        vet_rows.append(v)
    vet_rows.sort(key=lambda v: v['total'], reverse=True)

    return {
        'kpis': {'totalAppointments': len(appts), 'attendanceRate': attendance_rate},
        'statusCounts': status_counts,
        'byVeterinarian': vet_rows,
    }


@reports_bp.route('/appointments', methods=['GET'])
@role_required('admin')
def appointments_report():
    start, end = _parse_date_range()
    return jsonify(_appointments_data(start, end))


@reports_bp.route('/appointments/export', methods=['GET'])
@role_required('admin')
def appointments_report_export():
    start, end = _parse_date_range()
    data = _appointments_data(start, end)

    headers = ['Veterinario', 'Total Citas', 'Completadas', 'Canceladas', 'Efectividad']
    rows = [
        [v['name'], v['total'], v['completadas'], v['canceladas'],
         f'{v["effectiveness"]}%' if v['effectiveness'] is not None else '—']
        for v in data['byVeterinarian']
    ]
    rate = data['kpis']['attendanceRate']
    kpi_list = [
        ('Citas del Período', data['kpis']['totalAppointments']),
        ('Tasa de Asistencia', f'{rate}%' if rate is not None else 'Sin datos'),
        ('Completadas', data['statusCounts']['Completada']),
        ('Confirmadas', data['statusCounts']['Confirmada']),
        ('Pendientes', data['statusCounts']['Pendiente']),
        ('Canceladas', data['statusCounts']['Cancelada']),
    ]
    charts = [
        {
            'type': 'pie', 'title': 'Estado de las citas',
            'labels': list(data['statusCounts'].keys()), 'values': list(data['statusCounts'].values()),
        },
        {
            'type': 'bar', 'format': 'number', 'title': 'Citas por veterinario',
            'labels': [v['name'] for v in data['byVeterinarian']], 'values': [v['total'] for v in data['byVeterinarian']],
        },
    ]
    return _export_response('reporte_citas', _get_format(), 'Resumen de Citas', kpi_list, headers, rows, charts)


# ---------------------------------------------------------------------------
# Caja
# ---------------------------------------------------------------------------

def _resolve_session(session_id):
    if session_id:
        return CashRegisterSession.query.get_or_404(session_id)
    session = get_open_session()
    if session:
        return session
    return (
        CashRegisterSession.query.filter_by(status='Cerrada')
        .order_by(CashRegisterSession.closed_at.desc())
        .first()
    )


@reports_bp.route('/cash', methods=['GET'])
@role_required('admin')
def cash_report():
    session_id = request.args.get('sessionId', type=int)
    session = _resolve_session(session_id)

    recent_sessions = CashRegisterSession.query.order_by(CashRegisterSession.opened_at.desc()).limit(10).all()

    return jsonify({
        'session': _session_payload(session, include_movements=True) if session else None,
        'recentSessions': [
            {'id': s.id, 'status': s.status, 'openedAt': s.opened_at.isoformat() if s.opened_at else None}
            for s in recent_sessions
        ],
    })


@reports_bp.route('/cash/export', methods=['GET'])
@role_required('admin')
def cash_report_export():
    session_id = request.args.get('sessionId', type=int)
    session = _resolve_session(session_id)
    headers = ['Hora', 'Tipo', 'Referencia', 'Método', 'Monto']

    if not session:
        return _export_response('reporte_caja', _get_format(), 'Reporte de Caja', [], headers, [])

    payload = _session_payload(session, include_movements=True)
    totals = payload['totals']

    rows = [
        [m['time'][11:16] if m['time'] else '', 'Venta' if m['kind'] == 'in' else 'Devolución',
         m.get('invoiceNumber') or m.get('reason') or '', m['method'], f'{m["amount"]:,.0f}']
        for m in payload['movements']
    ]
    kpi_list = [
        ('Estado', session.status),
        ('Responsable', payload['responsibleUserName'] or '—'),
        ('Total Recaudado', f'$ {totals["totalRecaudado"]:,.0f}'),
        ('Efectivo Esperado', f'$ {totals["expectedCashLive"]:,.0f}'),
    ]
    if payload['cashDifference'] is not None:
        kpi_list.append(('Diferencia de Cuadre', f'$ {payload["cashDifference"]:,.0f}'))
        if payload['differenceJustification']:
            kpi_list.append(('Justificación', payload['differenceJustification']))

    charts = [{
        'type': 'pie', 'title': 'Efectivo vs Transferencia',
        'labels': ['Efectivo', 'Transferencia'],
        'values': [totals['netEfectivo'], totals['netTransferencia']],
    }]
    return _export_response('reporte_caja', _get_format(), 'Reporte de Caja', kpi_list, headers, rows, charts)
