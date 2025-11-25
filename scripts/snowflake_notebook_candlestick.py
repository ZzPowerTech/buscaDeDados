# ============================================================
# SNOWFLAKE NOTEBOOK - Gráfico Candlestick BBAS3
# ============================================================
# Este código deve ser executado em um Snowflake Notebook
# Não precisa de conexão - já está dentro do Snowflake!
# ============================================================

# Importar bibliotecas
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from snowflake.snowpark.context import get_active_session

# Obter sessão ativa do Snowflake (não precisa de credenciais!)
session = get_active_session()

# ============================================================
# 1. BUSCAR DADOS COM SQL
# ============================================================

query = """
SELECT 
    DATA_NEGOCIACAO,
    PRECO_ABERTURA,
    PRECO_MAXIMO,
    PRECO_MINIMO,
    PRECO_FECHAMENTO,
    VOLUME,
    -- Médias Móveis calculadas diretamente no SQL
    AVG(PRECO_FECHAMENTO) OVER (
        ORDER BY DATA_NEGOCIACAO 
        ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
    ) AS MM20,
    AVG(PRECO_FECHAMENTO) OVER (
        ORDER BY DATA_NEGOCIACAO 
        ROWS BETWEEN 49 PRECEDING AND CURRENT ROW
    ) AS MM50,
    AVG(PRECO_FECHAMENTO) OVER (
        ORDER BY DATA_NEGOCIACAO 
        ROWS BETWEEN 199 PRECEDING AND CURRENT ROW
    ) AS MM200
FROM BBAS3.PUBLIC.FATO_ACOES_REAL
WHERE DATA_NEGOCIACAO >= DATEADD(month, -12, CURRENT_DATE())
ORDER BY DATA_NEGOCIACAO
"""

# Executar query e converter para pandas
df = session.sql(query).to_pandas()

# ============================================================
# 2. CRIAR GRÁFICO CANDLESTICK
# ============================================================

fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.03,
    row_heights=[0.7, 0.3],
    subplot_titles=('BBAS3 - Análise Técnica com Médias Móveis', 'Volume')
)

# Candlestick principal
fig.add_trace(
    go.Candlestick(
        x=df['DATA_NEGOCIACAO'],
        open=df['PRECO_ABERTURA'],
        high=df['PRECO_MAXIMO'],
        low=df['PRECO_MINIMO'],
        close=df['PRECO_FECHAMENTO'],
        name='BBAS3',
        increasing_line_color='#26a69a',
        decreasing_line_color='#ef5350'
    ),
    row=1, col=1
)

# Média Móvel 20 dias
fig.add_trace(
    go.Scatter(
        x=df['DATA_NEGOCIACAO'],
        y=df['MM20'],
        name='MM20',
        line=dict(color='orange', width=1.5)
    ),
    row=1, col=1
)

# Média Móvel 50 dias
fig.add_trace(
    go.Scatter(
        x=df['DATA_NEGOCIACAO'],
        y=df['MM50'],
        name='MM50',
        line=dict(color='blue', width=1.5)
    ),
    row=1, col=1
)

# Média Móvel 200 dias
fig.add_trace(
    go.Scatter(
        x=df['DATA_NEGOCIACAO'],
        y=df['MM200'],
        name='MM200',
        line=dict(color='red', width=1.5)
    ),
    row=1, col=1
)

# Volume (colorido baseado no fechamento)
colors = ['#26a69a' if row['PRECO_FECHAMENTO'] >= row['PRECO_ABERTURA'] 
          else '#ef5350' for _, row in df.iterrows()]

fig.add_trace(
    go.Bar(
        x=df['DATA_NEGOCIACAO'],
        y=df['VOLUME'],
        name='Volume',
        marker_color=colors,
        showlegend=False
    ),
    row=2, col=1
)

# ============================================================
# 3. CONFIGURAR LAYOUT
# ============================================================

fig.update_layout(
    title='BBAS3 - Gráfico Candlestick com Médias Móveis (12 Meses)',
    xaxis_title='Data',
    yaxis_title='Preço (R$)',
    yaxis2_title='Volume',
    template='plotly_dark',
    height=800,
    xaxis_rangeslider_visible=False,
    hovermode='x unified'
)

# ============================================================
# 4. EXIBIR NO SNOWFLAKE NOTEBOOK
# ============================================================

st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 5. ESTATÍSTICAS COMPLEMENTARES
# ============================================================

st.subheader("📊 Estatísticas do Período")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Preço Atual", f"R$ {df['PRECO_FECHAMENTO'].iloc[-1]:.2f}")
    
with col2:
    variacao = ((df['PRECO_FECHAMENTO'].iloc[-1] / df['PRECO_FECHAMENTO'].iloc[0]) - 1) * 100
    st.metric("Variação 12M", f"{variacao:+.2f}%")
    
with col3:
    st.metric("Máxima", f"R$ {df['PRECO_MAXIMO'].max():.2f}")
    
with col4:
    st.metric("Mínima", f"R$ {df['PRECO_MINIMO'].min():.2f}")
