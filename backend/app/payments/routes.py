from flask import Blueprint, current_app, jsonify
from flask_jwt_extended import jwt_required

payments_bp = Blueprint('payments', __name__)


@payments_bp.route('/bank-transfer-info', methods=['GET'])
@jwt_required()
def bank_transfer_info():
    # Sin pasarela de pago online (decision 28 en CLAUDE.md) - Transferencia
    # se resuelve mostrando datos reales para que el cliente transfiera por
    # su cuenta, verificado despues por el personal (POST
    # /orders/staff/<id>/payment). Mismo patron que MAIL_*/recuperacion de
    # contrasena: vacio hasta que existan datos reales, sin romper el resto
    # del checkout.
    cfg = current_app.config
    bank_available = bool(cfg.get('BANK_ACCOUNT_NUMBER'))
    breb_available = bool(cfg.get('BREB_KEY'))

    return jsonify({
        'bank': {
            'available': bank_available,
            'accountHolder': cfg.get('BANK_ACCOUNT_HOLDER') or None,
            'bankName': cfg.get('BANK_NAME') or None,
            'accountType': cfg.get('BANK_ACCOUNT_TYPE') or None,
            'accountNumber': cfg.get('BANK_ACCOUNT_NUMBER') or None,
        },
        'breb': {
            'available': breb_available,
            'key': cfg.get('BREB_KEY') or None,
            'bankName': cfg.get('BREB_BANK') or None,
        },
    })
