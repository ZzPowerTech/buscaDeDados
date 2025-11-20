from snowflake.connector import connect

sf_conn = connect(
    user="ZZPOWERTECHZZ",
    password="m#zzx3PiyAzRf7Tg",
    account="RYQPYZE-FW60752",
    warehouse="COMPUTE_WH",
    database="BBAS3",
    schema="PUBLIC",
)

cursor = sf_conn.cursor()

print("📋 Estrutura da tabela BBAS3_DADOS_REAIS_API:")
cursor.execute("DESCRIBE TABLE BBAS3_DADOS_REAIS_API")
for col in cursor.fetchall():
    print(f"  • {col[0]:30} | Tipo: {col[1]}")

print("\n📊 Primeiras 3 linhas:")
cursor.execute("SELECT * FROM BBAS3_DADOS_REAIS_API LIMIT 3")
for row in cursor.fetchall():
    print(row)

cursor.close()
sf_conn.close()
