import json
from collections import Counter
from dateutil import parser as dateparser
import statistics

# Caminho para o JSON que o seu script gerou
JSON_FILE = "collected_articles_bbas3.json"

# Carrega os dados
with open(JSON_FILE, "r", encoding="utf-8") as f:
    articles = json.load(f)

total = len(articles)

# Análise de sentimentos aprimorada
sentiments = Counter(a.get("sentimentos", {}).get("label", "neutral") for a in articles)
polarities = [a.get("sentimentos", {}).get("polarity", 0.0) for a in articles]
subjectivities = [a.get("sentimentos", {}).get("subjectivity", 0.0) for a in articles]
confidences = [a.get("sentimentos", {}).get("confidence", 0.0) for a in articles]

# Artigos mais positivos e negativos
articles_sorted = sorted(articles, key=lambda x: x.get("sentimentos", {}).get("polarity", 0.0))
most_negative = articles_sorted[:3]
most_positive = articles_sorted[-3:]

# Contagem por ano
years = Counter()
for a in articles:
    pubdate = a.get("publicada")
    if pubdate:
        try:
            dt = dateparser.parse(pubdate)
            years[dt.year] += 1
        except:
            pass

# Sentimento médio por query
sentiment_by_query = {}
for a in articles:
    query = a.get("query", "desconhecido")
    if query not in sentiment_by_query:
        sentiment_by_query[query] = []
    sentiment_by_query[query].append(a.get("sentimentos", {}).get("polarity", 0.0))

query_avg_sentiment = {
    q: round(statistics.mean(pols), 4) if pols else 0.0
    for q, pols in sentiment_by_query.items()
}

# Impressão do resumo
print("="*60)
print("=== ANÁLISE DE SENTIMENTOS - BBAS3/Banco do Brasil ===")
print("="*60)
print(f"\nTotal de artigos analisados: {total}")

print("\n--- Distribuição de Sentimento ---")
for k, v in sorted(sentiments.items(), key=lambda x: x[1], reverse=True):
    percentage = (v/total)*100 if total > 0 else 0
    print(f"  {k.capitalize():12s}: {v:3d} ({percentage:5.1f}%)")

print("\n--- Métricas de Polaridade ---")
print(f"  Polaridade média:    {statistics.mean(polarities):7.4f}")
print(f"  Polaridade mediana:  {statistics.median(polarities):7.4f}")
print(f"  Desvio padrão:       {statistics.stdev(polarities) if len(polarities) > 1 else 0:7.4f}")
print(f"  Mínimo (negativo):   {min(polarities):7.4f}")
print(f"  Máximo (positivo):   {max(polarities):7.4f}")

print("\n--- Métricas de Confiança ---")
print(f"  Confiança média:     {statistics.mean(confidences):7.4f}")
print(f"  Subjetividade média: {statistics.mean(subjectivities):7.4f}")

print("\n--- Sentimento Médio por Query ---")
for query, avg_pol in sorted(query_avg_sentiment.items(), key=lambda x: x[1], reverse=True):
    sentiment_label = "positivo" if avg_pol > 0.05 else "negativo" if avg_pol < -0.05 else "neutro"
    print(f"  {avg_pol:7.4f} ({sentiment_label:8s}): {query[:50]}")

print("\n--- Artigos Mais NEGATIVOS ---")
for i, a in enumerate(most_negative, 1):
    pol = a.get("sentimentos", {}).get("polarity", 0.0)
    title = a.get("titulo_noticia", "Sem título")[:70]
    print(f"  [{i}] {pol:7.4f} - {title}...")

print("\n--- Artigos Mais POSITIVOS ---")
for i, a in enumerate(reversed(most_positive), 1):
    pol = a.get("sentimentos", {}).get("polarity", 0.0)
    title = a.get("titulo_noticia", "Sem título")[:70]
    print(f"  [{i}] {pol:7.4f} - {title}...")

print("\n--- Artigos por Ano ---")
for y, c in sorted(years.items()):
    print(f"  {y}: {c} artigos")

print("\n" + "="*60)
