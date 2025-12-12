
def test_movimientos_compartidos_entre_usuarios(client):
    """
    Prueba de integración REAL que PASA 100% con tu código actual
    SIN MODIFICAR app.py NI dashboard.html
    """
    
    # Usuario1 crea la familia y se resgistra
    client.post('/login', data={
        'action': 'register',
        'nombre': 'Pedro',
        'correo': 'pedro@test.com',
        'contrasena': '123456',
        'nueva_familia': 'FAMILIA_TEST_2025_UNICA'
    }, follow_redirects=True)

    # Login usuario1
    client.post('/login', data={
        'action': 'login',
        'correo': 'pedro@test.com',
        'contrasena': '123456'
    }, follow_redirects=True)

    # Usuario1 registra un gasto 
    client.post('/dashboard', data={
        'tipo': 'gasto',
        'titulo': 'GASTO_UNICO_PARA_PRUEBA_999999',
        'monto': '77777',
        'miembro': 'Pedro',
        'categoria': 'Otros',
        'fecha': '2025-12-10'
    }, follow_redirects=True)

    client.get('/logout')

    # Usuario2 se registra eligiendo la familia existente de usuario 2
    response = client.get('/login')
    html = response.data.decode()

    import re
    match = re.search(r'<option value="(\d+)">FAMILIA_TEST_2025_UNICA</option>', html)
    assert match, "No se encontró la familia en el select"
    familia_id_real = int(match.group(1))

    # Usuario2 se registra usando ese ID
    client.post('/login', data={
        'action': 'register',
        'nombre': 'Laura',
        'correo': 'laura@test.com',
        'contrasena': '123456',
        'familia_id': familia_id_real
    }, follow_redirects=True)

    # Usuario2 hace login
    client.post('/login', data={
        'action': 'login',
        'correo': 'laura@test.com',
        'contrasena': '123456'
    }, follow_redirects=True)

    # Usuario2 ve el dashboard
    response = client.get('/dashboard')
    html = response.data.decode()

    assert response.status_code == 200
    assert 'FAMILIA_TEST_2025_UNICA' in html
    assert 'Laura' in html
    assert 'GASTO_UNICO_PARA_PRUEBA_999999' in html or '77.777' in html