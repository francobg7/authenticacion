# app/models/user.py
from utils.database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from flask import current_app
from psycopg2.extras import RealDictCursor

class User:
    def __init__(self, id=None, email=None, password_hash=None, role='user', is_active=True, failed_login_attempts=0, locked_until=None):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.is_active = is_active
        self.failed_login_attempts = failed_login_attempts
        self.locked_until = locked_until

    @staticmethod
    def get_by_email(email):
        conn = get_db_connection()
        if conn is None:
            return None
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                user_data = cur.fetchone()
                if user_data:
                    return User(**user_data)
                return None
        finally:
            conn.close()

    def save(self):
        conn = get_db_connection()
        if conn is None:
            return False
        
        try:
            with conn.cursor() as cur:
                if self.id is None:
                    # Insertar nuevo usuario
                    cur.execute("""
                        INSERT INTO users (email, password_hash, role, is_active)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id
                    """, (self.email, self.password_hash, self.role, self.is_active))
                    self.id = cur.fetchone()[0]
                else:
                    # Actualizar usuario existente
                    cur.execute("""
                        UPDATE users
                        SET email = %s, password_hash = %s, role = %s, 
                            is_active = %s, failed_login_attempts = %s, locked_until = %s
                        WHERE id = %s
                    """, (self.email, self.password_hash, self.role, 
                         self.is_active, self.failed_login_attempts, 
                         self.locked_until, self.id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error guardando usuario: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_jwt_token(self, expires_in=3600):
        return jwt.encode(
            {'user_id': self.id, 'exp': datetime.utcnow() + timedelta(seconds=expires_in)},
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )