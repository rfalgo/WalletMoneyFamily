def test_registrar_ingreso_gasto_y_eliminar_movimiento(client):
    """
    Prueba de integración completa:
    Registro → Ingreso → Gasto → Eliminar último → Verificar saldo actualizado
    """

    # Registro Y Login 
    client.post('/login', data={
        'action': 'register',
        'nombre': 'Luis',
        'correo': 'luis@wallet.com',
        'contrasena': '123456',
        'nueva_familia': 'Familia Luis 2025'
    }, follow_redirects=True)

    client.post('/login', data={
        'action': 'login',
        'correo': 'luis@wallet.com',
        'contrasena': '123456'
    }, follow_redirects=True)

    # Registar Ingreso
    client.post('/dashboard', data={
        'tipo': 'ingreso',
        'titulo': 'Salario Diciembre',
        'monto': '3500000',
        'miembro': 'Luis',
        'categoria': 'Salario'
    }, follow_redirects=True)

    # Registrar Gasto
    client.post('/dashboard', data={
        'tipo': 'gasto',
        'titulo': 'Supermercado Navidad',
        'monto': '220000',
        'miembro': 'Luis',
        'categoria': 'Comida'
    }, follow_redirects=True)

    # Verificar que el saldo es 3.280.000
    response = client.get('/dashboard')
    html = response.get_data(as_text=True)
    assert '3.280.000' in html or '3280000' in html

    # Eliminar el último movimiento 
    response_eliminar = client.post('/eliminar_ultimo', follow_redirects=True)

    # Verificar mensaje de éxito
    assert b'eliminado' in response_eliminar.data.lower() or b'correctamente' in response_eliminar.data.lower()

    # Verificar que el saldo es 3.500.000
    final = client.get('/dashboard')
    html_final = final.get_data(as_text=True)

    assert '3.500.000' in html_final or '3500000' in html_final
    assert 'Supermercado Navidad' not in html_final 

    assert final.status_code == 200