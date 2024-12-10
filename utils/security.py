# app/utils/security.py

from flask_wtf.csrf import CSRFProtect
from flask import request, abort, jsonify
from functools import wraps
from datetime import datetime, timedelta
from utils import database
from models.user import User  # Agrega esta importación
csrf = CSRFProtect()

def init_security(app):
    # Configuración de cookies seguras
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=1800,  # 30 minutos
        WTF_CSRF_TIME_LIMIT=3600,        # 1 hora
        WTF_CSRF_SSL_STRICT=True
    )
    
    # Inicializar CSRF protection
    csrf.init_app(app)
    
    # Configurar headers de seguridad
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response

def rate_limit(max_attempts=3, lockout_time=300):  # 5 minutos de bloqueo
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if request.method == 'POST':
                user = User.query.filter_by(email=request.json.get('email')).first()
                if user and user.failed_login_attempts >= max_attempts:
                    if not user.locked_until:
                        user.locked_until = datetime.utcnow() + timedelta(seconds=lockout_time)
                        database.session.commit()
                    return jsonify({'error': 'Demasiados intentos. Cuenta bloqueada temporalmente'}), 429
            return f(*args, **kwargs)
        return wrapped
    return decorator