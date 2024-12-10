# __init__.py
from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
from config import Config

login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializar extensiones
    login_manager.init_app(app)
    CORS(app)
    
    # Configurar login_manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página'
    
    # Registrar blueprints
    from auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    from admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        return User.get_by_id(user_id)
    
    return app