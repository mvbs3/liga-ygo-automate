# conftest.py
import json
from teste_compras import cartas_encontradas, cartas_nao_encontradas

def pytest_sessionfinish(session, exitstatus):
    print("pytest_sessionfinish chamada")  # Para garantir que a função está sendo chamada
    relatorio = {
        "encontradas": cartas_encontradas,
        "nao_encontradas": cartas_nao_encontradas
    }
    with open("resultado_cartas.json", "w", encoding="utf-8") as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)