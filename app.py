from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from src.db import get_db, init_app as init_db_app
from datetime import datetime
import json
import psycopg2

app = Flask(__name__, static_folder='src/static', template_folder='src/templates')
app.secret_key = 'walletmoneyfamily_2025_super_secreta_123456789'

init_db_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


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
    cursor.execute('SELECT id, correo, nombre, familia_id FROM usuarios WHERE id = %s', (user_id,))
    data = cursor.fetchone()
    if data:
        return User(data['id'], data['correo'], data['nombre'], data['familia_id'])
    return None


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'register':
            nombre = request.form['nombre'].strip()
            correo = request.form['correo'].strip().lower()
            contrasena = request.form['contrasena']
            nueva_familia = request.form.get('nueva_familia', '').strip()
            familia_id = request.form.get('familia_id', '').strip()

            if not all([nombre, correo, contrasena]):
                flash('Todos los campos son obligatorios.', 'warning')
                return redirect(url_for('login'))

            try:
                if nueva_familia:
                    cursor.execute('INSERT INTO familias (nombre) VALUES (%s) RETURNING id', (nueva_familia,))
                    result = cursor.fetchone()
                    familia_id = result['id']
                    conn.commit()
                elif familia_id:
                    familia_id = int(familia_id)
                else:
                    flash('Selecciona o crea una familia.', 'warning')
                    return redirect(url_for('login'))

                cursor.execute(
                    'INSERT INTO usuarios (nombre, correo, contrasena, familia_id) VALUES (%s, %s, %s, %s)',
                    (nombre, correo, contrasena, familia_id)
                )
                conn.commit()
                flash('Cuenta creada exitosamente!', 'success')

            except psycopg2.IntegrityError as e:
                conn.rollback()
                if 'usuarios_correo_key' in str(e):
                    flash('Este correo ya está registrado.', 'danger')
                elif 'familias_nombre_key' in str(e):
                    flash('El nombre de la familia ya existe.', 'danger')
                else:
                    flash('Datos duplicados.', 'danger')
            except Exception as e:
                conn.rollback()
                flash('Error inesperado.', 'danger')
            return redirect(url_for('login'))

        elif action == 'login':
            correo = request.form['correo'].strip().lower()
            contrasena = request.form['contrasena']
            cursor.execute(
                'SELECT id, correo, nombre, familia_id FROM usuarios WHERE correo = %s AND contrasena = %s',
                (correo, contrasena)
            )
            user_data = cursor.fetchone()
            if user_data:
                user = User(user_data['id'], user_data['correo'], user_data['nombre'], user_data['familia_id'])
                login_user(user)
                session['familia_id'] = user_data['familia_id']
                flash(f'Bienvenido, {user.nombre}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Credenciales incorrectas.', 'danger')

    cursor.execute('SELECT id, nombre FROM familias ORDER BY nombre')
    familias = cursor.fetchall()
    return render_template('login.html', familias=familias)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    conn = get_db()
    cursor = conn.cursor()
    familia_id = current_user.familia_id

    if request.method == 'POST' and 'tipo' in request.form:
        tipo = request.form['tipo']
        titulo = request.form['titulo'].strip()
        try:
            monto = float(request.form['monto'])
            if monto <= 0: raise ValueError()
        except:
            flash('Monto inválido.', 'danger')
            return redirect(url_for('dashboard'))

        miembro = request.form['miembro'].strip()
        categoria = request.form['categoria'].strip()
        descripcion = request.form.get('descripcion', '').strip()
        fecha = datetime.now()

        tabla = 'ingresos' if tipo == 'ingreso' else 'gastos'
        cursor.execute(f'INSERT INTO {tabla} (usuario_id, titulo, monto, miembro, categoria, descripcion, fecha) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                      (current_user.id, titulo, monto, miembro, categoria, descripcion, fecha))
        conn.commit()
        flash(f'{tipo.title()} registrado!', 'success')
        return redirect(url_for('dashboard'))

    # Datos para el dashboard 
    cursor.execute('SELECT nombre FROM familias WHERE id = %s', (familia_id,))
    familia = cursor.fetchone()
    familia_nombre = familia['nombre'] if familia else "Familia"

    cursor.execute('SELECT nombre, correo FROM usuarios WHERE familia_id = %s ORDER BY nombre', (familia_id,))
    miembros_familia = cursor.fetchall()

    # Totales ingresos y gastos
    cursor.execute('SELECT COALESCE(SUM(monto), 0) FROM ingresos i JOIN usuarios u ON i.usuario_id = u.id WHERE u.familia_id = %s', (familia_id,))
    total_ingresos = float(cursor.fetchone()['coalesce'])

    cursor.execute('SELECT COALESCE(SUM(monto), 0) FROM gastos g JOIN usuarios u ON g.usuario_id = u.id WHERE u.familia_id = %s', (familia_id,))
    total_gastos = float(cursor.fetchone()['coalesce'])

    saldo_total = total_ingresos - total_gastos

    # Últimos movimientos
    cursor.execute('''
        SELECT 'ingreso' AS tipo, titulo, monto, fecha, miembro, id FROM ingresos 
        WHERE usuario_id IN (SELECT id FROM usuarios WHERE familia_id=%s)
        UNION ALL
        SELECT 'gasto' AS tipo, titulo, monto, fecha, miembro, id FROM gastos 
        WHERE usuario_id IN (SELECT id FROM usuarios WHERE familia_id=%s)
        ORDER BY fecha DESC, id DESC LIMIT 10
    ''', (familia_id, familia_id))
    movimientos = cursor.fetchall()

    # Verificar si tiene movimientos
    cursor.execute('SELECT 1 FROM ingresos WHERE usuario_id = %s UNION ALL SELECT 1 FROM gastos WHERE usuario_id = %s LIMIT 1',
                  (current_user.id, current_user.id))
    tiene_movimientos = cursor.fetchone() is not None

    # Gráfico barras 
    cursor.execute('''
        SELECT TO_CHAR(fecha, 'Mon YYYY') AS mes,
               COALESCE(SUM(CASE WHEN tipo='ingreso' THEN monto ELSE 0 END), 0) AS ingresos,
               COALESCE(SUM(CASE WHEN tipo='gasto' THEN monto ELSE 0 END), 0) AS gastos
        FROM (
            SELECT fecha, monto, 'ingreso' AS tipo FROM ingresos WHERE usuario_id IN (SELECT id FROM usuarios WHERE familia_id=%s)
            UNION ALL
            SELECT fecha, monto, 'gasto' AS tipo FROM gastos WHERE usuario_id IN (SELECT id FROM usuarios WHERE familia_id=%s)
        ) t
        GROUP BY mes ORDER BY MIN(fecha) DESC LIMIT 6
    ''', (familia_id, familia_id))
    barras = cursor.fetchall()
    meses = [row['mes'] for row in barras] if barras else ['Sin datos']
    ingresos_mensual = [float(row['ingresos']) for row in barras] if barras else [0]
    gastos_mensual = [float(row['gastos']) for row in barras] if barras else [0]

    # Gráfico pastel
    cursor.execute('SELECT categoria, COALESCE(SUM(monto), 0) AS total FROM gastos WHERE usuario_id IN (SELECT id FROM usuarios WHERE familia_id=%s) AND categoria IS NOT NULL GROUP BY categoria', (familia_id,))
    pastel = cursor.fetchall()
    categorias = [row['categoria'] for row in pastel] if pastel else ['Sin gastos']
    montos_categoria = [float(row['total']) for row in pastel] if pastel else [0]

    # Grafico línea 
    cursor.execute('''
        SELECT fecha, 
               SUM(CASE WHEN tipo='ingreso' THEN monto ELSE -monto END) AS saldo_diario
        FROM (
            SELECT fecha, monto, 'ingreso' AS tipo FROM ingresos WHERE usuario_id IN (SELECT id FROM usuarios WHERE familia_id=%s)
            UNION ALL
            SELECT fecha, monto, 'gasto' AS tipo FROM gastos WHERE usuario_id IN (SELECT id FROM usuarios WHERE familia_id=%s)
        ) t
        GROUP BY fecha ORDER BY fecha
    ''', (familia_id, familia_id))
    linea = cursor.fetchall()

    fechas_saldo = []
    saldo_acumulado = []
    acum = 0

    if linea:
        for row in linea:
            fecha_str = row['fecha'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(row['fecha'], 'strftime') else str(row['fecha'])
            fechas_saldo.append(fecha_str)
            acum += float(row['saldo_diario'])
            saldo_acumulado.append(round(acum, 2))
    else:
        hoy = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        fechas_saldo = [hoy]
        saldo_acumulado = [0]

    today = datetime.now().strftime('%Y-%m-%d ')

    return render_template('dashboard.html',
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
        tiene_movimientos=tiene_movimientos,
        today=today,
        current_user=current_user
    )

   # Filtro para mostrar fecha + hora 
@app.template_filter('datetime')
def format_datetime(value):
    if value is None:
        return ""
    return value.strftime('%Y-%m-%d %H:%M:%S')

# Eliminar último movimiento
@app.route('/eliminar_ultimo', methods=['POST'])
@login_required
def eliminar_ultimo():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT 'ingreso' AS tipo, id, fecha FROM ingresos WHERE usuario_id = %s
        UNION ALL
        SELECT 'gasto'   tipo, id, fecha FROM gastos   WHERE usuario_id = %s
        ORDER BY fecha DESC, id DESC LIMIT 1
    ''', (current_user.id, current_user.id))

    ultimo_movimiento = cursor.fetchone()

    if not ultimo_movimiento:
        flash('No tienes movimientos para eliminar.', 'info')
        return redirect(url_for('dashboard'))   

    tipo   = ultimo_movimiento['tipo']
    mov_id = ultimo_movimiento['id']

    if tipo == 'ingreso':
        cursor.execute('DELETE FROM ingresos WHERE id = %s', (mov_id,))
    else:
        cursor.execute('DELETE FROM gastos WHERE id = %s', (mov_id,))

    conn.commit()
    flash('Último movimiento eliminado correctamente.', 'warning')
    return redirect(url_for('dashboard'))

# Cerrar sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('familia_id', None)
    return redirect(url_for('login'))


# Inicializar la base de datos 
from init_db import init_db
with app.app_context():
    init_db()


if __name__ == '__main__':
    app.run(debug=True)