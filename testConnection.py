from pymongo import MongoClient, errors

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "bigData"
COLLECTION_NAME = "teste_colecao"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')  # testa conexão
    print("MongoDB conectado com sucesso!")

    db = client[DB_NAME]
    col = db[COLLECTION_NAME]

    # teste de inserção
    result = col.update_one({"teste": "ping"}, {"$set": {"teste": "ping"}}, upsert=True)
    print("Inserção/Atualização realizada com sucesso!")
except errors.ServerSelectionTimeoutError as e:
    print(f"Erro de conexão com MongoDB: {e}")
except Exception as e:
    print(f"Erro geral: {e}")
