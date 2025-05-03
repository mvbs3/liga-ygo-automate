import pytest
import time
import os
import io
import json
import random
import subprocess
import shutil
import logging
from PIL import Image
import pytesseract
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Variáveis globais para armazenar resultados
cartas_encontradas = []
cartas_nao_encontradas = []

def extrair_preco_com_ocr(elemento):
    png = elemento.screenshot_as_png
    imagem = Image.open(io.BytesIO(png))
    preco = pytesseract.image_to_string(imagem, config='--psm 7')
    return preco.strip()

def espera_elemento(browser, by, value, timeout=10):
    try:
        return WebDriverWait(browser, timeout).until(EC.presence_of_element_located((by, value)))
    except Exception as e:
        logger.warning(f"Elemento não encontrado: {by}={value}, erro: {e}")
        return None

def random_delay(min_seconds=3, max_seconds=7):
    """Adiciona um delay aleatório para simular comportamento humano"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)

def get_cartas():
    """Obtém a lista de cartas a serem pesquisadas"""
    cartas = []
    pasta = "lista_de_compras"
    for nome_arquivo in os.listdir(pasta):
        caminho = os.path.join(pasta, nome_arquivo)
        if os.path.isfile(caminho) and nome_arquivo.endswith(".txt"):
            with open(caminho, "r", encoding="utf-8") as f:
                cartas += [linha.strip() for linha in f if linha.strip()]
    return cartas

def setup_undetected_browser():
    options = Options()
    #options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')  # Importante para GitHub Actions
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36')
    
    # Verificar se estamos rodando no GitHub Actions
    if os.environ.get('GITHUB_ACTIONS'):
        # Configurações específicas para o GitHub Actions
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-extensions')
        
    driver = webdriver.Chrome(options=options)
    
    # Esconder sinais de automação
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

@pytest.fixture
def browser():
    try:
        driver = setup_undetected_browser()
        yield driver
    except Exception as e:
        logger.error(f"Erro ao configurar o navegador: {e}")
        raise
    finally:
        try:
            if 'driver' in locals():
                driver.quit()
        except:
            pass

def resolver_captcha(browser):
    """Função básica para detectar e lidar com captchas"""
    try:
        # Verificar se há um iframe de reCAPTCHA
        if len(browser.find_elements(By.XPATH, "//iframe[contains(@src, 'recaptcha')]")) > 0:
            logger.warning("reCAPTCHA detectado! Aguardando 30 segundos para intervenção manual.")
            # Em produção, você poderia usar um serviço de resolução de captcha
            time.sleep(30)
            return True
            
        # Verificar se há desafio Cloudflare
        if "Checking your browser" in browser.page_source or "cloudflare" in browser.page_source.lower():
            logger.warning("Desafio Cloudflare detectado! Aguardando 30 segundos.")
            time.sleep(30)
            return True
            
    except Exception as e:
        logger.error(f"Erro ao verificar captcha: {e}")
    
    return False

@pytest.mark.parametrize("carta", get_cartas())
def test_pesquisar_carta(browser, carta):
    try:
        # Usar uma rotação de user agents para cada requisição
        ua = UserAgent()
        browser.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": ua.random})
        
        # Adicionar delay aleatório antes de iniciar
        random_delay(3, 7)
        
        # Acessar o site com parâmetros aleatórios para evitar cache
        timestamp = int(time.time())
        browser.get(f"https://www.ligayugioh.com.br/?t={timestamp}")
        
        # Verificar se há captcha ou desafio Cloudflare
        if resolver_captcha(browser):
            logger.info("Tentando novamente após resolver captcha/desafio")
        
        # Salvar HTML para debug
        with open("page_debug.html", "w", encoding="utf-8") as f:
            f.write(browser.page_source)
        
        # Fechar banners e pop-ups
        try:
            # Banner de promoção
            campanha = espera_elemento(browser, By.ID, "campanha-del-1")
            if campanha and campanha.is_displayed():
                campanha.click()
                random_delay(1, 2)
        except:
            pass
            
        try:
            # Banner de cookies
            cookie_banner = espera_elemento(browser, By.CLASS_NAME, "lgpd-button")
            if cookie_banner and cookie_banner.is_displayed():
                cookie_banner.click()
                random_delay(1, 2)
        except:
            pass
        
        # Aguardar carregamento do campo de pesquisa
        pesquisa = espera_elemento(browser, By.ID, "mainsearch")
        if not pesquisa:
            logger.error(f"Campo de pesquisa não encontrado para carta: {carta}")
            cartas_nao_encontradas.append(carta)
            assert False, "Campo de pesquisa não encontrado"
        
        # Simular digitação humana mais realista
        for caractere in carta:
            pesquisa.send_keys(caractere)
            time.sleep(random.uniform(0.05, 0.2))
        
        random_delay(1, 2)
        pesquisa.send_keys(Keys.ENTER)
        
        # Aguardar resultados
        random_delay(3, 7)
        
        # Verificar se há resultados ou redirecionamento direto
        boxes = browser.find_elements(By.CLASS_NAME, "box")
        resultados_encontrados = False
        pagina_carta = False
        
        # Se houver resultados de pesquisa, encontrar a carta correta
        if boxes:
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
                        logger.info(f"Carta encontrada: {nome_link}")
                        resultados_encontrados = True
                        
                        # Simular comportamento humano: move para o elemento antes de clicar
                        browser.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", link)
                        random_delay(1, 2)
                        
                        link.click()
                        logger.info("Redirecionado para a página da carta.")
                        random_delay(2, 5)
                        pagina_carta = True
                        break
                except Exception as e:
                    logger.debug(f"Erro ao processar box: {e}")
                    continue
        
        # Verificar se estamos na página da carta
        if not resultados_encontrados:
            try:
                erro = espera_elemento(browser, By.CLASS_NAME, "alertaErro")
                if erro:
                    logger.warning(f"Carta não encontrada: {carta}")
                    cartas_nao_encontradas.append(carta)
                    assert False, f"Carta não encontrada: {carta}"
            except:
                # Pode ser que já estejamos na página da carta
                pass
            logger.info("Verificando se já estamos na página da carta.")
            pagina_carta = True
        
        # Extrair preço se estiver na página da carta
        if pagina_carta:
            try:
                # Aguardar e tentar encontrar o preço várias vezes
                for tentativa in range(3):
                    preco_elemento = espera_elemento(browser, By.CLASS_NAME, "new-price")
                    if preco_elemento:
                        random_delay(1, 2)
                        preco = extrair_preco_com_ocr(preco_elemento)
                        if preco:
                            logger.info(f"Preço da carta '{carta}': {preco}")
                            cartas_encontradas.append((carta, preco))
                            assert True
                            return
                        else:
                            logger.warning(f"OCR falhou na tentativa {tentativa+1}")
                            random_delay(2, 3)
                    else:
                        random_delay(2, 3)
                
                # Se chegou até aqui, não conseguiu extrair o preço
                logger.error(f"Preço não encontrado para: {carta}")
                cartas_nao_encontradas.append(carta)
                assert False, f"Preço não encontrado para: {carta}"
                
            except Exception as e:
                logger.error(f"Erro ao extrair preço para {carta}: {e}")
                cartas_nao_encontradas.append(carta)
                assert False, f"Erro ao extrair preço: {e}"
        else:
            logger.error(f"Não foi possível acessar a página da carta: {carta}")
            cartas_nao_encontradas.append(carta)
            assert False, "Não foi possível acessar a página da carta"
            
    except Exception as e:
        logger.error(f"Erro inesperado ao pesquisar a carta {carta}: {e}")
        cartas_nao_encontradas.append(carta)
        assert False, f"Erro inesperado: {e}"