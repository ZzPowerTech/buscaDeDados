import yfinance as yf
import pandas as pd
from snowflake.connector import connect
from snowflake.connector.pandas_tools import write_pandas
from sqlalchemy import create_engine
from datetime import datetime

# ================================
# CONFIGURAÇÕES
# ================================

# Ação para buscar (BBAS3 = Banco do Brasil)
TICKER = "BBAS3.SA"  # .SA indica ações da B3 (Brasil)
DATA_INICIO = "2020-01-01"
DATA_FIM = datetime.now().strftime("%Y-%m-%d")

# PostgreSQL
pg_user = "postgres"
pg_password = "llwk20051"
pg_host = "localhost"
pg_port = "5432"
pg_db = "bigdata"

# Snowflake
sf_user = "ZZPOWERTECHZZ"
sf_password = "m#zzx3PiyAzRf7Tg"
sf_account = "RYQPYZE-FW60752"
sf_warehouse = "COMPUTE_WH"
sf_database = "BBAS3"
sf_schema = "PUBLIC"

# ================================
# BUSCAR DADOS DA API (Yahoo Finance)
# ================================

print(f"📊 Buscando dados de {TICKER} via API Yahoo Finance...")
print(f"   Período: {DATA_INICIO} até {DATA_FIM}\n")

# Baixar dados históricos
acao = yf.Ticker(TICKER)
df = acao.history(start=DATA_INICIO, end=DATA_FIM)

# Resetar index para ter a data como coluna
df.reset_index(inplace=True)

# Converter data para formato de data simples (sem timezone)
df['Date'] = pd.to_datetime(df['Date']).dt.date

# Calcular variação percentual diária
df['Variacao_Percentual'] = df['Close'].pct_change() * 100

# Renomear colunas para português
df = df.rename(columns={
    'Date': 'Data',
    'Open': 'Abertura',
    'High': 'Maxima',
    'Low': 'Minima',
    'Close': 'Fechamento',
    'Volume': 'Volume'
})

# Arredondar valores para 2 casas decimais
df['Abertura'] = df['Abertura'].round(2)
df['Maxima'] = df['Maxima'].round(2)
df['Minima'] = df['Minima'].round(2)
df['Fechamento'] = df['Fechamento'].round(2)
df['Variacao_Percentual'] = df['Variacao_Percentual'].round(2)

# Selecionar apenas as colunas necessárias
df = df[['Data', 'Abertura', 'Maxima', 'Minima', 'Fechamento', 'Volume', 'Variacao_Percentual']]

# Remover linhas com dados faltantes
df = df.dropna()

print(f"✅ {len(df)} registros obtidos da API!\n")
print("📋 Primeiras 5 linhas:")
print(df.head())
print("\n📋 Últimas 5 linhas:")
print(df.tail())

# ================================
# SALVAR NO POSTGRESQL
# ================================

print("\n" + "=" * 60)
print("💾 SALVANDO NO POSTGRESQL")
print("=" * 60)

pg_engine = create_engine(
    f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
)

nome_tabela_pg = "bbas3_dados_reais_api"

df.to_sql(
    nome_tabela_pg,
    pg_engine,
    if_exists='replace',  # Substitui se a tabela já existir
    index=False
)

print(f"✅ Dados salvos no PostgreSQL na tabela '{nome_tabela_pg}'")

# ================================
# SALVAR NO SNOWFLAKE
# ================================

print("\n" + "=" * 60)
print("❄️  SALVANDO NO SNOWFLAKE")
print("=" * 60)

sf_conn = connect(
    user=sf_user,
    password=sf_password,
    account=sf_account,
    warehouse=sf_warehouse,
    database=sf_database,
    schema=sf_schema,
)

nome_tabela_sf = "BBAS3_DADOS_REAIS_API"

sucesso, conta, num_chunks, _ = write_pandas(
    conn=sf_conn,
    df=df,
    table_name=nome_tabela_sf,
    auto_create_table=True,
    overwrite=True
)

print(f"✅ Dados salvos no Snowflake na tabela '{nome_tabela_sf}'")
print(f"   → Sucesso: {sucesso}, Linhas inseridas: {conta}")

# ================================
# ESTATÍSTICAS DOS DADOS
# ================================

print("\n" + "=" * 60)
print("📈 ESTATÍSTICAS DOS DADOS OBTIDOS")
print("=" * 60)

print(f"\nPeríodo coberto:")
print(f"  De: {df['Data'].min()}")
print(f"  Até: {df['Data'].max()}")
print(f"  Total de dias: {len(df)}")

print(f"\nPreço de Fechamento:")
print(f"  Mínimo: R$ {df['Fechamento'].min():.2f}")
print(f"  Máximo: R$ {df['Fechamento'].max():.2f}")
print(f"  Médio: R$ {df['Fechamento'].mean():.2f}")

print(f"\nVariação Diária:")
print(f"  Maior alta: {df['Variacao_Percentual'].max():.2f}%")
print(f"  Maior queda: {df['Variacao_Percentual'].min():.2f}%")
print(f"  Média: {df['Variacao_Percentual'].mean():.2f}%")

print(f"\nVolume:")
print(f"  Médio diário: {df['Volume'].mean():,.0f} ações")
print(f"  Máximo: {df['Volume'].max():,.0f} ações")

sf_conn.close()

print("\n🎉 Processo concluído com sucesso!")
print("\nPróximos passos:")
print("  1. Execute o script 'transformar_dados_api.py' para criar o modelo dimensional")
print("  2. Use as views criadas para análises no Snowflake")
