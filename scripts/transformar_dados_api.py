from snowflake.connector import connect

# ================================
# CONFIGURAÇÕES SNOWFLAKE
# ================================
sf_user = "ZZPOWERTECHZZ"
sf_password = "m#zzx3PiyAzRf7Tg"
sf_account = "RYQPYZE-FW60752"
sf_warehouse = "COMPUTE_WH"
sf_database = "BBAS3"
sf_schema = "PUBLIC"

# Conectar ao Snowflake
sf_conn = connect(
    user=sf_user,
    password=sf_password,
    account=sf_account,
    warehouse=sf_warehouse,
    database=sf_database,
    schema=sf_schema,
)

print("🔧 Criando modelo dimensional com dados reais da API...\n")

cursor = sf_conn.cursor()

# Criar tabela FATO com dados da API
sql_criar_fato = """
CREATE OR REPLACE TABLE FATO_ACOES_REAL AS
SELECT 
    TO_DATE("Data") as DATA_NEGOCIACAO,
    "Abertura" as PRECO_ABERTURA,
    "Maxima" as PRECO_MAXIMO,
    "Minima" as PRECO_MINIMO,
    "Fechamento" as PRECO_FECHAMENTO,
    "Volume" as VOLUME,
    "Variacao_Percentual" as VARIACAO_PERCENTUAL
FROM BBAS3_DADOS_REAIS_API
WHERE "Data" IS NOT NULL
ORDER BY "Data";
"""

cursor.execute(sql_criar_fato)
print("✅ Tabela FATO_ACOES_REAL criada com sucesso!")

# Criar dimensão TEMPO
sql_criar_dim_tempo = """
CREATE OR REPLACE TABLE DIM_TEMPO_REAL AS
SELECT DISTINCT
    TO_DATE("Data") as DATA,
    YEAR(TO_DATE("Data")) as ANO,
    QUARTER(TO_DATE("Data")) as TRIMESTRE,
    MONTH(TO_DATE("Data")) as MES,
    MONTHNAME(TO_DATE("Data")) as NOME_MES,
    DAY(TO_DATE("Data")) as DIA,
    DAYNAME(TO_DATE("Data")) as DIA_SEMANA,
    WEEK(TO_DATE("Data")) as SEMANA_ANO
FROM BBAS3_DADOS_REAIS_API
WHERE "Data" IS NOT NULL;
"""

cursor.execute(sql_criar_dim_tempo)
print("✅ Tabela DIM_TEMPO_REAL criada com sucesso!")

# Criar view de resumo mensal
sql_view_resumo_mensal = """
CREATE OR REPLACE VIEW VW_RESUMO_MENSAL_REAL AS
SELECT 
    t.ANO,
    t.MES,
    t.NOME_MES,
    ROUND(AVG(f.PRECO_FECHAMENTO), 2) as PRECO_MEDIO,
    ROUND(MAX(f.PRECO_MAXIMO), 2) as PRECO_MAX,
    ROUND(MIN(f.PRECO_MINIMO), 2) as PRECO_MIN,
    SUM(f.VOLUME) as VOLUME_TOTAL,
    ROUND(AVG(f.VARIACAO_PERCENTUAL), 2) as VARIACAO_MEDIA,
    COUNT(*) as DIAS_NEGOCIADOS
FROM FATO_ACOES_REAL f
JOIN DIM_TEMPO_REAL t ON f.DATA_NEGOCIACAO = t.DATA
GROUP BY t.ANO, t.MES, t.NOME_MES
ORDER BY t.ANO, t.MES;
"""

cursor.execute(sql_view_resumo_mensal)
print("✅ View VW_RESUMO_MENSAL_REAL criada com sucesso!")

# Criar view de análise anual
sql_view_analise_anual = """
CREATE OR REPLACE VIEW VW_ANALISE_ANUAL_REAL AS
SELECT 
    t.ANO,
    ROUND(AVG(f.PRECO_FECHAMENTO), 2) as PRECO_MEDIO_ANO,
    ROUND(MAX(f.PRECO_MAXIMO), 2) as PRECO_MAXIMO_ANO,
    ROUND(MIN(f.PRECO_MINIMO), 2) as PRECO_MINIMO_ANO,
    ROUND(MAX(f.VARIACAO_PERCENTUAL), 2) as MAIOR_ALTA,
    ROUND(MIN(f.VARIACAO_PERCENTUAL), 2) as MAIOR_QUEDA,
    ROUND(AVG(f.VARIACAO_PERCENTUAL), 2) as VARIACAO_MEDIA,
    ROUND(STDDEV(f.VARIACAO_PERCENTUAL), 2) as VOLATILIDADE,
    SUM(f.VOLUME) as VOLUME_TOTAL_ANO,
    COUNT(*) as DIAS_NEGOCIADOS
FROM FATO_ACOES_REAL f
JOIN DIM_TEMPO_REAL t ON f.DATA_NEGOCIACAO = t.DATA
GROUP BY t.ANO
ORDER BY t.ANO;
"""

cursor.execute(sql_view_analise_anual)
print("✅ View VW_ANALISE_ANUAL_REAL criada com sucesso!")

# Criar view de médias móveis e indicadores técnicos
sql_view_indicadores = """
CREATE OR REPLACE VIEW VW_INDICADORES_TECNICOS AS
SELECT 
    DATA_NEGOCIACAO,
    PRECO_FECHAMENTO,
    VARIACAO_PERCENTUAL,
    VOLUME,
    -- Médias Móveis
    ROUND(AVG(PRECO_FECHAMENTO) OVER (
        ORDER BY DATA_NEGOCIACAO 
        ROWS BETWEEN 7 PRECEDING AND CURRENT ROW
    ), 2) as MEDIA_MOVEL_7D,
    ROUND(AVG(PRECO_FECHAMENTO) OVER (
        ORDER BY DATA_NEGOCIACAO 
        ROWS BETWEEN 20 PRECEDING AND CURRENT ROW
    ), 2) as MEDIA_MOVEL_20D,
    ROUND(AVG(PRECO_FECHAMENTO) OVER (
        ORDER BY DATA_NEGOCIACAO 
        ROWS BETWEEN 50 PRECEDING AND CURRENT ROW
    ), 2) as MEDIA_MOVEL_50D,
    ROUND(AVG(PRECO_FECHAMENTO) OVER (
        ORDER BY DATA_NEGOCIACAO 
        ROWS BETWEEN 200 PRECEDING AND CURRENT ROW
    ), 2) as MEDIA_MOVEL_200D,
    -- Volatilidade
    ROUND(STDDEV(VARIACAO_PERCENTUAL) OVER (
        ORDER BY DATA_NEGOCIACAO 
        ROWS BETWEEN 30 PRECEDING AND CURRENT ROW
    ), 2) as VOLATILIDADE_30D,
    -- Retorno acumulado
    ROUND(((PRECO_FECHAMENTO / FIRST_VALUE(PRECO_FECHAMENTO) OVER (ORDER BY DATA_NEGOCIACAO)) - 1) * 100, 2) as RETORNO_ACUMULADO_PCT
FROM FATO_ACOES_REAL
ORDER BY DATA_NEGOCIACAO DESC;
"""

cursor.execute(sql_view_indicadores)
print("✅ View VW_INDICADORES_TECNICOS criada com sucesso!")

# Criar view de performance trimestral
sql_view_trimestral = """
CREATE OR REPLACE VIEW VW_PERFORMANCE_TRIMESTRAL AS
SELECT 
    t.ANO,
    t.TRIMESTRE,
    ROUND(AVG(f.PRECO_FECHAMENTO), 2) as PRECO_MEDIO,
    ROUND(
        (MAX(CASE WHEN f.DATA_NEGOCIACAO = (
            SELECT MAX(DATA_NEGOCIACAO) 
            FROM FATO_ACOES_REAL f2
            JOIN DIM_TEMPO_REAL t2 ON f2.DATA_NEGOCIACAO = t2.DATA
            WHERE t2.ANO = t.ANO AND t2.TRIMESTRE = t.TRIMESTRE
        ) THEN f.PRECO_FECHAMENTO END) / 
        MIN(CASE WHEN f.DATA_NEGOCIACAO = (
            SELECT MIN(DATA_NEGOCIACAO) 
            FROM FATO_ACOES_REAL f2
            JOIN DIM_TEMPO_REAL t2 ON f2.DATA_NEGOCIACAO = t2.DATA
            WHERE t2.ANO = t.ANO AND t2.TRIMESTRE = t.TRIMESTRE
        ) THEN f.PRECO_FECHAMENTO END) - 1) * 100
    , 2) as VARIACAO_TRIMESTRE,
    SUM(f.VOLUME) as VOLUME_TOTAL
FROM FATO_ACOES_REAL f
JOIN DIM_TEMPO_REAL t ON f.DATA_NEGOCIACAO = t.DATA
GROUP BY t.ANO, t.TRIMESTRE
ORDER BY t.ANO, t.TRIMESTRE;
"""

cursor.execute(sql_view_trimestral)
print("✅ View VW_PERFORMANCE_TRIMESTRAL criada com sucesso!")

# Mostrar resumo
print("\n" + "=" * 60)
print("📊 RESUMO DOS DADOS TRANSFORMADOS")
print("=" * 60)

cursor.execute("SELECT COUNT(*) FROM FATO_ACOES_REAL")
print(f"Total de registros: {cursor.fetchone()[0]}")

cursor.execute("SELECT MIN(DATA_NEGOCIACAO), MAX(DATA_NEGOCIACAO) FROM FATO_ACOES_REAL")
data_min, data_max = cursor.fetchone()
print(f"Período: {data_min} até {data_max}")

print("\n📈 Análise por ano:")
cursor.execute("SELECT * FROM VW_ANALISE_ANUAL_REAL ORDER BY ANO")
print("\nANO | PREÇO_MÉDIO | MAIOR_ALTA | MAIOR_QUEDA | VOLATILIDADE")
print("-" * 60)
for row in cursor.fetchall():
    print(f"{row[0]} | R$ {row[1]:7.2f} | {row[4]:6.2f}% | {row[5]:7.2f}% | {row[7]:6.2f}%")

cursor.close()
sf_conn.close()

print("\n🎉 Transformação concluída! Tabelas e views disponíveis:")
print("   • FATO_ACOES_REAL - Tabela fato com dados da API")
print("   • DIM_TEMPO_REAL - Dimensão temporal")
print("   • VW_RESUMO_MENSAL_REAL - Análise mensal")
print("   • VW_ANALISE_ANUAL_REAL - Análise anual completa")
print("   • VW_INDICADORES_TECNICOS - Médias móveis e indicadores")
print("   • VW_PERFORMANCE_TRIMESTRAL - Performance por trimestre")
