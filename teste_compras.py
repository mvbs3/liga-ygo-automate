import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import os
import pytesseract
from PIL import Image
import io
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
cartas_encontradas = []
cartas_nao_encontradas = []

def extrair_preco_com_ocr(elemento):
    png = elemento.screenshot_as_png
    imagem = Image.open(io.BytesIO(png))
    preco = pytesseract.image_to_string(imagem, config='--psm 7')
    return preco.strip()

def espera_elemento(browser, by, value, timeout=5):
    return WebDriverWait(browser, timeout).until(EC.presence_of_element_located((by, value)))

def setup_browser():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)

    stealth(driver,
        languages=["pt-BR", "pt"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL",
        fix_hairline=True,
    )

    return driver

@pytest.fixture
def browser():
    # options = Options()
    # options.add_argument('--headless')  
    # options.add_argument('--disable-gpu')
    # options.add_argument('--no-sandbox')
    # driver = webdriver.Chrome(options=options)
    # yield driver
    # driver.quit()
    driver = setup_browser()
    yield driver
    driver.quit()
def get_cartas():
    cartas = []
    pasta = "lista_de_compras"
    for nome_arquivo in os.listdir(pasta):
        caminho = os.path.join(pasta, nome_arquivo)
        if os.path.isfile(caminho) and nome_arquivo.endswith(".txt"):
            with open(caminho, "r", encoding="utf-8") as f:
                cartas += [linha.strip() for linha in f if linha.strip()]
    return cartas

@pytest.mark.parametrize("carta", get_cartas())
def test_pesquisar_carta(browser, carta):
    browser.get("https://www.ligayugioh.com.br/")
    #espera_elemento(browser, By.ID, "mainsearch")

    try:
        # Fecha banner promocional se existir
        try:
            campanha = espera_elemento(browser, By.ID, "campanha-del-1")
            campanha.click()
            time.sleep(1)
        except:
            pass

        # Fecha banner de cookies se aparecer
        try:
            cookie_banner = espera_elemento(browser, By.CLASS_NAME, "lgpd-button")
            cookie_banner.click()
            time.sleep(1)
        except:
            pass

        with open("page_debug.html", "w", encoding="utf-8") as f:
            f.write(browser.page_source)

        # Pesquisa a carta
        pesquisa = espera_elemento(browser, By.ID, "mainsearch")
        pesquisa.clear()
        pesquisa.send_keys(carta)
        pesquisa.send_keys(Keys.ENTER)

        time.sleep(3)
        # Verifica se há resultados com classe 'box p25'
        boxes = browser.find_elements(By.CLASS_NAME, "box")
        resultados_encontrados = False
        pagina_carta = False

        for box in boxes:
            try:
                link = box.find_element(By.CSS_SELECTOR, ".mtg-name a")
                try:
                    link_aux = box.find_element(By.CSS_SELECTOR, ".mtg-name-aux a")
                    nome_link_aux = link_aux.get_attribute("innerHTML").strip()
                except:
                    nome_link_aux = ""
                nome_link = link.get_attribute("innerHTML").strip()
                if carta.lower() == nome_link.lower() or carta.lower() == nome_link_aux.lower():
                    print(f"Carta encontrada: {nome_link}")
                    print(link.get_attribute("href"))
                    resultados_encontrados = True

                    link.click()
                    print("Redirecionado para a página da carta.")
                    espera_elemento(browser, By.CLASS_NAME, "new-price")  # Espera o preço carregar
                    pagina_carta = True
                    break
            except:
                continue

        if not resultados_encontrados:
            try:
                erro = espera_elemento(browser, By.CLASS_NAME, "alertaErro")
                if erro:
                    print("Nenhuma carta encontrada.")
                    assert False
            except:
                pass
            print("Já estou na página da carta.")
            pagina_carta = True

        if pagina_carta:
            try:
                preco_elemento = espera_elemento(browser, By.CLASS_NAME, "new-price")
                preco = extrair_preco_com_ocr(preco_elemento)
                print(f"Preço da carta '{carta}': {preco}")
                cartas_encontradas.append((carta, preco))
                assert True
            except:
                print(f"Preço não encontrado visualmente para: {carta}")
                cartas_nao_encontradas.append(carta)
                assert False

    except Exception as e:
        print(f"Erro ao pesquisar a carta {carta}: {e}")
        assert False
