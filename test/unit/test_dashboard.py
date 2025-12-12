def test_registro_movimiento(client):
    """
    Prueba que se pueda registrar un movimiento correctamente
    """
    # Registro + login
    client.post('/login', data={
        'action': 'register',
        'nombre': 'Mov Test',
        'correo': 'movtest123@test.com',
        'contrasena': '123456',
        'nueva_familia': 'MovFam123',
        'miembro': 'Mov Test'
    }, follow_redirects=True)

    client.post('/login', data={
        'action': 'login',
        'correo': 'movtest123@test.com',
        'contrasena': '123456'
    }, follow_redirects=True)

    # Registrar un ingreso
    response = client.post('/dashboard', data={
        'tipo': 'ingreso',
        'titulo': 'Salario Pytest',
        'monto': '5000000',
        'miembro': 'Mov Test',
        'categoria': 'Salario',
        'descripcion': 'Test automatico'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'registrado' in response.data.lower() or b'exitosamente' in response.data.lower()


def test_eliminar_ultimo_movimiento(client):
    """
    Prueba que se elimine correctamente el último movimiento registrado
    """
    # Registro + login
    client.post('/login', data={
        'action': 'register',
        'nombre': 'Elim Test',
        'correo': 'elimtest123@test.com',
        'contrasena': '123456',
        'nueva_familia': 'ElimFam123',
        'miembro': 'Elim Test'
    }, follow_redirects=True)

    client.post('/login', data={
        'action': 'login',
        'correo': 'elimtest123@test.com',
        'contrasena': '123456'
    }, follow_redirects=True)

    # Registrar un movimiento para poder eliminarlo
    client.post('/dashboard', data={
        'tipo': 'gasto',
        'titulo': 'Netflix',
        'monto': '35000',
        'miembro': 'Elim Test',
        'categoria': 'Entretenimiento',
        'descripcion': 'Test eliminar'
    }, follow_redirects=True)

    # Eliminar último
    response = client.post('/eliminar_ultimo', follow_redirects=True)

    assert response.status_code == 200
    assert b'eliminado' in response.data.lower() or b'correctamente' in response.data.lower()


def test_logout(client):
    """
    Prueba que el cierre de sesion funcione correctamente:
    - Redirige al login
    - Destruye la sesion
    - Ya no se puede acceder al dashboard (redirige al login)
    """

    # Registrar y hacer login al usuario
    client.post('/login', data={
        'action': 'register',
        'nombre': 'Usuario Logout',
        'correo': 'logout@test.com',
        'contrasena': '123456',
        'nueva_familia': 'FamiliaTestLogout'
    }, follow_redirects=True)

    client.post('/login', data={
        'action': 'login',
        'correo': 'logout@test.com',
        'contrasena': '123456'
    }, follow_redirects=True)

    # 2. Cerrar sesión
    logout_response = client.get('/logout', follow_redirects=True)

    # 3. verificar que redirige al login y muestra el contenido correcto
    assert logout_response.status_code == 200
    assert b'Login - WalletMoneyFamily' in logout_response.data
    assert b'Iniciar Sesion' in logout_response.data or b'Crear Cuenta Nueva' in logout_response.data

    # 4. Intentar acceder al dashboard → debe redirigir al login 
    dashboard_response = client.get('/dashboard', follow_redirects=False)
    assert dashboard_response.status_code == 302
    assert '/login' in dashboard_response.location  