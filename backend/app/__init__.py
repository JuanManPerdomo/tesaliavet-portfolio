from flask import Flask
from flask_cors import CORS

from .config import Config
from .extensions import db, migrate, jwt


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from . import models  # noqa: F401 (registra los modelos en SQLAlchemy)
    from .auth.routes import auth_bp
    from .products.routes import products_bp
    from .pqrs.routes import pqrs_bp
    from .pets.routes import pets_bp
    from .catalog.routes import catalog_bp
    from .appointments.routes import appointments_bp
    from .staff.routes import staff_bp
    from .suppliers.routes import suppliers_bp
    from .categories.routes import categories_bp
    from .vaccines.routes import vaccines_bp
    from .species.routes import species_bp
    from .stock_alerts.routes import stock_alerts_bp
    from .purchase_orders.routes import purchase_orders_bp
    from .cart.routes import cart_bp
    from .orders.routes import orders_bp
    from .payments.routes import payments_bp
    from .audit.routes import audit_bp
    from .cash_register.routes import cash_register_bp
    from .notifications.routes import notifications_bp
    from .client_notifications.routes import client_notifications_bp
    from .reports.routes import reports_bp
    from .reminders.commands import register_reminder_commands
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(pqrs_bp, url_prefix='/api/pqrs')
    app.register_blueprint(pets_bp, url_prefix='/api/pets')
    app.register_blueprint(catalog_bp, url_prefix='/api/catalog')
    app.register_blueprint(appointments_bp, url_prefix='/api/appointments')
    app.register_blueprint(staff_bp, url_prefix='/api/staff')
    app.register_blueprint(suppliers_bp, url_prefix='/api/suppliers')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')
    app.register_blueprint(vaccines_bp, url_prefix='/api/vaccines')
    app.register_blueprint(species_bp, url_prefix='/api/species')
    app.register_blueprint(stock_alerts_bp, url_prefix='/api/stock-alerts')
    app.register_blueprint(purchase_orders_bp, url_prefix='/api/purchase-orders')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(audit_bp, url_prefix='/api/audit')
    app.register_blueprint(cash_register_bp, url_prefix='/api/cash-register')
    app.register_blueprint(notifications_bp, url_prefix='/api/staff/notifications')
    app.register_blueprint(client_notifications_bp, url_prefix='/api/notifications')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    register_reminder_commands(app)

    @app.route('/')
    def home():
        return {'message': 'TESALIAVET API'}

    return app