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


def test_sistema_completo_flujo_completo(browser):
    wait = WebDriverWait(browser, 20)

    browser.get("http://127.0.0.1:5000")

    # Registro manual usuario 
    btn_register = wait.until(EC.element_to_be_clickable((By.ID, "btn-register")))
    browser.execute_script("arguments[0].click();", btn_register)
    time.sleep(2)

    wait.until(EC.visibility_of_element_located((By.NAME, "nombre")))
    browser.find_element(By.NAME, "nombre").send_keys("Selenium FINAL")
    browser.find_element(By.NAME, "correo").send_keys("final123334567801@test.com")
    browser.find_element(By.NAME, "contrasena").send_keys("Fv8#Tq92567801!Lm@Xz4p")
    browser.find_element(By.NAME, "nueva_familia").send_keys("Familia FINAL2026190123")

    crear_btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Crear Cuenta')]")
    browser.execute_script("arguments[0].click();", crear_btn)
    time.sleep(6)

    # Registro completo, ahora hacer login
    wait.until(EC.presence_of_element_located((By.NAME, "correo")))
    browser.find_element(By.NAME, "correo").clear()
    browser.find_element(By.NAME, "correo").send_keys("final123334567801@test.com")
    browser.find_element(By.NAME, "contrasena").clear()
    browser.find_element(By.NAME, "contrasena").send_keys("Fv8#Tq92567801!Lm@Xz4p")

    login_btn = browser.find_element(By.ID, "btn-login")
    browser.execute_script("arguments[0].click();", login_btn)
    time.sleep(10)

    # Verificar que está en el dashboard
    assert "/dashboard" in browser.current_url
    assert "Selenium FINAL" in browser.page_source


    # Registrar Ingreso 
    browser.find_element(By.NAME, "titulo").send_keys("Sueldo Diciembre")
    browser.find_element(By.NAME, "monto").send_keys("6000000")
    browser.find_element(By.NAME, "categoria").send_keys("Salario")
    browser.find_element(By.NAME, "descripcion").send_keys("Ingreso automático")
    
    registrar_btn = browser.find_element(By.CSS_SELECTOR, "button.btn-success")
    browser.execute_script("arguments[0].click();", registrar_btn)
    time.sleep(5)

    assert "Sueldo Diciembre" in browser.page_source

    # Registrar Gasto
    tipo_select = Select(browser.find_element(By.NAME, "tipo"))
    tipo_select.select_by_visible_text("Gasto")
    time.sleep(2)  # Espera a que cambie el botón

    browser.find_element(By.NAME, "titulo").send_keys("Netflix 8K")
    browser.find_element(By.NAME, "monto").send_keys("99000")
    browser.find_element(By.NAME, "categoria").send_keys("Entretenimiento")
    browser.find_element(By.NAME, "descripcion").send_keys("Prueba final")

    registrar_btn = browser.find_element(By.CSS_SELECTOR, "button.btn-success")
    browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", registrar_btn)
    time.sleep(1)
    browser.execute_script("arguments[0].click();", registrar_btn)
    time.sleep(5)

    assert "Netflix 8K" in browser.page_source

    # Eliminar último movimiento
    eliminar_btn = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//button[contains(@class, 'btn-danger') and contains(., 'Eliminar último movimiento')]"
    )))
    browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", eliminar_btn)
    time.sleep(1)
    browser.execute_script("arguments[0].click();", eliminar_btn)

    # Aceptar la alerta de confirmación
    WebDriverWait(browser, 10).until(EC.alert_is_present())
    browser.switch_to.alert.accept()

    # Verificar que el movimiento ya no está
    browser.refresh()
    time.sleep(4)

    assert "Netflix 8K" not in browser.page_source

    # Cerrar sesión
    cerrar = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Cerrar Sesión")))
    browser.execute_script("arguments[0].click();", cerrar)
    time.sleep(2)

    assert "Login" in browser.title
    