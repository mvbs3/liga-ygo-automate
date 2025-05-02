# test_compras.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time

@pytest.fixture
def browser():
    options = Options()
    #options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

def get_cartas():
    with open("cartas.txt", "r", encoding="utf-8") as f:
        return [linha.strip() for linha in f if linha.strip()]

@pytest.mark.parametrize("carta", get_cartas())
def test_adicionar_ao_carrinho(browser, carta):
    browser.get("https://www.ligayugioh.com.br/")
    time.sleep(1)
    try:
        retultados = browser.find_elements(By.ID, "campanha-del-1")
        retultados[0].click()
        time.sleep(3)
        pesquisa = browser.find_element(By.ID, "mainsearch")
        pesquisa.send_keys(carta)
        pesquisa.send_keys(Keys.ENTER)
        time.sleep(2)
    except Exception:
            print(f"{carta} está fora de estoque ou não encontrada.")

   