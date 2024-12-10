# run.py
from __init__ import create_app
from utils.database import get_db_connection
from models.user import User

app = create_app()

@app.cli.command("test-db")
def test_db():
    """Prueba la conexión a la base de datos"""
    conn = get_db_connection()
    if conn:
        print("Conexión a la base de datos exitosa!")
        conn.close()
    else:
        print("Error conectando a la base de datos")

@app.cli.command("create-admin")
def create_admin():
    """Crea un usuario administrador"""
    admin = User(
        email='admin@example.com',
        role='admin'
    )
    admin.set_password('Admin123!')
    
    if admin.save():
        print('Usuario admin creado exitosamente')
    else:
        print('Error creando usuario admin')

if __name__ == '__main__':
    app.run(debug=True)