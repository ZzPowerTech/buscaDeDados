"""
Dashboard Completo: RSI + MACD + Bollinger + Volume
4 subplots interativos
"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path
import numpy as np

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.config import settings
from snowflake.connector import connect

print("📊 Gerando Dashboard Completo de Indicadores...")

conn = connect(
    user=settings.snowflake.user,
    password=settings.snowflake.password,
    account=settings.snowflake.account,
    warehouse=settings.snowflake.warehouse,
    database=settings.snowflake.database,
    schema=settings.snowflake.schema
)

query = """
WITH dados_base AS (
    SELECT 
        DATA_NEGOCIACAO as data,
        PRECO_FECHAMENTO as preco,
        PRECO_ABERTURA as abertura,
        PRECO_MAXIMO as maxima,
        PRECO_MINIMO as minima,
        VOLUME,
        VARIACAO_PERCENTUAL as variacao,
        -- Médias móveis
        AVG(PRECO_FECHAMENTO) OVER (ORDER BY DATA_NEGOCIACAO ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) as SMA20,
        STDDEV(PRECO_FECHAMENTO) OVER (ORDER BY DATA_NEGOCIACAO ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) as STD20,
        -- Para RSI
        PRECO_FECHAMENTO - LAG(PRECO_FECHAMENTO) OVER (ORDER BY DATA_NEGOCIACAO) as mudanca
    FROM BBAS3.PUBLIC.FATO_ACOES_REAL
    WHERE DATA_NEGOCIACAO >= DATEADD(month, -6, CURRENT_DATE())
)
SELECT 
    data,
    preco,
    abertura,
    maxima,
    minima,
    VOLUME,
    variacao,
    SMA20,
    SMA20 + (2 * STD20) as BB_upper,
    SMA20 - (2 * STD20) as BB_lower,
    CASE WHEN mudanca > 0 THEN mudanca ELSE 0 END as ganho,
    CASE WHEN mudanca < 0 THEN ABS(mudanca) ELSE 0 END as perda
FROM dados_base
ORDER BY data
"""

df = pd.read_sql(query, conn)
conn.close()

# Calcular RSI
df['avg_ganho'] = df['GANHO'].rolling(window=14).mean()
df['avg_perda'] = df['PERDA'].rolling(window=14).mean()
df['RS'] = df['avg_ganho'] / df['avg_perda'].replace(0, np.nan)
df['RSI'] = 100 - (100 / (1 + df['RS']))

# Calcular MACD (simplificado)
df['EMA12'] = df['PRECO'].ewm(span=12, adjust=False).mean()
df['EMA26'] = df['PRECO'].ewm(span=26, adjust=False).mean()
df['MACD'] = df['EMA12'] - df['EMA26']
df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
df['Histograma'] = df['MACD'] - df['Signal']

print(f"✅ {len(df)} dias de indicadores calculados")

# Criar dashboard com 4 subplots
fig = make_subplots(
    rows=4, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.02,
    subplot_titles=(
        'Preço + Bandas de Bollinger',
        'RSI (Índice de Força Relativa)',
        'MACD',
        'Volume'
    ),
    row_heights=[0.4, 0.2, 0.2, 0.2]
)

# 1. Preço + Bollinger Bands
fig.add_trace(
    go.Scatter(x=df['DATA'], y=df['PRECO'], name='Preço', line=dict(color='#2196F3', width=2)),
    row=1, col=1
)
fig.add_trace(
    go.Scatter(x=df['DATA'], y=df['BB_UPPER'], name='BB Superior', 
               line=dict(color='rgba(255,255,255,0.3)', dash='dash')),
    row=1, col=1
)
fig.add_trace(
    go.Scatter(x=df['DATA'], y=df['SMA20'], name='SMA20', 
               line=dict(color='#FF9800', width=1)),
    row=1, col=1
)
fig.add_trace(
    go.Scatter(x=df['DATA'], y=df['BB_LOWER'], name='BB Inferior',
               line=dict(color='rgba(255,255,255,0.3)', dash='dash'),
               fill='tonexty', fillcolor='rgba(255,152,0,0.1)'),
    row=1, col=1
)

# 2. RSI
fig.add_trace(
    go.Scatter(x=df['DATA'], y=df['RSI'], name='RSI', 
               line=dict(color='#9C27B0', width=2)),
    row=2, col=1
)
fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=2, col=1)
fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=2, col=1)
fig.add_hrect(y0=70, y1=100, fillcolor="red", opacity=0.1, row=2, col=1)
fig.add_hrect(y0=0, y1=30, fillcolor="green", opacity=0.1, row=2, col=1)

# 3. MACD
fig.add_trace(
    go.Scatter(x=df['DATA'], y=df['MACD'], name='MACD', 
               line=dict(color='#00BCD4', width=1.5)),
    row=3, col=1
)
fig.add_trace(
    go.Scatter(x=df['DATA'], y=df['Signal'], name='Signal', 
               line=dict(color='#FF5722', width=1.5)),
    row=3, col=1
)
colors_macd = ['#26a69a' if x > 0 else '#ef5350' for x in df['Histograma']]
fig.add_trace(
    go.Bar(x=df['DATA'], y=df['Histograma'], name='Histograma',
           marker_color=colors_macd, opacity=0.6),
    row=3, col=1
)

# 4. Volume
colors_vol = ['#26a69a' if row['PRECO'] >= row['ABERTURA'] else '#ef5350' 
              for _, row in df.iterrows()]
fig.add_trace(
    go.Bar(x=df['DATA'], y=df['VOLUME'], name='Volume',
           marker_color=colors_vol, showlegend=False),
    row=4, col=1
)

# Layout geral
fig.update_layout(
    title='Dashboard Completo - Análise Técnica BBAS3',
    template='plotly_dark',
    height=1000,
    showlegend=True,
    hovermode='x unified',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

fig.update_xaxes(title_text="Data", row=4, col=1)
fig.update_yaxes(title_text="Preço (R$)", row=1, col=1)
fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
fig.update_yaxes(title_text="MACD", row=3, col=1)
fig.update_yaxes(title_text="Volume", row=4, col=1)

output_file = root_dir / 'data' / 'dashboard_indicadores.html'
fig.write_html(str(output_file))
print(f"\n✅ Dashboard salvo em: {output_file}")
print("🌐 Abrindo no navegador...")
fig.show()
