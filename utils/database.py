# app/utils/database.py
import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config

def get_db_connection():
    """Crea una conexión a la base de datos PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            port=Config.DB_PORT
        )
        return conn
        
    except psycopg2.Error as e:
        print(f"Error conectando a PostgreSQL: {e}")
        return None
        
get_db_connection()