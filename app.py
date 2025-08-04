import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.secret_key = os.environ.get("SESSION_SECRET", "phishx-secret-key-change-in-production")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///phishx.db")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'
    login_manager.login_message = 'Please log in to access the admin panel.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    from routes.admin import admin_bp
    from routes.phish import phish_bp
    from routes.api import api_bp
    
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(phish_bp, url_prefix='/phish')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Main route
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('admin.dashboard'))
    
    with app.app_context():
        # Import models to ensure tables are created
        from models import User, Campaign, CapturedCredential, PhishingTemplate, SessionLog
        db.create_all()
        
        # Create default admin user if not exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            from werkzeug.security import generate_password_hash
            admin_user = User(
                username='admin',
                email='admin@phishx.local',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            app.logger.info("Default admin user created: admin/admin123")
    
    return app

# Create app instance
app = create_app()
