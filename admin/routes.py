# admin/routes.py
from flask import render_template, jsonify
from flask_login import login_required, current_user
from admin import bp
from models.user import User
from utils.decorators import admin_required
from utils.database import get_db_connection
from psycopg2.extras import RealDictCursor

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    return render_template('dashboard.html')

@bp.route('/users', methods=['GET'])
@login_required
@admin_required
def get_users():
    """
    Ruta para obtener todos los usuarios (solo admin)
    """
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Error de conexión a la base de datos'}), 500
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, email, role, is_active 
                FROM users
                ORDER BY id
            """)
            users = cur.fetchall()
            return jsonify(users), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    """
    Ruta para eliminar un usuario (solo admin)
    """
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Error de conexión a la base de datos'}), 500
    
    try:
        with conn.cursor() as cur:
            # Verificar si el usuario existe
            cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if not cur.fetchone():
                return jsonify({'error': 'Usuario no encontrado'}), 404
            
            # Eliminar el usuario
            cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            return jsonify({'message': 'Usuario eliminado exitosamente'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()
