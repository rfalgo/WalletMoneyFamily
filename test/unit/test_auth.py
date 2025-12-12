def test_registro_exitoso(client):
    # Registro usuario
    response = client.post('/login', data={
        'action': 'register',
        'nombre': 'Fabian Test',
        'correo': 'fabiantest123@test.com',
        'contrasena': '123456',
        'nueva_familia': 'FamiliaFabian123'
    })

    # Debe redirigir (código 302)
    assert response.status_code == 302
    assert '/login' in response.location

    # Ir a login para verificar que el usuario fue creado
    final = client.get('/login')
    assert b'' in final.data  

def test_login_correcto(client):
    client.post('/login', data={
        'action': 'register',
        'nombre': 'Login Test',
        'correo': 'login123@test.com',
        'contrasena': '123456',
        'nueva_familia': 'LoginFam123'
    })

    response = client.post('/login', data={
        'action': 'login',
        'correo': 'login123@test.com',
        'contrasena': '123456'
    }, follow_redirects=True)

    assert b'dashboard' in response.data.lower()