import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pytesseract
from PIL import Image
import io
import os

def extrair_preco_com_ocr(elemento):
    png = elemento.screenshot_as_png
    imagem = Image.open(io.BytesIO(png))
    preco = pytesseract.image_to_string(imagem, config='--psm 7')
    return preco.strip()

@pytest.fixture
def browser():
    options = Options()
    #options.add_argument('--headless')  # Ative se quiser rodar sem abrir o navegador
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

def get_cartas():
    with open("cartas.txt", "r", encoding="utf-8") as f:
        return [linha.strip() for linha in f if linha.strip()]

@pytest.mark.parametrize("carta", get_cartas())
def test_pesquisar_carta(browser, carta):
    browser.get("https://www.ligayugioh.com.br/")
    time.sleep(1)

    try:
        # Fecha banner promocional se existir
        try:
            campanha = browser.find_element(By.ID, "campanha-del-1")
            campanha.click()
            time.sleep(1)
        except:
            pass  # Se não existir, segue normalmente

        # Fechar banner de cookies, se aparecer
        try:
            cookie_banner = browser.find_element(By.CLASS_NAME, "lgpd-button")
            
            cookie_banner.click()  # Ou encontre o botão de fechar
            time.sleep(1)
        except:
            pass  # Caso não haja banner, continue normalmente

        # Pesquisa a carta
        pesquisa = browser.find_element(By.ID, "mainsearch")
        pesquisa.clear()
        pesquisa.send_keys(carta)
        pesquisa.send_keys(Keys.ENTER)
        time.sleep(3)

        # Verifica se há resultados com classe 'box p25'
        boxes = browser.find_elements(By.CSS_SELECTOR, ".box.p25")
        resultados_encontrados = False
        pagina_carta = False

        for box in boxes:
            try:
                link = box.find_element(By.CSS_SELECTOR, ".mtg-name a")
                nome_link = link.get_attribute("innerHTML").strip()
                if carta.lower() == nome_link.lower():
                    print(f"Carta encontrada: {nome_link}")
                    print(link.get_attribute("href"))
                    resultados_encontrados = True
                    
                    link.click()  # Clica no link da carta

                    print("Redirecionado para a página da carta.")
                    pagina_carta = True
                    time.sleep(5)
                    break  # Interrompe o loop após clicar
            except Exception as e:
                print(f"Erro ao clicar no link: {e}")
                continue

        if not resultados_encontrados:
            try:
                erro = browser.find_element(By.CLASS_NAME, "alertaErro")
                if(erro):
                    print("Nenhuma carta encontrada.")
                    assert False
            except:
                pass
            print("Já estou na página da carta.")
            pagina_carta = True
        if pagina_carta:
            #cards_preco = browser.find_elements(By.CLASS_NAME, "store")
            #print(cards_preco[0].get_attribute("outerHTML"))
            #card = cards_preco[0]
            # Captura e exibe o preço com OCR
            try:
                preco_elemento = browser.find_element(By.CLASS_NAME, "new-price")
                preco = extrair_preco_com_ocr(preco_elemento)
                print(f"Preço da carta '{carta}': {preco}")
            except:
                print(f"Preço não encontrado visualmente para: {carta}")


        time.sleep(5)
        assert True
    except Exception as e:
        print(f"Erro ao pesquisar a carta {carta}: {e}")
        assert False


