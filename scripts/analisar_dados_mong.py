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

print("🔍 Analisando tabela DADOS_MONG...\n")

# Ver estrutura
print("📋 Estrutura da tabela:")
print("=" * 80)
cursor.execute("DESCRIBE TABLE DADOS_MONG")
for col in cursor.fetchall():
    print(f"  • {col[0]:30} | Tipo: {col[1]}")

# Ver quantidade de registros
cursor.execute("SELECT COUNT(*) FROM DADOS_MONG")
total = cursor.fetchone()[0]
print(f"\nTotal de registros: {total}")

# Ver primeiras linhas
print("\n📊 Primeiras 5 registros:")
print("=" * 80)
cursor.execute("SELECT * FROM DADOS_MONG LIMIT 5")
colunas = [desc[0] for desc in cursor.description]
print(f"Colunas: {', '.join(colunas)}\n")

for i, row in enumerate(cursor.fetchall(), 1):
    print(f"Registro {i}:")
    for col, val in zip(colunas, row):
        if isinstance(val, str) and len(val) > 100:
            print(f"  {col}: {val[:100]}...")
        else:
            print(f"  {col}: {val}")
    print()

# Ver valores únicos de algumas colunas importantes
print("\n📊 Análise de dados:")
print("=" * 80)

cursor.execute("SELECT DISTINCT query FROM DADOS_MONG")
queries = cursor.fetchall()
print(f"\nQueries únicas: {len(queries)}")
for q in queries[:5]:
    print(f"  • {q[0]}")

cursor.execute("SELECT DISTINCT label FROM DADOS_MONG")
labels = cursor.fetchall()
print(f"\nLabels únicas: {len(labels)}")
for l in labels:
    print(f"  • {l[0]}")

# Ver distribuição de polaridade e subjetividade
cursor.execute("""
    SELECT 
        ROUND(AVG(polarity), 2) as polarity_media,
        ROUND(MIN(polarity), 2) as polarity_min,
        ROUND(MAX(polarity), 2) as polarity_max,
        ROUND(AVG(subjectivity), 2) as subjectivity_media,
        ROUND(MIN(subjectivity), 2) as subjectivity_min,
        ROUND(MAX(subjectivity), 2) as subjectivity_max
    FROM DADOS_MONG
""")
stats = cursor.fetchone()
print(f"\n📈 Estatísticas de Análise de Sentimento:")
print(f"  Polaridade (média): {stats[0]}")
print(f"  Polaridade (min-max): {stats[1]} até {stats[2]}")
print(f"  Subjetividade (média): {stats[3]}")
print(f"  Subjetividade (min-max): {stats[4]} até {stats[5]}")

cursor.close()
sf_conn.close()

print("\n✅ Análise concluída!")
