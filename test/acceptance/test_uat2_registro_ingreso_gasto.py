# tests/acceptance/test_uat2_registro_ingreso_gasto.py
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

def login(browser, wait, correo, contrasena):
    browser.get("https://walletmoneyfamily.onrender.com/")
    wait.until(EC.presence_of_element_located((By.NAME, "correo")))

    campo_correo = browser.find_element(By.NAME, "correo")
    for letra in correo:
        campo_correo.send_keys(letra)
        time.sleep(0.03)

    campo_pass = browser.find_element(By.NAME, "contrasena")
    for letra in contrasena:
        campo_pass.send_keys(letra)
        time.sleep(0.03)

    time.sleep(1)
    login_btn = browser.find_element(By.ID, "btn-login")
    browser.execute_script("arguments[0].click();", login_btn)

    wait.until(EC.url_contains("/dashboard"))

def registrar_movimiento(browser, wait, tipo, titulo, monto, categoria, descripcion=""):
    tipo_select = Select(browser.find_element(By.NAME, "tipo"))
    tipo_select.select_by_visible_text(tipo)
    time.sleep(1)

    campo_titulo = browser.find_element(By.NAME, "titulo")
    campo_titulo.clear()
    for letra in titulo:
        campo_titulo.send_keys(letra)
        time.sleep(0.03)

    campo_monto = browser.find_element(By.NAME, "monto")
    campo_monto.clear()
    for digito in monto:
        campo_monto.send_keys(digito)
        time.sleep(0.03)

    categoria_select = Select(browser.find_element(By.NAME, "categoria"))
    categoria_select.select_by_visible_text(categoria)
    time.sleep(1)

    campo_desc = browser.find_element(By.NAME, "descripcion")
    campo_desc.clear()
    for letra in descripcion:
        campo_desc.send_keys(letra)
        time.sleep(0.03)

    time.sleep(1)

    if tipo == "Ingreso":
        registrar_btn = browser.find_element(By.ID, "btn-ingreso")
    else:
        registrar_btn = browser.find_element(By.ID, "btn-gasto")

    browser.execute_script("arguments[0].scrollIntoView(true);", registrar_btn)
    time.sleep(1)
    browser.execute_script("arguments[0].click();", registrar_btn)

def test_movimientos_ingreso_gasto(browser):
    wait = WebDriverWait(browser, 60)

    # 1. Login lento y visible
    login(browser, wait, correo="maicoltrujillo1@usuario.com", contrasena="Fv8#Tq92567801!Lm@Xz4p")

    nombre_usuario = "Maicol Trujillo"
    wait.until(EC.visibility_of_element_located((By.XPATH, f"//*[contains(text(), '{nombre_usuario}')]")))
    time.sleep(2)

    # 2. Registrar ingreso lento
    registrar_movimiento(
        browser, wait,
        tipo="Ingreso",
        titulo="Salario Diciembre",
        monto="3000000",
        categoria="Salario",
        descripcion="Salario del mes de diciembre"
    )

    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Ingreso registrado!')]")))
    time.sleep(2)

    # 3. Registrar gasto lento
    registrar_movimiento(
        browser, wait,
        tipo="Gasto",
        titulo="Mercado Semanal",
        monto="150000",
        categoria="Comida",
        descripcion="Alimentación de la semana"
    )

    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Gasto registrado!')]")))
    time.sleep(2)

    # 4. SCROLL AUTOMÁTICO A LA TABLA DE MOVIMIENTOS (MÉTODO INFALIBLE)
    # Buscamos la tabla directamente (no el título)
    tabla_movimientos = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table-hover")))
    
    # Scroll suave y centrado
    browser.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", tabla_movimientos)
    time.sleep(3)  # Pausa para ver el scroll

    # 5. Verificar movimientos
    wait.until(EC.visibility_of_element_located((By.XPATH, "//td[contains(text(), 'Salario Diciembre')]")))
    wait.until(EC.visibility_of_element_located((By.XPATH, "//td[contains(text(), 'Mercado Semanal')]")))
    wait.until(EC.visibility_of_element_located((By.XPATH, f"//small[contains(text(), '{nombre_usuario}')]")))

    # 6. Verificar que el nombre del miembro está en la misma fila
    wait.until(EC.visibility_of_element_located((By.XPATH, f"//tr[td[contains(text(), 'Salario Diciembre')]]//small[contains(text(), '{nombre_usuario}')]")))
    wait.until(EC.visibility_of_element_located((By.XPATH, f"//tr[td[contains(text(), 'Mercado Semanal')]]//small[contains(text(), '{nombre_usuario}')]")))

    time.sleep(5)  # Pausa final para ver todo