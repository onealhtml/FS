"""
🕷️ Oficina de Web Scraping - Script de Demonstração
====================================================
Este script coleta citações do site quotes.toscrape.com
e salva em um arquivo CSV.

Requisitos: pip install requests beautifulsoup4
"""

import requests
from bs4 import BeautifulSoup
import csv

# 1. Acessar o site
print("🌐 Acessando o site quotes.toscrape.com...")
resposta = requests.get("https://quotes.toscrape.com/")
print(f"   Status: {resposta.status_code} (200 = sucesso!)\n")

# 2. Ler o HTML com BeautifulSoup
soup = BeautifulSoup(resposta.text, "html.parser")

# 3. Encontrar todas as citações
citacoes = soup.find_all("div", class_="quote")
print(f"📋 Encontradas {len(citacoes)} citações!\n")
print("-" * 60)

# 4. Extrair dados de cada citação
dados = []
for i, citacao in enumerate(citacoes, 1):
    texto = citacao.find("span", class_="text").get_text()
    autor = citacao.find("small", class_="author").get_text()
    tags = [tag.get_text() for tag in citacao.find_all("a", class_="tag")]

    dados.append({
        "texto": texto,
        "autor": autor,
        "tags": ", ".join(tags)
    })

    print(f'{i}. "{texto[:60]}..."')
    print(f"   ✍️  {autor}")
    print(f"   🏷️  Tags: {', '.join(tags)}\n")

# 5. Salvar em CSV
with open("citacoes.csv", "w", newline="", encoding="utf-8") as arquivo:
    escritor = csv.DictWriter(arquivo, fieldnames=["texto", "autor", "tags"])
    escritor.writeheader()
    escritor.writerows(dados)

print("-" * 60)
print(f"✅ {len(dados)} citações salvas em 'citacoes.csv'!")
print("📊 Agora você pode abrir no Excel ou Google Sheets.")
