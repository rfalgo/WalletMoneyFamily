from src.db import get_db

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Tablas SQL para la aplicación WalletMoneyFamily
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS familias (
            id SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL UNIQUE,
            contrasena TEXT NOT NULL,
            familia_id INTEGER,
            FOREIGN KEY (familia_id) REFERENCES familias(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ingresos (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER,
            titulo TEXT NOT NULL,
            monto REAL NOT NULL,
            miembro TEXT NOT NULL,
            categoria TEXT,
            descripcion TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- GUARDA FECHA + HORA
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gastos (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER,
            titulo TEXT NOT NULL,
            monto REAL NOT NULL,
            miembro TEXT NOT NULL,
            categoria TEXT,
            descripcion TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- GUARDA FECHA + HORA
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    ''')

    # Asegurar que las columnas de fecha sean del tipo TIMESTAMP
    try:
        cursor.execute('ALTER TABLE ingresos ALTER COLUMN fecha TYPE TIMESTAMP USING fecha::timestamp')
        cursor.execute('ALTER TABLE gastos ALTER COLUMN fecha TYPE TIMESTAMP USING fecha::timestamp')
    except:
        pass  

    try:
        cursor.execute('ALTER TABLE ingresos ALTER COLUMN fecha SET DEFAULT CURRENT_TIMESTAMP')
        cursor.execute('ALTER TABLE gastos ALTER COLUMN fecha SET DEFAULT CURRENT_TIMESTAMP')
    except:
        pass  

    conn.commit()
    print("Base de datos inicializada correctamente")

if __name__ == '__main__':
    init_db()