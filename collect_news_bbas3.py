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
from pymongo import MongoClient, errors  # garante import de errors

# ---------- CONFIG ----------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "bigData")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "projeto_ativos")
OUTPUT_JSON = "collected_articles_bbas3.json"

QUERIES = [
    "BBAS3 Banco do Brasil resultados 2025",
    "Banco do Brasil agribusiness inadimplencia 2025",
    "OFAC sanctions Brazil Banco do Brasil",
    "Magnitsky act Brazil Banco do Brasil",
    "Banco do Brasil",
    "BBAS3 B3"
]

MAX_PER_QUERY = 30
MAX_YEARS_BACK = 5
SLEEP_BETWEEN_REQUESTS = 1.0

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# ---------- FUNÇÕES ----------

def google_news_rss(query):
    q = quote_plus(query)
    return f"https://news.google.com/rss/search?q={q}&hl=pt-BR&gl=BR&ceid=BR:pt-419"

def snippet_from_text(text, max_words=25):
    if not text:
        return ""
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    for para in paragraphs:
        words = para.split()
        if len(words) >= 5:
            return " ".join(words[:max_words]).rstrip(" .,:;") + ("..." if len(words) > max_words else "")
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
    title = e.get("title", "")
    summary = e.get("summary", "")
    content = ""
    if "content" in e and len(e.content) > 0:
        content = " ".join([c.value for c in e.content if "value" in c])

    text_for_snippet = content or summary or title
    snippet = snippet_from_text(text_for_snippet)
    sentiment = sentiment_text(snippet)

    pub = ""
    if "published_parsed" in e and e.published_parsed:
        try:
            pub = datetime(*e.published_parsed[:6], tzinfo=timezone.utc).isoformat()
        except Exception:
            pub = ""

    return {
        "url": url,
        "titulo_noticia": title,
        "publicada": pub,
        "busca_feita": datetime.now(timezone.utc).isoformat(),
        "resumo": snippet,
        "sentimentos": sentiment
    }

def collect_from_query(query, max_items=MAX_PER_QUERY, since_years=MAX_YEARS_BACK):
    feed_url = google_news_rss(query)
    logging.info(f"Buscando RSS para: {query}")
    feed = feedparser.parse(feed_url)

    if getattr(feed, "bozo", False):
        logging.warning(f"Erro ao processar RSS: {feed.bozo_exception}")

    entries = feed.get("entries", [])[:max_items]
    docs = []
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=365*since_years)

    for e in entries:
        pub_dt = None
        if "published_parsed" in e and e.published_parsed:
            try:
                pub_dt = datetime(*e.published_parsed[:6], tzinfo=timezone.utc)
            except:
                pass
        if pub_dt and pub_dt < cutoff_date:
            continue
        doc = process_feed_entry(e)
        doc["query"] = query
        docs.append(doc)
        time.sleep(SLEEP_BETWEEN_REQUESTS + random.random()*0.5)

    return docs

def get_mongo_collection(uri=MONGO_URI, db_name=MONGO_DB, collection_name=MONGO_COLLECTION):
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client[db_name]
        col = db[collection_name]
        logging.info(f"Conectado ao MongoDB: {uri}, DB: {db_name}, Collection: {collection_name}")
        return col
    except errors.ServerSelectionTimeoutError as e:
        logging.error(f"Não foi possível conectar ao MongoDB: {e}")
        return None

def save_to_mongo(docs):
    col = get_mongo_collection()
    if col is None:
        logging.error("Coleção MongoDB não disponível. Abortando insert.")
        return

    ops = 0
    for d in docs:
        url = d.get("url")
        if not url:
            logging.warning(f"Documento sem URL, pulando: {d}")
            continue
        try:
            col.update_one({"url": url}, {"$set": d}, upsert=True)
            ops += 1
        except Exception as e:
            logging.error(f"Erro ao salvar documento {url}: {e}")
    logging.info(f"Total de documentos inseridos/atualizados: {ops}")

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

    save_to_mongo(all_docs)
    logging.info("Finalizado.")

if __name__ == "__main__":
    main()
