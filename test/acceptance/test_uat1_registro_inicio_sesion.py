import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
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

def test_uat1_registro_inicio_sesion(browser):
    wait = WebDriverWait(browser, 60)

    browser.get("https://walletmoneyfamily.onrender.com/")
    time.sleep(2)

    # Clic en "Crear Cuenta Nueva"
    btn_register = wait.until(EC.element_to_be_clickable((By.ID, "btn-register")))
    browser.execute_script("arguments[0].scrollIntoView(true);", btn_register)
    time.sleep(1)
    browser.execute_script("arguments[0].click();", btn_register)
    time.sleep(2)

    # DIGITACIÓN LENTA DEL REGISTRO
    campo_nombre = browser.find_element(By.NAME, "nombre")
    for letra in "Maicol Trujillo":
        campo_nombre.send_keys(letra)
        time.sleep(0.05)

    campo_correo = browser.find_element(By.NAME, "correo")
    for letra in "maicoltrujillo1@usuario.com":
        campo_correo.send_keys(letra)
        time.sleep(0.05)

    campo_pass = browser.find_element(By.NAME, "contrasena")
    for letra in "Fv8#Tq92567801!Lm@Xz4p":
        campo_pass.send_keys(letra)
        time.sleep(0.05)

    campo_familia = browser.find_element(By.NAME, "nueva_familia")
    for letra in "Trujillo Medina":
        campo_familia.send_keys(letra)
        time.sleep(0.05)

    time.sleep(2)

    crear_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Crear Cuenta')]")))
    browser.execute_script("arguments[0].scrollIntoView(true);", crear_btn)
    time.sleep(1)
    browser.execute_script("arguments[0].click();", crear_btn)

    # Esperar que vuelva al login
    wait.until(EC.presence_of_element_located((By.NAME, "correo")))
    time.sleep(3)

    # DIGITACIÓN LENTA DEL LOGIN
    campo_correo_login = browser.find_element(By.NAME, "correo")
    campo_correo_login.clear()
    for letra in "maicoltrujillo1@usuario.com":
        campo_correo_login.send_keys(letra)
        time.sleep(0.05)

    campo_pass_login = browser.find_element(By.NAME, "contrasena")
    campo_pass_login.clear()
    for letra in "Fv8#Tq92567801!Lm@Xz4p":
        campo_pass_login.send_keys(letra)
        time.sleep(0.05)

    time.sleep(2)

    login_btn = wait.until(EC.element_to_be_clickable((By.ID, "btn-login")))
    browser.execute_script("arguments[0].scrollIntoView(true);", login_btn)
    time.sleep(1)
    browser.execute_script("arguments[0].click();", login_btn)

    # Verificar dashboard
    wait.until(EC.url_contains("/dashboard"))
    time.sleep(3)

    # SCROLL FINAL AL NOMBRE DE LA FAMILIA (INFALIBLE)
    # El nombre está dentro de un <span class="fw-bold">
    nombre_familia = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[contains(text(), 'Trujillo Medina')]")))
    browser.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", nombre_familia)
    time.sleep(3)  # Pausa larga para ver el nombre de la familia centrado

    assert "/dashboard" in browser.current_url
    assert "Trujillo Medina" in browser.page_source