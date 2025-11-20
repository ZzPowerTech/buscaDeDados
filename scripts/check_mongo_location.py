"""
Script para verificar localização exata dos dados no MongoDB
"""
from pymongo import MongoClient
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.config import settings

print("="*80)
print("🔍 VERIFICANDO LOCALIZAÇÃO DOS DADOS NO MONGODB")
print("="*80)

# Conectar
client = MongoClient(settings.mongodb.uri, serverSelectionTimeoutMS=5000)

print(f"\n📡 Conectado ao MongoDB: {settings.mongodb.uri}")
print(f"\n📊 Configuração atual:")
print(f"   Database: {settings.mongodb.database}")
print(f"   Collection: {settings.mongodb.collection}")

# Listar todos os databases
print(f"\n📂 Databases disponíveis:")
for db_name in client.list_database_names():
    db = client[db_name]
    collections = db.list_collection_names()
    print(f"\n   • {db_name}")
    if collections:
        for col_name in collections:
            count = db[col_name].count_documents({})
            print(f"      └─ {col_name}: {count} documentos")
    else:
        print(f"      └─ (vazio)")

# Verificar database específico
db = client[settings.mongodb.database]
col = db[settings.mongodb.collection]
count = col.count_documents({})

print(f"\n" + "="*80)
print(f"✅ DADOS NO DESTINO CONFIGURADO:")
print(f"   {settings.mongodb.database}.{settings.mongodb.collection}: {count} documentos")
print("="*80)

# Mostrar uma amostra
if count > 0:
    print(f"\n📰 Amostra (1 documento):")
    doc = col.find_one()
    print(f"   Título: {doc.get('titulo_noticia', 'N/A')[:80]}...")
    print(f"   Query: {doc.get('query', 'N/A')}")
    print(f"   Sentimento: {doc.get('sentimentos', {}).get('label', 'N/A')}")
    print(f"   Campos: {', '.join(list(doc.keys())[:10])}...")

client.close()
