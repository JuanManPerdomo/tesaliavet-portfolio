import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    # Access token corto + refresh token largo (ver decision 8/Next Steps #3 en
    # CLAUDE.md) - antes el access token duraba 7 dias fijos sin forma de
    # renovarlo. api.js renueva solo via /auth/refresh cuando un 401 llega por
    # token vencido, asi que la sesion real sigue durando ~30 dias para el
    # usuario aunque el access token en si sea de corta duracion.
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'uploads')

    # Recuperacion de contrasena por correo (codigo de 6 digitos, decision
    # 40/54): sin MAIL_USERNAME configurado, auth/mailer.py loguea el codigo
    # en vez de mandarlo, asi el flujo se puede probar entero en desarrollo
    # sin esperar credenciales reales. Mismo patron para BANK_*/BREB_* mas
    # abajo (checkout). Activo desde 2026-08-23 con un Gmail real.
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'TesaliaVet <no-responder@tesaliavet.com>')

    # Deep-links del frontend dentro de los correos transaccionales (ej.
    # "Ver mi pedido" -> {FRONTEND_URL}/mis-pedidos/12) - decision 40 lo
    # habia quitado al pasar a codigo de 6 digitos, se reintroduce solo
    # para esto. Default de desarrollo (puerto real de Vite en este
    # proyecto); en produccion se sobreescribe con el dominio real.
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

    # Datos de Transferencia para el checkout (decision 28 en CLAUDE.md): sin
    # pasarela online, el cliente transfiere por su cuenta a esta cuenta real
    # y el personal lo verifica manualmente. Vacios por defecto - nunca se
    # commitean valores reales aca, solo viven en backend/.env de cada
    # maquina (gitignored). BREB_KEY vacio hasta que el negocio tenga una
    # llave Bre-B real; mientras tanto el checkout muestra "Próximamente".
    BANK_ACCOUNT_HOLDER = os.getenv('BANK_ACCOUNT_HOLDER', '')
    BANK_NAME = os.getenv('BANK_NAME', '')
    BANK_ACCOUNT_TYPE = os.getenv('BANK_ACCOUNT_TYPE', '')
    BANK_ACCOUNT_NUMBER = os.getenv('BANK_ACCOUNT_NUMBER', '')
    BREB_KEY = os.getenv('BREB_KEY', '')
    BREB_BANK = os.getenv('BREB_BANK', '')
