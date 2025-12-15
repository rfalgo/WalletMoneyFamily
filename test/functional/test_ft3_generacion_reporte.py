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

def test_ft3_generacion_reporte(browser):
    wait = WebDriverWait(browser, 60)

    # 1. Iniciar sesión
    browser.get("https://walletmoneyfamily.onrender.com/")
    
    wait.until(EC.presence_of_element_located((By.NAME, "correo")))
    browser.find_element(By.NAME, "correo").send_keys("tatianalandazury@usuario.com")
    browser.find_element(By.NAME, "contrasena").send_keys("Fv8#Tq92567801!Lm@Xz4p")
    
    login_btn = browser.find_element(By.ID, "btn-login")
    browser.execute_script("arguments[0].click();", login_btn)
    
    wait.until(EC.url_contains("/dashboard"))
    time.sleep(3)

    # 2. Verificar movimientos
    assert "Ingreso" in browser.page_source or "Gasto" in browser.page_source

    # 3. Scroll al gráfico de barras
    bar_chart = wait.until(EC.visibility_of_element_located((By.ID, "barChart")))
    browser.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", bar_chart)
    time.sleep(3)

    # 4. Scroll al gráfico de pastel
    pie_chart = browser.find_element(By.ID, "pieChart")
    browser.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", pie_chart)
    time.sleep(3)

    # 5. SCROLL AL GRÁFICO DE LÍNEA (evolución del saldo)
    line_chart = wait.until(EC.visibility_of_element_located((By.ID, "lineChart")))
    browser.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", line_chart)
    time.sleep(5)  # Pausa larga para ver el gráfico de línea bien

    # 6. SCROLL FINAL A LA TABLA DE ÚLTIMOS MOVIMIENTOS
    tabla_movimientos = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table.table-hover")))
    browser.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", tabla_movimientos)
    time.sleep(6)  # Pausa extra larga para que se vea claramente la tabla al final

    # Verificaciones finales
    assert line_chart.is_displayed()
    assert tabla_movimientos.is_displayed()
    assert "Últimos 10 movimientos" in browser.page_source

