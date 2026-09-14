from ..models import CashRegisterSession


def get_open_session():
    """La sesion de caja abierta ahora mismo, o None. Una sola caja fisica para
    toda la tienda - nunca hay mas de una 'Abierta' a la vez (decision 46)."""
    return CashRegisterSession.query.filter_by(status='Abierta').first()
