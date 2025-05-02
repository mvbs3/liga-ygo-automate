# conftest.py
import json
from teste_compras import cartas_encontradas, cartas_nao_encontradas

def pytest_sessionfinish(session, exitstatus):
    # Cria um dicionário com os resultados das cartas encontradas e não encontradas
    relatorio = {
        "encontradas": cartas_encontradas,  # lista de tuplas (nome, preco)
        "nao_encontradas": cartas_nao_encontradas  # lista de cartas não encontradas
    }
    
    # Salva o relatório em um arquivo JSON
    with open("resultado_cartas.json", "w", encoding="utf-8") as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)
