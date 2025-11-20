"""
Análise detalhada de sentimentos com exemplos específicos e contexto
"""
import json
from collections import Counter, defaultdict
from dateutil import parser as dateparser
import statistics
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
JSON_FILE = BASE_DIR / "data" / "collected_articles_bbas3.json"

# Carrega os dados
with open(JSON_FILE, "r", encoding="utf-8") as f:
    articles = json.load(f)

print("="*80)
print("ANÁLISE DETALHADA DE SENTIMENTOS - BBAS3/Banco do Brasil")
print("="*80)

# Separa artigos por categoria de sentimento
positive_articles = [a for a in articles if a.get("sentimentos", {}).get("label") == "positive"]
negative_articles = [a for a in articles if a.get("sentimentos", {}).get("label") == "negative"]
neutral_articles = [a for a in articles if a.get("sentimentos", {}).get("label") == "neutral"]

print(f"\n📊 RESUMO GERAL:")
print(f"   Total de artigos: {len(articles)}")
print(f"   ✅ Positivos: {len(positive_articles)} ({len(positive_articles)/len(articles)*100:.1f}%)")
print(f"   ❌ Negativos: {len(negative_articles)} ({len(negative_articles)/len(articles)*100:.1f}%)")
print(f"   ⚪ Neutros: {len(neutral_articles)} ({len(neutral_articles)/len(articles)*100:.1f}%)")

# Análise de palavras-chave
print(f"\n🔍 ANÁLISE DE PALAVRAS-CHAVE:")
total_pos_keywords = sum(a.get("sentimentos", {}).get("positive_keywords", 0) for a in articles)
total_neg_keywords = sum(a.get("sentimentos", {}).get("negative_keywords", 0) for a in articles)
print(f"   Palavras-chave positivas detectadas: {total_pos_keywords}")
print(f"   Palavras-chave negativas detectadas: {total_neg_keywords}")
print(f"   Ratio positivo/negativo: {total_pos_keywords/total_neg_keywords if total_neg_keywords > 0 else 'N/A':.2f}")

# Top 10 artigos mais polarizados
print(f"\n📰 TOP 10 ARTIGOS MAIS POSITIVOS:")
top_positive = sorted(positive_articles, 
                     key=lambda x: x.get("sentimentos", {}).get("polarity", 0), 
                     reverse=True)[:10]
for i, a in enumerate(top_positive, 1):
    sent = a.get("sentimentos", {})
    title = a.get("titulo_noticia", "Sem título")[:65]
    pol = sent.get("polarity", 0)
    conf = sent.get("confidence", 0)
    pos_kw = sent.get("positive_keywords", 0)
    neg_kw = sent.get("negative_keywords", 0)
    pub = a.get("publicada", "")[:10]
    print(f"   [{i:2d}] {pol:6.4f} (conf:{conf:.2f}) [{pos_kw}+/{neg_kw}-] {pub} - {title}...")

print(f"\n📰 TOP 10 ARTIGOS MAIS NEGATIVOS:")
top_negative = sorted(negative_articles, 
                     key=lambda x: x.get("sentimentos", {}).get("polarity", 0))[:10]
for i, a in enumerate(top_negative, 1):
    sent = a.get("sentimentos", {})
    title = a.get("titulo_noticia", "Sem título")[:65]
    pol = sent.get("polarity", 0)
    conf = sent.get("confidence", 0)
    pos_kw = sent.get("positive_keywords", 0)
    neg_kw = sent.get("negative_keywords", 0)
    pub = a.get("publicada", "")[:10]
    print(f"   [{i:2d}] {pol:6.4f} (conf:{conf:.2f}) [{pos_kw}+/{neg_kw}-] {pub} - {title}...")

# Análise temporal
print(f"\n📅 ANÁLISE TEMPORAL DE SENTIMENTOS:")
sentiment_by_year = defaultdict(lambda: {"positive": 0, "negative": 0, "neutral": 0, "polarities": []})

for a in articles:
    pubdate = a.get("publicada")
    if pubdate:
        try:
            dt = dateparser.parse(pubdate)
            year = dt.year
            label = a.get("sentimentos", {}).get("label", "neutral")
            polarity = a.get("sentimentos", {}).get("polarity", 0.0)
            
            sentiment_by_year[year][label] += 1
            sentiment_by_year[year]["polarities"].append(polarity)
        except:
            pass

for year in sorted(sentiment_by_year.keys()):
    data = sentiment_by_year[year]
    total_year = data["positive"] + data["negative"] + data["neutral"]
    avg_pol = statistics.mean(data["polarities"]) if data["polarities"] else 0.0
    sentiment_trend = "📈 positivo" if avg_pol > 0.05 else "📉 negativo" if avg_pol < -0.05 else "➡️  neutro"
    
    print(f"   {year}: {total_year:3d} artigos | "
          f"✅ {data['positive']:3d} | ❌ {data['negative']:3d} | ⚪ {data['neutral']:3d} | "
          f"Média: {avg_pol:7.4f} {sentiment_trend}")

# Análise por tema
print(f"\n🏷️  ANÁLISE POR TEMA:")
theme_sentiments = defaultdict(lambda: {"articles": [], "polarities": []})

for a in articles:
    query = a.get("query", "")
    polarity = a.get("sentimentos", {}).get("polarity", 0.0)
    
    # Categoriza por tema
    if "inadimplencia" in query.lower() or "agribusiness" in query.lower():
        theme = "Inadimplência Agronegócio"
    elif "resultados" in query.lower():
        theme = "Resultados Financeiros"
    elif "ofac" in query.lower() or "magnitsky" in query.lower():
        theme = "Sanções Internacionais"
    elif "B3" in query:
        theme = "Mercado de Ações"
    else:
        theme = "Geral"
    
    theme_sentiments[theme]["articles"].append(a)
    theme_sentiments[theme]["polarities"].append(polarity)

for theme in sorted(theme_sentiments.keys()):
    data = theme_sentiments[theme]
    articles_count = len(data["articles"])
    avg_pol = statistics.mean(data["polarities"]) if data["polarities"] else 0.0
    
    positive = sum(1 for a in data["articles"] if a.get("sentimentos", {}).get("label") == "positive")
    negative = sum(1 for a in data["articles"] if a.get("sentimentos", {}).get("label") == "negative")
    neutral = sum(1 for a in data["articles"] if a.get("sentimentos", {}).get("label") == "neutral")
    
    sentiment_icon = "✅" if avg_pol > 0.05 else "❌" if avg_pol < -0.05 else "⚪"
    
    print(f"   {sentiment_icon} {theme:30s}: {articles_count:3d} artigos | "
          f"Polaridade média: {avg_pol:7.4f} | "
          f"+{positive} /{neutral} /-{negative}")

# Artigos com alta confiança
print(f"\n🎯 ARTIGOS COM ALTA CONFIANÇA (>0.3):")
high_confidence = sorted(
    [a for a in articles if a.get("sentimentos", {}).get("confidence", 0) > 0.3],
    key=lambda x: x.get("sentimentos", {}).get("confidence", 0),
    reverse=True
)[:10]

for i, a in enumerate(high_confidence, 1):
    sent = a.get("sentimentos", {})
    title = a.get("titulo_noticia", "Sem título")[:65]
    pol = sent.get("polarity", 0)
    conf = sent.get("confidence", 0)
    label = sent.get("label", "neutral")
    icon = "✅" if label == "positive" else "❌" if label == "negative" else "⚪"
    print(f"   [{i:2d}] {icon} {conf:.4f} | pol:{pol:7.4f} | {title}...")

print("\n" + "="*80)
print(f"💾 Dados salvos em: {JSON_FILE}")
print(f"🗄️  Dados no MongoDB: bigData.projeto_ativos")
print("="*80)
