# app/utils/validators.py
from email_validator import validate_email, EmailNotValidError
import re
from html import escape

def sanitize_input(text):
    """Sanitiza el input del usuario para prevenir XSS"""
    if isinstance(text, str):
        return escape(text.strip())
    return text

def validate_and_sanitize_user_data(data):
    """Valida y sanitiza los datos de entrada del usuario"""
    sanitized_data = {}
    errors = {}
    
    # Validar y sanitizar email
    email = data.get('email', '').strip().lower()
    try:
        valid_email = validate_email(email).email
        sanitized_data['email'] = valid_email
    except EmailNotValidError:
        errors['email'] = 'Email inválido'
    
    # Validar contraseña
    password = data.get('password', '')
    if not password:
        errors['password'] = 'La contraseña es requerida'
    elif len(password) < 8:
        errors['password'] = 'La contraseña debe tener al menos 8 caracteres'
    elif not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', password):
        errors['password'] = 'La contraseña debe contener al menos una letra y un número'
    else:
        sanitized_data['password'] = password
    
    return sanitized_data, errors