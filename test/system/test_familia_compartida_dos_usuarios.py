import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture(scope="module")
def browser():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()

    yield driver
    driver.quit()


# -----------------------------------------------------------
# FUNCIONES AUXILIARES
# -----------------------------------------------------------

def register_user(browser, wait, nombre, correo, contrasena, nueva_familia=None, familia_existente=None):
    """Registra un usuario usando nueva familia o seleccionando una existente."""
    browser.get("http://127.0.0.1:5000")

    btn_register = wait.until(EC.element_to_be_clickable((By.ID, "btn-register")))
    browser.execute_script("arguments[0].click();", btn_register)

    wait.until(EC.visibility_of_element_located((By.NAME, "nombre")))
    browser.find_element(By.NAME, "nombre").send_keys(nombre)
    browser.find_element(By.NAME, "correo").send_keys(correo)
    browser.find_element(By.NAME, "contrasena").send_keys(contrasena)

    if nueva_familia:
        browser.find_element(By.NAME, "nueva_familia").send_keys(nueva_familia)

    if familia_existente:
        familia_select = Select(browser.find_element(By.NAME, "familia_id"))
        familia_select.select_by_visible_text(familia_existente)

    crear_btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Crear Cuenta')]")
    browser.execute_script("arguments[0].click();", crear_btn)


def login(browser, wait, correo, contrasena):
    wait.until(EC.presence_of_element_located((By.NAME, "correo")))
    browser.find_element(By.NAME, "correo").send_keys(correo)
    browser.find_element(By.NAME, "contrasena").send_keys(contrasena)

    login_btn = browser.find_element(By.ID, "btn-login")
    browser.execute_script("arguments[0].click();", login_btn)


def registrar_movimiento(browser, wait, tipo, titulo, monto, categoria, descripcion):
    tipo_select = Select(browser.find_element(By.NAME, "tipo"))
    tipo_select.select_by_visible_text(tipo)

    browser.find_element(By.NAME, "titulo").send_keys(titulo)
    browser.find_element(By.NAME, "monto").send_keys(monto)

    categoria_select = Select(browser.find_element(By.NAME, "categoria"))
    categoria_select.select_by_visible_text(categoria)

    browser.find_element(By.NAME, "descripcion").send_keys(descripcion)

    registrar_btn = browser.find_element(By.CSS_SELECTOR, "button.btn-success")
    browser.execute_script("arguments[0].click();", registrar_btn)


# -----------------------------------------------------------
# TEST PRINCIPAL
# -----------------------------------------------------------

def test_familia_compartida_dos_usuarios(browser):
    wait = WebDriverWait(browser, 20)

    
    # Registro usuario 1 crea nueva familia
   
    register_user(
        browser, wait,
        nombre="Selenium FINAL 1",
        correo="final11@test.com",
        contrasena="Fv8#Tq925!Lm@Xz4p",
        nueva_familia="Familia Exterminas"
    )

    login(browser, wait, "final11@test.com", "Fv8#Tq925!Lm@Xz4p")
    wait.until(EC.url_contains("/dashboard"))
    assert "Selenium FINAL 1" in browser.page_source

    # Registrar gasto
    registrar_movimiento(
        browser, wait,
        tipo="Gasto",
        titulo="Netflix 8K",
        monto="99000",
        categoria="Entretenimiento",
        descripcion="Prueba final"
    )

    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'Netflix 8K')]")))

    # Cerrar sesión
    cerrar = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Cerrar Sesión")))
    browser.execute_script("arguments[0].click();", cerrar)
    assert "Login" in browser.title

   
    # Registro usuario 2 usa familia usada por usuario 1
 
    register_user(
        browser, wait,
        nombre="Selenium FINAL 2",
        correo="final22@test.com",
        contrasena="Fv8#Tq925!Lm@Xz4p",
        familia_existente="Familia Exterminas"
    )

    login(browser, wait, "final22@test.com", "Fv8#Tq925!Lm@Xz4p")
    wait.until(EC.url_contains("/dashboard"))
    assert "Selenium FINAL 2" in browser.page_source

    # Registrar ingreso
    registrar_movimiento(
        browser, wait,
        tipo="Ingreso",
        titulo="Beca Universidad",
        monto="1500000",
        categoria="Otros",
        descripcion="Ingreso automático"
    )

    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'Beca Universidad')]")))

    # Cerrar sesión
    cerrar = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Cerrar Sesión")))
    browser.execute_script("arguments[0].click();", cerrar)

    assert "Login" in browser.title
