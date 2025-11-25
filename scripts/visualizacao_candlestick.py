"""
Gráfico Candlestick Profissional com Plotly
Mostra OHLC + Volume + Médias Móveis
"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.config import settings
from snowflake.connector import connect

print("📊 Gerando Gráfico Candlestick Interativo...")

# Conectar ao Snowflake
conn = connect(
    user=settings.snowflake.user,
    password=settings.snowflake.password,
    account=settings.snowflake.account,
    warehouse=settings.snowflake.warehouse,
    database=settings.snowflake.database,
    schema=settings.snowflake.schema
)

# Buscar dados
query = """
SELECT 
    DATA_NEGOCIACAO as data,
    PRECO_ABERTURA as abertura,
    PRECO_MAXIMO as maxima,
    PRECO_MINIMO as minima,
    PRECO_FECHAMENTO as fechamento,
    VOLUME,
    -- Médias móveis
    AVG(PRECO_FECHAMENTO) OVER (
        ORDER BY DATA_NEGOCIACAO 
        ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
    ) as MM20,
    AVG(PRECO_FECHAMENTO) OVER (
        ORDER BY DATA_NEGOCIACAO 
        ROWS BETWEEN 49 PRECEDING AND CURRENT ROW
    ) as MM50,
    AVG(PRECO_FECHAMENTO) OVER (
        ORDER BY DATA_NEGOCIACAO 
        ROWS BETWEEN 199 PRECEDING AND CURRENT ROW
    ) as MM200
FROM BBAS3.PUBLIC.FATO_ACOES_REAL
WHERE DATA_NEGOCIACAO >= DATEADD(month, -12, CURRENT_DATE())
ORDER BY data
"""

df = pd.read_sql(query, conn)
conn.close()

print(f"✅ {len(df)} dias de dados carregados")

# Criar subplots (Candlestick + Volume)
fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.03,
    subplot_titles=('BBAS3 - Preço e Médias Móveis', 'Volume'),
    row_heights=[0.7, 0.3]
)

# Candlestick
fig.add_trace(
    go.Candlestick(
        x=df['DATA'],
        open=df['ABERTURA'],
        high=df['MAXIMA'],
        low=df['MINIMA'],
        close=df['FECHAMENTO'],
        name='BBAS3',
        increasing_line_color='#26a69a',
        decreasing_line_color='#ef5350'
    ),
    row=1, col=1
)

# Médias Móveis
fig.add_trace(
    go.Scatter(
        x=df['DATA'], 
        y=df['MM20'], 
        name='MM20',
        line=dict(color='#2196F3', width=1.5)
    ),
    row=1, col=1
)

fig.add_trace(
    go.Scatter(
        x=df['DATA'], 
        y=df['MM50'], 
        name='MM50',
        line=dict(color='#FF9800', width=1.5)
    ),
    row=1, col=1
)

fig.add_trace(
    go.Scatter(
        x=df['DATA'], 
        y=df['MM200'], 
        name='MM200',
        line=dict(color='#9C27B0', width=2)
    ),
    row=1, col=1
)

# Volume
colors = ['#26a69a' if row['FECHAMENTO'] >= row['ABERTURA'] else '#ef5350' 
          for _, row in df.iterrows()]

fig.add_trace(
    go.Bar(
        x=df['DATA'], 
        y=df['VOLUME'],
        name='Volume',
        marker_color=colors,
        showlegend=False
    ),
    row=2, col=1
)

# Layout
fig.update_layout(
    title='Análise Técnica BBAS3 - Banco do Brasil',
    yaxis_title='Preço (R$)',
    yaxis2_title='Volume',
    template='plotly_dark',
    xaxis_rangeslider_visible=False,
    height=800,
    hovermode='x unified',
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

fig.update_xaxes(title_text="Data", row=2, col=1)

# Salvar e mostrar
output_file = root_dir / 'data' / 'grafico_candlestick.html'
fig.write_html(str(output_file))
print(f"\n✅ Gráfico salvo em: {output_file}")
print("🌐 Abrindo no navegador...")
fig.show()
