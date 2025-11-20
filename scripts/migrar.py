import pandas as pd
from sqlalchemy import create_engine
from snowflake.connector import connect
from snowflake.connector.pandas_tools import write_pandas

# ================================
# CONFIGURAÇÕES
# ================================

# PostgreSQL
pg_user = "postgres"
pg_password = "llwk20051"
pg_host = "localhost"
pg_port = "5432"
pg_db = "bigdata"

# Snowflake
sf_user = "ZZPOWERTECHZZ"
sf_password = "m#zzx3PiyAzRf7Tg"
sf_account = "RYQPYZE-FW60752"  # EXEMPLO: abcdef-ab12345
sf_warehouse = "COMPUTE_WH"
sf_database = "BBAS3"
sf_schema = "PUBLIC"

# Tabelas que você quer migrar
tabelas_para_migrar = ["bbas3_dados_hist_ricos_1", "dados_mong"]


# ================================
# CONECTAR AO POSTGRESQL
# ================================

pg_engine = create_engine(
    f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
)

print("Conectado ao PostgreSQL.")


# ================================
# CONECTAR AO SNOWFLAKE
# ================================

sf_conn = connect(
    user=sf_user,
    password=sf_password,
    account=sf_account,
    warehouse=sf_warehouse,
    database=sf_database,
    schema=sf_schema,
)

print("Conectado ao Snowflake.")


# ================================
# MIGRAR CADA TABELA
# ================================

for tabela in tabelas_para_migrar:
    print(f"\n📥 Lendo tabela '{tabela}' do PostgreSQL...")

    # Carregar tabela em DataFrame
    df = pd.read_sql(f'SELECT * FROM "{tabela}"', pg_engine)

    print(f"   → {len(df)} registros carregados.")

    print(f"📤 Enviando tabela '{tabela.upper()}' para Snowflake...")

    # Criar tabela automaticamente + inserir dados
    sucesso, conta, num_chunks, _ = write_pandas(
        conn=sf_conn,
        df=df,
        table_name=tabela.upper(),
        auto_create_table=True,     # 🔥 Snowflake cria tabela sozinho
        overwrite=True              # sobrescreve a tabela se já existir
    )

    print(f"   → Sucesso: {sucesso}, Linhas inseridas: {conta}")

print("\n🎉 Migração concluída com sucesso!")

# ================================
# VERIFICAR TABELAS CRIADAS
# ================================
print("\n📋 Verificando tabelas criadas no Snowflake...")

cursor = sf_conn.cursor()
cursor.execute("SHOW TABLES IN SCHEMA PUBLIC")
tabelas_snowflake = cursor.fetchall()

print(f"\n   Tabelas encontradas no schema PUBLIC:")
for tabela in tabelas_snowflake:
    print(f"   • {tabela[1]}")  # Nome da tabela está na posição 1

cursor.close()
sf_conn.close()
