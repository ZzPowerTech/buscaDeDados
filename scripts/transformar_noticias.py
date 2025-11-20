from snowflake.connector import connect

sf_conn = connect(
    user="ZZPOWERTECHZZ",
    password="m#zzx3PiyAzRf7Tg",
    account="RYQPYZE-FW60752",
    warehouse="COMPUTE_WH",
    database="BBAS3",
    schema="PUBLIC",
)

print("🔧 Transformando tabela DADOS_MONG (Notícias)...\n")

cursor = sf_conn.cursor()

# Criar tabela FATO de notícias com dados limpos
sql_criar_fato_noticias = """
CREATE OR REPLACE TABLE FATO_NOTICIAS AS
SELECT 
    "_id" as ID_NOTICIA,
    TO_TIMESTAMP_NTZ("busca_feita") as DATA_BUSCA,
    TO_TIMESTAMP_NTZ("publicada") as DATA_PUBLICACAO,
    "query" as QUERY_BUSCA,
    "titulo_noticia" as TITULO,
    REGEXP_REPLACE("url", '^https://news\\.google\\.com/rss/articles/', '') as URL_LIMPA,
    "url" as URL_COMPLETA,
    "label" as SENTIMENTO,
    ROUND("polarity", 2) as POLARIDADE,
    ROUND("subjectivity", 2) as SUBJETIVIDADE,
    -- Extrair domínio da notícia
    CASE 
        WHEN "titulo_noticia" LIKE '% - %' 
        THEN TRIM(SPLIT_PART("titulo_noticia", ' - ', -1))
        ELSE 'Desconhecido'
    END as FONTE_NOTICIA
FROM DADOS_MONG
WHERE "_id" IS NOT NULL;
"""

cursor.execute(sql_criar_fato_noticias)
print("✅ Tabela FATO_NOTICIAS criada com sucesso!")

# Criar dimensão de sentimento
sql_dim_sentimento = """
CREATE OR REPLACE TABLE DIM_SENTIMENTO AS
SELECT DISTINCT
    "label" as SENTIMENTO,
    CASE 
        WHEN "label" = 'positive' THEN 'Positivo'
        WHEN "label" = 'negative' THEN 'Negativo'
        WHEN "label" = 'neutral' THEN 'Neutro'
        ELSE 'Desconhecido'
    END as SENTIMENTO_PT,
    CASE 
        WHEN "label" = 'positive' THEN 1
        WHEN "label" = 'neutral' THEN 0
        WHEN "label" = 'negative' THEN -1
        ELSE 0
    END as SENTIMENTO_VALOR
FROM DADOS_MONG;
"""

cursor.execute(sql_dim_sentimento)
print("✅ Tabela DIM_SENTIMENTO criada com sucesso!")

# Criar view de análise de sentimento por período
sql_view_sentimento_periodo = """
CREATE OR REPLACE VIEW VW_SENTIMENTO_POR_PERIODO AS
SELECT 
    DATE_TRUNC('day', DATA_PUBLICACAO) as DATA,
    SENTIMENTO,
    COUNT(*) as TOTAL_NOTICIAS,
    ROUND(AVG(POLARIDADE), 2) as POLARIDADE_MEDIA,
    ROUND(AVG(SUBJETIVIDADE), 2) as SUBJETIVIDADE_MEDIA
FROM FATO_NOTICIAS
GROUP BY DATE_TRUNC('day', DATA_PUBLICACAO), SENTIMENTO
ORDER BY DATA DESC, SENTIMENTO;
"""

cursor.execute(sql_view_sentimento_periodo)
print("✅ View VW_SENTIMENTO_POR_PERIODO criada com sucesso!")

# Criar view de distribuição por fonte
sql_view_por_fonte = """
CREATE OR REPLACE VIEW VW_NOTICIAS_POR_FONTE AS
SELECT 
    FONTE_NOTICIA,
    COUNT(*) as TOTAL_NOTICIAS,
    ROUND(AVG(POLARIDADE), 2) as POLARIDADE_MEDIA,
    COUNT(CASE WHEN SENTIMENTO = 'positive' THEN 1 END) as NOTICIAS_POSITIVAS,
    COUNT(CASE WHEN SENTIMENTO = 'neutral' THEN 1 END) as NOTICIAS_NEUTRAS,
    COUNT(CASE WHEN SENTIMENTO = 'negative' THEN 1 END) as NOTICIAS_NEGATIVAS
FROM FATO_NOTICIAS
GROUP BY FONTE_NOTICIA
ORDER BY TOTAL_NOTICIAS DESC;
"""

cursor.execute(sql_view_por_fonte)
print("✅ View VW_NOTICIAS_POR_FONTE criada com sucesso!")

# Criar view combinando notícias com cotações
sql_view_correlacao = """
CREATE OR REPLACE VIEW VW_CORRELACAO_NOTICIAS_PRECO AS
SELECT 
    DATE(n.DATA_PUBLICACAO) as DATA,
    COUNT(n.ID_NOTICIA) as TOTAL_NOTICIAS,
    ROUND(AVG(n.POLARIDADE), 2) as POLARIDADE_MEDIA_DIA,
    ROUND(AVG(CASE WHEN n.SENTIMENTO = 'positive' THEN 1.0 
                    WHEN n.SENTIMENTO = 'negative' THEN -1.0 
                    ELSE 0.0 END), 2) as SCORE_SENTIMENTO,
    a.PRECO_FECHAMENTO,
    a.VARIACAO_PERCENTUAL
FROM FATO_NOTICIAS n
LEFT JOIN FATO_ACOES_REAL a ON DATE(n.DATA_PUBLICACAO) = a.DATA_NEGOCIACAO
GROUP BY DATE(n.DATA_PUBLICACAO), a.PRECO_FECHAMENTO, a.VARIACAO_PERCENTUAL
ORDER BY DATA DESC;
"""

cursor.execute(sql_view_correlacao)
print("✅ View VW_CORRELACAO_NOTICIAS_PRECO criada com sucesso!")

# Mostrar estatísticas
print("\n" + "=" * 60)
print("📊 ESTATÍSTICAS DAS NOTÍCIAS")
print("=" * 60)

cursor.execute("SELECT COUNT(*) FROM FATO_NOTICIAS")
print(f"Total de notícias: {cursor.fetchone()[0]}")

cursor.execute("""
    SELECT 
        SENTIMENTO,
        COUNT(*) as TOTAL,
        ROUND(AVG(POLARIDADE), 2) as POLARIDADE_MEDIA
    FROM FATO_NOTICIAS
    GROUP BY SENTIMENTO
    ORDER BY TOTAL DESC
""")

print("\n📈 Distribuição por sentimento:")
print("-" * 60)
for row in cursor.fetchall():
    print(f"  {row[0]:10} → {row[1]:3} notícias | Polaridade média: {row[2]}")

print("\n📰 Top 5 fontes de notícias:")
print("-" * 60)
cursor.execute("SELECT * FROM VW_NOTICIAS_POR_FONTE LIMIT 5")
for row in cursor.fetchall():
    print(f"  {row[0]:30} → {row[1]:3} notícias | Polaridade: {row[2]}")

cursor.close()
sf_conn.close()

print("\n🎉 Transformação concluída! Tabelas e views disponíveis:")
print("   • FATO_NOTICIAS - Notícias com análise de sentimento")
print("   • DIM_SENTIMENTO - Dimensão de sentimento")
print("   • VW_SENTIMENTO_POR_PERIODO - Sentimento agregado por dia")
print("   • VW_NOTICIAS_POR_FONTE - Distribuição por fonte de notícia")
print("   • VW_CORRELACAO_NOTICIAS_PRECO - Correlação entre notícias e preço")
