"""
Coleta notícias do Google News RSS sobre BBAS3/Banco do Brasil,
gera snippet, analisa sentimento e salva JSON + MongoDB.

Respeita robots.txt e não contorna paywalls.
"""

import os
import json
import logging
import random
import time
from urllib.parse import quote_plus
from datetime import datetime, timedelta, timezone

import feedparser
from textblob import TextBlob
from pymongo import MongoClient

# ---------- CONFIG ----------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "projeto_bigdata")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "projeto-ativos")
OUTPUT_JSON = "collected_articles_bbas3.json"

QUERIES = [
    "BBAS3 Banco do Brasil resultados 2025",
    "Banco do Brasil agribusiness inadimplencia 2025",
    "OFAC sanctions Brazil Banco do Brasil",
    "Magnitsky act Brazil Banco do Brasil"
]

MAX_PER_QUERY = 20
MAX_YEARS_BACK = 5
SLEEP_BETWEEN_REQUESTS = 1.0

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# ---------- FUNÇÕES ----------

def google_news_rss(query):
    """Retorna RSS feed URL para query."""
    q = quote_plus(query)
    return f"https://news.google.com/rss/search?q={q}&hl=pt-BR&gl=BR&ceid=BR:pt-419"

def snippet_from_text(text, max_words=25):
    """Extrai um snippet do texto real da notícia, limitado a max_words."""
    if not text:
        return ""

    # Quebra o texto em parágrafos e remove os vazios
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]

    # Se não houver parágrafos, retorna vazio
    if not paragraphs:
        return ""

    # Escolhe o primeiro parágrafo com conteúdo mínimo
    for para in paragraphs:
        words = para.split()
        if len(words) >= 5:  # evita parágrafos muito curtos tipo “Foto” ou “Leia mais”
            if len(words) <= max_words:
                return para
            else:
                return " ".join(words[:max_words]).rstrip(" .,:;") + "..."

    # fallback: primeiro parágrafo mesmo que curto
    words = paragraphs[0].split()
    return " ".join(words[:max_words]).rstrip(" .,:;") + "..."

def sentiment_text(text):
    if not text:
        return {"polarity": 0.0, "subjectivity": 0.0, "label": "neutral"}
    tb = TextBlob(text)
    p = round(tb.sentiment.polarity, 4)
    s = round(tb.sentiment.subjectivity, 4)
    label = "neutral"
    if p > 0.1:
        label = "positive"
    elif p < -0.1:
        label = "negative"
    return {"polarity": p, "subjectivity": s, "label": label}

def process_feed_entry(e):
    url = e.get("link")
    title = e.get("title")
    pub = e.get("published")
    snippet = snippet_from_text(title)
    sentiment = sentiment_text(snippet)
    return {
        "url": url,
        "titulo_noticia": title,
        "publicada": pub,
        "busca_feita": datetime.now(timezone.utc).isoformat(),
        "snippet": snippet,
        "sentiment": sentiment
    }

def collect_from_query(query, max_items=MAX_PER_QUERY, since_years=MAX_YEARS_BACK):
    feed_url = google_news_rss(query)
    logging.info(f"Buscando RSS para: {query}")
    feed = feedparser.parse(feed_url)
    entries = feed.get("entries", [])[:max_items]
    docs = []
    cutoff_date = datetime.now() - timedelta(days=365*since_years)
    for e in entries:
        pub = None
        if "published" in e:
            try:
                pub = datetime(*e.published_parsed[:6])
            except:
                pass
        if pub and pub < cutoff_date:
            continue
        doc = process_feed_entry(e)
        doc["query"] = query
        docs.append(doc)
        time.sleep(SLEEP_BETWEEN_REQUESTS + random.random()*0.5)
    return docs

def save_to_mongo(docs):
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    col = db[MONGO_COLLECTION]
    ops = 0
    for d in docs:
        url = d.get("url")
        if not url:
            continue
        col.update_one({"url": url}, {"$set": d}, upsert=True)
        ops += 1
    logging.info(f"Salvo {ops} documentos no MongoDB ({MONGO_DB}/{MONGO_COLLECTION})")

def main():
    all_docs = []
    seen_urls = set()
    for q in QUERIES:
        try:
            docs = collect_from_query(q)
            for d in docs:
                url = d.get("url")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_docs.append(d)
        except Exception as e:
            logging.error(f"Erro ao coletar {q}: {e}")

    logging.info(f"Coletados {len(all_docs)} itens únicos. Salvando JSON e MongoDB...")
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(all_docs, f, ensure_ascii=False, indent=2)
    try:
        save_to_mongo(all_docs)
    except Exception as e:
        logging.error(f"Erro ao salvar no MongoDB: {e}")
    logging.info("Finalizado.")

if __name__ == "__main__":
    main()
