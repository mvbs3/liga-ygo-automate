import json
import logging
import os
from teste_compras import cartas_encontradas, cartas_nao_encontradas

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def pytest_sessionstart(session):
    """Executa antes de iniciar os testes"""
    logger.info("Iniciando a sessão de testes")
    
    # Verifica se o diretório de lista_de_compras existe
    if not os.path.exists("lista_de_compras"):
        logger.warning("Diretório lista_de_compras não encontrado. Criando...")
        os.makedirs("lista_de_compras")
        # Cria um arquivo de exemplo se necessário
        with open("lista_de_compras/exemplo.txt", "w", encoding="utf-8") as f:
            f.write("Dark Magician\nBlue-Eyes White Dragon")

def pytest_sessionfinish(session, exitstatus):
    """Executa após finalizar os testes"""
    logger.info("Finalizando a sessão de testes")
    
    # Criar o relatório
    relatorio = {
        "encontradas": cartas_encontradas,
        "nao_encontradas": cartas_nao_encontradas
    }
    
    # Salvar o relatório em JSON
    try:
        with open("resultado_cartas.json", "w", encoding="utf-8") as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        logger.info(f"Relatório salvo: {len(cartas_encontradas)} cartas encontradas, {len(cartas_nao_encontradas)} não encontradas")
    except Exception as e:
        logger.error(f"Erro ao salvar relatório: {e}")
    
    # Criar um relatório em formato texto também (para debug)
    try:
        with open("resultado_cartas.txt", "w", encoding="utf-8") as f:
            f.write("✅ CARTAS ENCONTRADAS:\n")
            for carta, preco in cartas_encontradas:
                f.write(f"- {carta}: R$ {preco}\n")
            
            f.write("\n❌ CARTAS NÃO ENCONTRADAS:\n")
            for carta in cartas_nao_encontradas:
                f.write(f"- {carta}\n")
        logger.info("Relatório de texto criado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao criar relatório de texto: {e}")