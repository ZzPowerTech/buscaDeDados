import json
from collections import Counter
from dateutil import parser as dateparser

# Caminho para o JSON que o seu script gerou
JSON_FILE = "collected_articles_bbas3.json"

# Carrega os dados
with open(JSON_FILE, "r", encoding="utf-8") as f:
    articles = json.load(f)

total = len(articles)
paywalled = sum(1 for a in articles if a.get("article_extraction", {}).get("paywalled"))
sentiments = Counter(a.get("article_extraction", {}).get("sentiment", {}).get("label", "neutral") for a in articles)

# Contagem por ano
years = Counter()
for a in articles:
    pubdate = a.get("article_extraction", {}).get("pubdate")
    if pubdate:
        try:
            dt = dateparser.parse(pubdate)
            years[dt.year] += 1
        except:
            pass

# Impressão do resumo
print("=== Resumo dos Artigos Coletados ===")
print(f"Total de artigos: {total}")
print(f"Artigos paywalled: {paywalled}")
print("Distribuição de sentimento:")
for k, v in sentiments.items():
    print(f"  {k}: {v}")
print("Artigos por ano:")
for y, c in sorted(years.items()):
    print(f"  {y}: {c}")
