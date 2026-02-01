from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from models import db, User
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate = Migrate(app, db)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Jinja Filters
    @app.template_filter('currency')
    def format_currency(value):
        try:
            return "Rp {:,.0f}".format(value).replace(',', '.')
        except (ValueError, TypeError):
            return "Rp 0"

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.pengadaan import pengadaan_bp
    from routes.penyedia import penyedia_bp
    from routes.anggaran import anggaran_bp
    from routes.users import users_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(pengadaan_bp, url_prefix='/pengadaan')
    app.register_blueprint(penyedia_bp, url_prefix='/penyedia')
    app.register_blueprint(anggaran_bp, url_prefix='/anggaran')
    app.register_blueprint(users_bp, url_prefix='/users')

    @app.route('/')
    def index():
        return redirect(url_for('dashboard.index'))

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
