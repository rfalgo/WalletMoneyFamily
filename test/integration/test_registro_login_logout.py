# tests/integration/test_registro_login_logout.py
def test_flujo_completo_registro_login_dashboard_logout(client):
    """
    Prueba de integración completa:
    Registro → Login → Dashboard → Logout → Protección
    FUNCIONA CON TU CÓDIGO REAL (sin flash renderizado en login)
    """

    # Registro de usuario
    response = client.post('/login', data={
        'action': 'register',
        'nombre': 'Ana María',
        'correo': 'ana@test.com',
        'contrasena': '123456',
        'nueva_familia': 'Familia Ana'
    }, follow_redirects=False)

    assert response.status_code == 302
    assert '/login' in response.location

    # Login de usuario
    login_response = client.post('/login', data={
        'action': 'login',
        'correo': 'ana@test.com',
        'contrasena': '123456'
    }, follow_redirects=True)

    assert login_response.status_code == 200
    assert b'dashboard' in login_response.data.lower()
    assert b'Ana' in login_response.data

    # Acceso a Dashboard 
    dashboard_response = client.get('/dashboard')
    assert dashboard_response.status_code == 200

    # Cierre de sesión
    logout_response = client.get('/logout', follow_redirects=True)
    assert logout_response.status_code == 200
    assert b'Login - WalletMoneyFamily' in logout_response.data

    # Protección de rutas tras logout
    protected = client.get('/dashboard', follow_redirects=False)
    assert protected.status_code == 302
    assert '/login' in protected.location