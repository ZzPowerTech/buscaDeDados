"""
Script para verificar os dados inseridos no MongoDB
"""
from pymongo import MongoClient, errors
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "bigData")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "projeto_ativos")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print(f"✓ MongoDB conectado: {MONGO_URI}")
    
    db = client[MONGO_DB]
    col = db[MONGO_COLLECTION]
    
    # Contar documentos
    count = col.count_documents({})
    print(f"✓ Total de documentos na coleção '{MONGO_COLLECTION}': {count}")
    
    if count > 0:
        # Mostrar alguns exemplos
        print("\n=== Primeiros 3 documentos ===")
        for i, doc in enumerate(col.find().limit(3), 1):
            print(f"\n[{i}] Query: {doc.get('query', 'N/A')}")
            print(f"    Título: {doc.get('titulo_noticia', 'N/A')[:80]}...")
            print(f"    URL: {doc.get('url', 'N/A')[:60]}...")
            print(f"    Sentimento: {doc.get('sentimentos', {}).get('label', 'N/A')}")
            print(f"    Publicada: {doc.get('publicada', 'N/A')}")
        
        # Estatísticas de sentimento
        print("\n=== Distribuição de Sentimentos ===")
        pipeline = [
            {"$group": {
                "_id": "$sentimentos.label",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        for result in col.aggregate(pipeline):
            label = result['_id'] if result['_id'] else 'sem_sentimento'
            print(f"  {label}: {result['count']}")
        
        # Contar por query
        print("\n=== Documentos por Query ===")
        pipeline = [
            {"$group": {
                "_id": "$query",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        for result in col.aggregate(pipeline):
            print(f"  {result['_id']}: {result['count']}")
    else:
        print("\n⚠ Nenhum documento encontrado na coleção!")
        
except errors.ServerSelectionTimeoutError as e:
    print(f"✗ Erro de conexão com MongoDB: {e}")
except Exception as e:
    print(f"✗ Erro geral: {e}")
