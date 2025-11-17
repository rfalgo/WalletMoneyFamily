import sqlite3

def init_db():
    conn = sqlite3.connect('walletmoneyfamily.db')
    cursor = conn.cursor()

    # === TABLAS ===
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS familias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL UNIQUE,
            contrasena TEXT NOT NULL,
            familia_id INTEGER,
            FOREIGN KEY (familia_id) REFERENCES familias(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ingresos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            titulo TEXT NOT NULL,
            monto REAL NOT NULL,
            miembro TEXT NOT NULL,
            categoria TEXT,
            descripcion TEXT,
            fecha DATE NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            titulo TEXT NOT NULL,
            monto REAL NOT NULL,
            miembro TEXT NOT NULL,
            categoria TEXT,
            descripcion TEXT,
            fecha DATE NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    ''')

    # === DATOS ===
    """cursor.execute('INSERT OR IGNORE INTO familias (nombre) VALUES (?)', ('Familia López',))
    cursor.execute('SELECT id FROM familias WHERE nombre = ?', ('Familia López',))
    familia_id = cursor.fetchone()[0]

    cursor.execute('INSERT OR IGNORE INTO usuarios (nombre, correo, contrasena, familia_id) VALUES (?, ?, ?, ?)',
                   ('Ana López', 'ana@example.com', '123456', familia_id))
    cursor.execute('SELECT id FROM usuarios WHERE correo = ?', ('ana@example.com',))
    ana_id = cursor.fetchone()[0]

    cursor.execute('INSERT OR IGNORE INTO ingresos (usuario_id, titulo, monto, miembro, categoria, fecha) VALUES (?, ?, ?, ?, ?, ?)',
                   (ana_id, 'Salario', 400000, 'Ana López', 'Salario', '2025-10-25'))
    cursor.execute('INSERT OR IGNORE INTO gastos (usuario_id, titulo, monto, miembro, categoria, fecha) VALUES (?, ?, ?, ?, ?, ?)',
                   (ana_id, 'Supermercado', 30000, 'Ana López', 'Comida', '2025-10-27'))"""

    conn.commit()
    conn.close()
    print("BASE DE DATOS CREADA CON ÉXITO EN LA RAÍZ")

if __name__ == '__main__':
    init_db()