from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Upload Folder
    import os
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    from flask import redirect, url_for
    @app.route('/')
    def index():
        return redirect(url_for('events.list_events'))

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.routes import auth, admin, events, payment, orders
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(events.bp)
    app.register_blueprint(payment.bp)
    app.register_blueprint(orders.bp)

    return app
