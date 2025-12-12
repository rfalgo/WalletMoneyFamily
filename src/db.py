
import os
from flask import g
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
# Función para obtener la conexión a la base de datos
def get_db():
    if 'db' not in g:
        database_url = os.getenv('DATABASE_URL')
        if database_url and database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(
            database_url,
            sslmode='require',
            cursor_factory=RealDictCursor  
        )
        g.db = conn
    return g.db
# Cierre de la conexión
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
# Inicialización de la base de datos con la aplicación Flask
def init_app(app):
    app.teardown_appcontext(close_db)