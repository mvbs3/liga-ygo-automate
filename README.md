
📦 Projeto: liga-ygo-automate

Este projeto automatiza o monitoramento de preços e disponibilidade de cartas de Yu-Gi-Oh! na plataforma Liga Yu-Gi-Oh, que reúne diversas lojas do Brasil em um só lugar.

💡 Motivação:
No Brasil, os preços das cartas de Yu-Gi-Oh! funcionam como uma verdadeira bolsa de valores: mudam constantemente com base em popularidade, meta do jogo, estoque, entre outros. Acompanhar isso manualmente todos os dias é cansativo, especialmente se você está de olho em várias cartas para compra ou venda.

✅ O que esse app faz:
- A partir de uma lista .txt com os nomes das cartas que você deseja monitorar;
- Roda todos os dias automaticamente às 9h da manhã (via GitHub Actions);
- Acessa o site da Liga Yu-Gi-Oh usando automação com Selenium;
- Verifica se as cartas estão disponíveis e seus preços mais baixos;
- Gera um relatório e envia um email automático com o resumo das cartas encontradas e não encontradas.

📚 Tecnologias utilizadas:
- Python
- Selenium
- PyTest
- GitHub Actions (para agendamento e execução automática)

📦 Instalação local:

1. Crie o ambiente virtual:
    python3 -m venv venv
    source venv/bin/activate

2. Instale os requisitos:
    pip install -r requirements.txt

3. Rode os testes:
    pytest teste_compras.py
    # ou use a flag -s para ver os prints no terminal
    pytest -s teste_compras.py

🛠 Dica para runners self-hosted:
Se estiver usando runs-on: self-hosted, e o GitHub Actions pedir sudo, adicione permissões de root ao runner ou ajuste os comandos que necessitam de sudo para evitar prompts (modifique com responsabilidade e segurança).

📩 Saída esperada por email:
📊 Resultado da busca de cartas 📊

✅ Cartas encontradas:
- Vanquish Soul Dr. Mad Love: R$ 1,50
- Dark Magician: R$ 29,98

❌ Cartas não encontradas:
- Vanquish Soul Jiaolong

Desenvolvido por Marcelo Victor 💙