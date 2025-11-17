from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from src.db import get_db, init_app as init_db_app
import sqlite3
from datetime import datetime
import json

app = Flask(__name__, static_folder='src/static', template_folder='src/templates')
app.secret_key = 'tu_clave_secreta_muy_segura_123'

init_db_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# === MODELO DE USUARIO ===
class User(UserMixin):
    def __init__(self, id, correo, nombre, familia_id=None):
        self.id = id
        self.correo = correo
        self.nombre = nombre
        self.familia_id = familia_id


@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, correo, nombre, familia_id FROM usuarios WHERE id = ?', (user_id,))
    data = cursor.fetchone()
    return User(data[0], data[1], data[2], data[3]) if data else None


@app.route('/')
def index():
    return redirect(url_for('login'))


# === LOGIN Y REGISTRO ===
@app.route('/login', methods=['GET', 'POST'])
def login():
    conn = get_db()
    cursor = conn.cursor()
    

    if request.method == 'POST':
        action = request.form.get('action')

        # === REGISTRO DE USUARIO ===
        if action == 'register':
            nombre = request.form['nombre'].strip()
            correo = request.form['correo'].strip().lower()
            contrasena = request.form['contrasena']
            nueva_familia = request.form.get('nueva_familia', '').strip()
            familia_id = request.form.get('familia_id', '').strip()

            # Validaciones básicas
            if not correo or not contrasena or not nombre:
                flash('⚠️ Todos los campos son obligatorios para crear la cuenta.', 'warning')
                return redirect(url_for('login'))

            try:
                if nueva_familia:
                    # Crear nueva familia
                    cursor.execute('INSERT INTO familias (nombre) VALUES (?)', (nueva_familia,))
                    familia_id = cursor.lastrowid
                elif familia_id:
                    familia_id = int(familia_id)
                else:
                    flash('Por favor, selecciona una familia existente o crea una nueva.', 'warning')
                    return redirect(url_for('login'))

                # Crear usuario
                cursor.execute(
                    'INSERT INTO usuarios (nombre, correo, contrasena, familia_id) VALUES (?, ?, ?, ?)',
                    (nombre, correo, contrasena, familia_id)
                )
                conn.commit()
                flash('✅ Cuenta creada con éxito. ¡Ahora puedes iniciar sesión!', 'success')

            except sqlite3.IntegrityError as e:
                if 'familias.nombre' in str(e):
                    flash('Esa familia ya existe. Elige otro nombre.', 'danger')
                elif 'usuarios.correo' in str(e):
                    flash('Este correo ya está registrado. Intenta iniciar sesión.', 'danger')
                else:
                    flash('Error al crear la cuenta. Intenta de nuevo.', 'danger')
            return redirect(url_for('login'))

        # === INICIO DE SESIÓN ===
        elif action == 'login':
            correo = request.form['correo'].strip().lower()
            contrasena = request.form['contrasena']

            cursor.execute(
                'SELECT id, correo, nombre, familia_id FROM usuarios WHERE correo = ? AND contrasena = ?',
                (correo, contrasena)
            )
            user_data = cursor.fetchone()

            if user_data:
                user = User(user_data[0], user_data[1], user_data[2], user_data[3])
                login_user(user)
                session['familia_id'] = user_data[3]
                flash(f'¡Bienvenido, {user.nombre}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('❌ Credenciales incorrectas. Verifica tu correo y contraseña.', 'danger')

    # === Cargar familias existentes ===
    cursor.execute('SELECT id, nombre FROM familias ORDER BY nombre')
    familias = cursor.fetchall()

    return render_template('login.html', familias=familias)


# === DASHBOARD ===
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    familia_id = current_user.familia_id

    # === Registrar ingresos o gastos ===
    if request.method == 'POST' and 'tipo' in request.form:
        tipo = request.form['tipo']
        titulo = request.form['titulo'].strip()
        try:
            monto = float(request.form['monto'])
            if monto <= 0:
                raise ValueError()
        except ValueError:
            flash('El monto debe ser un número mayor que 0.', 'danger')
            return redirect(url_for('dashboard'))

        miembro = request.form['miembro'].strip()
        categoria = request.form['categoria'].strip()
        descripcion = request.form.get('descripcion', '').strip()
        fecha = request.form['fecha']

        tabla = 'ingresos' if tipo == 'ingreso' else 'gastos'
        cursor.execute(f'''
            INSERT INTO {tabla} (usuario_id, titulo, monto, miembro, categoria, descripcion, fecha)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (current_user.id, titulo, monto, miembro, categoria, descripcion, fecha))
        conn.commit()
        flash(f'{tipo.title()} registrado con éxito.', 'success')
        return redirect(url_for('dashboard'))

    # === Datos generales de la familia ===
    cursor.execute('SELECT nombre FROM familias WHERE id = ?', (familia_id,))
    familia = cursor.fetchone()
    familia_nombre = familia['nombre'] if familia else "Familia"

    cursor.execute('SELECT nombre, correo FROM usuarios WHERE familia_id = ? ORDER BY nombre', (familia_id,))
    miembros_familia = cursor.fetchall()

    # === Totales ===
    cursor.execute('''
        SELECT COALESCE(SUM(i.monto), 0) FROM ingresos i
        JOIN usuarios u ON i.usuario_id = u.id
        WHERE u.familia_id = ?
    ''', (familia_id,))
    total_ingresos = float(cursor.fetchone()[0] or 0)

    cursor.execute('''
        SELECT COALESCE(SUM(g.monto), 0) FROM gastos g
        JOIN usuarios u ON g.usuario_id = u.id
        WHERE u.familia_id = ?
    ''', (familia_id,))
    total_gastos = float(cursor.fetchone()[0] or 0)

    saldo_total = total_ingresos - total_gastos

    # === Últimos movimientos ===
    cursor.execute('''
        SELECT tipo, titulo, monto, fecha, miembro, id FROM (
            SELECT 'ingreso' AS tipo, i.titulo, i.monto, i.fecha, i.miembro, i.id
            FROM ingresos i JOIN usuarios u ON i.usuario_id = u.id WHERE u.familia_id = ?
            UNION ALL
            SELECT 'gasto' AS tipo, g.titulo, g.monto, g.fecha, g.miembro, g.id
            FROM gastos g JOIN usuarios u ON g.usuario_id = u.id WHERE u.familia_id = ?
        ) ORDER BY fecha DESC, id DESC LIMIT 5
    ''', (familia_id, familia_id))
    movimientos = cursor.fetchall()

    # === Datos para gráficos ===
    cursor.execute('''
        SELECT strftime('%Y-%m', fecha) as mes,
               SUM(CASE WHEN tipo = 'ingreso' THEN monto ELSE 0 END) AS ingresos,
               SUM(CASE WHEN tipo = 'gasto' THEN monto ELSE 0 END) AS gastos
        FROM (
            SELECT fecha, monto, 'ingreso' AS tipo FROM ingresos i JOIN usuarios u ON i.usuario_id = u.id WHERE u.familia_id = ?
            UNION ALL
            SELECT fecha, monto, 'gasto' AS tipo FROM gastos g JOIN usuarios u ON g.usuario_id = u.id WHERE u.familia_id = ?
        )
        GROUP BY mes ORDER BY mes DESC LIMIT 6
    ''', (familia_id, familia_id))
    barras = cursor.fetchall()

    meses = [datetime.strptime(row['mes'], '%Y-%m').strftime('%b %Y') if row['mes'] else 'Sin mes' for row in barras]
    ingresos_mensual = [float(row['ingresos'] or 0) for row in barras]
    gastos_mensual = [float(row['gastos'] or 0) for row in barras]

    # === Gastos por categoría ===
    cursor.execute('''
        SELECT g.categoria, COALESCE(SUM(g.monto), 0) AS total
        FROM gastos g JOIN usuarios u ON g.usuario_id = u.id
        WHERE u.familia_id = ? AND g.categoria IS NOT NULL AND g.categoria != ''
        GROUP BY g.categoria
    ''', (familia_id,))
    pastel = cursor.fetchall()
    categorias = [row['categoria'] or 'Otros' for row in pastel]
    montos_categoria = [float(row['total']) for row in pastel]

    # === Evolución del saldo ===
    cursor.execute('''
        SELECT fecha, SUM(CASE WHEN tipo = 'ingreso' THEN monto ELSE -monto END) AS saldo_diario
        FROM (
            SELECT fecha, monto, 'ingreso' AS tipo FROM ingresos i JOIN usuarios u ON i.usuario_id = u.id WHERE u.familia_id = ?
            UNION ALL
            SELECT fecha, monto, 'gasto' AS tipo FROM gastos g JOIN usuarios u ON g.usuario_id = u.id WHERE u.familia_id = ?
        )
        GROUP BY fecha ORDER BY fecha
    ''', (familia_id, familia_id))
    linea = cursor.fetchall()

    fechas_saldo = [row['fecha'] for row in linea]
    saldo_acumulado = []
    acum = 0
    for row in linea:
        acum += float(row['saldo_diario'] or 0)
        saldo_acumulado.append(round(acum, 2))

    if not meses:
        meses = [datetime.now().strftime('%b %Y')]
        ingresos_mensual = [0]
        gastos_mensual = [0]
    if not categorias:
        categorias = ['Sin gastos']
        montos_categoria = [0]
    if not fechas_saldo:
        fechas_saldo = [datetime.now().strftime('%Y-%m-%d')]
        saldo_acumulado = [0]

    today = datetime.now().strftime('%Y-%m-%d')

    cursor.execute('''
        SELECT COUNT(*) FROM (
            SELECT 1 FROM ingresos WHERE usuario_id = ?
            UNION ALL
            SELECT 1 FROM gastos WHERE usuario_id = ?
        )
    ''', (current_user.id, current_user.id))
    tiene_movimientos = cursor.fetchone()[0] > 0

    return render_template(
        'dashboard.html',
        familia_nombre=familia_nombre,
        saldo_total=saldo_total,
        total_ingresos=total_ingresos,
        total_gastos=total_gastos,
        miembros=len(miembros_familia),
        miembros_familia=miembros_familia,
        movimientos=movimientos,
        meses=json.dumps(meses),
        ingresos_mensual=json.dumps(ingresos_mensual),
        gastos_mensual=json.dumps(gastos_mensual),
        categorias=json.dumps(categorias),
        montos_categoria=json.dumps(montos_categoria),
        fechas_saldo=json.dumps(fechas_saldo),
        saldo_acumulado=json.dumps(saldo_acumulado),
        today=today,
        tiene_movimientos=tiene_movimientos,
        current_user=current_user
    )


# === ELIMINAR ÚLTIMO MOVIMIENTO ===
@app.route('/eliminar_ultimo', methods=['POST'])
@login_required
def eliminar_ultimo():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT 'ingreso' AS tipo, id FROM ingresos
        WHERE usuario_id = ?
        ORDER BY fecha DESC, id DESC LIMIT 1
    ''', (current_user.id,))
    ultimo_ingreso = cursor.fetchone()

    cursor.execute('''
        SELECT 'gasto' AS tipo, id FROM gastos
        WHERE usuario_id = ?
        ORDER BY fecha DESC, id DESC LIMIT 1
    ''', (current_user.id,))
    ultimo_gasto = cursor.fetchone()

    ultimo = None
    if ultimo_ingreso and ultimo_gasto:
        ultimo = ('ingresos', ultimo_ingreso[1]) if ultimo_ingreso[1] > ultimo_gasto[1] else ('gastos', ultimo_gasto[1])
    elif ultimo_ingreso:
        ultimo = ('ingresos', ultimo_ingreso[1])
    elif ultimo_gasto:
        ultimo = ('gastos', ultimo_gasto[1])

    if ultimo:
        tabla, mov_id = ultimo
        cursor.execute(f'DELETE FROM {tabla} WHERE id = ?', (mov_id,))
        conn.commit()
        flash('Último movimiento eliminado correctamente.', 'warning')
    else:
        flash('No tienes movimientos para eliminar.', 'info')

    return redirect(url_for('dashboard'))


# === CERRAR SESIÓN ===
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('familia_id', None)
    return redirect(url_for('login'))


# === INICIALIZAR BASE DE DATOS ===
from init_db import init_db

with app.app_context():
    init_db()
    print("✅ Base de datos verificada en la raíz del proyecto.")

if __name__ == '__main__':
    app.run(debug=True)
