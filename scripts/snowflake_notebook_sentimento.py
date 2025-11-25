# ============================================================
# SNOWFLAKE NOTEBOOK - Correlação Sentimento × Preço BBAS3
# ============================================================

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from snowflake.snowpark.context import get_active_session

session = get_active_session()

# ============================================================
# 1. BUSCAR DADOS - JOIN ENTRE NOTÍCIAS E PREÇOS
# ============================================================

# Primeiro, vamos buscar os dados de preço
query_precos = """
SELECT 
    DATA_NEGOCIACAO,
    PRECO_FECHAMENTO,
    VOLUME
FROM BBAS3.PUBLIC.FATO_ACOES_REAL
WHERE DATA_NEGOCIACAO >= DATEADD(month, -12, CURRENT_DATE())
ORDER BY DATA_NEGOCIACAO
"""

df_precos = session.sql(query_precos).to_pandas()

# SOLUÇÃO ALTERNATIVA: Usar campos ANO_PUBLICACAO e MES_PUBLICACAO ao invés de PUBLICADA
query_sentimento = """
SELECT 
    ANO_PUBLICACAO,
    MES_PUBLICACAO,
    SENTIMENTO_POLARITY,
    RELEVANCIA
FROM BBAS3.PUBLIC.NOTICIAS_BBAS3
WHERE ANO_PUBLICACAO IS NOT NULL 
  AND MES_PUBLICACAO IS NOT NULL
ORDER BY ANO_PUBLICACAO DESC, MES_PUBLICACAO DESC
"""

df_noticias = session.sql(query_sentimento).to_pandas()

# Criar data a partir de ANO e MES
try:
    df_noticias['DATA_PUBLICACAO'] = pd.to_datetime(
        df_noticias['ANO_PUBLICACAO'].astype(str) + '-' + 
        df_noticias['MES_PUBLICACAO'].astype(str).str.zfill(2) + '-01'
    )
    st.success(f"✅ Convertidas {len(df_noticias)} notícias usando ANO_PUBLICACAO e MES_PUBLICACAO")
except Exception as e:
    st.error(f"Erro ao converter datas: {e}")
    df_noticias = pd.DataFrame()

# Debug: Mostrar quantas notícias foram encontradas
st.write(f"📰 Notícias encontradas: {len(df_noticias)}")
st.write(f"📅 Período notícias: {df_noticias['DATA_PUBLICACAO'].min()} a {df_noticias['DATA_PUBLICACAO'].max()}")
st.write(f"📊 Preços encontrados: {len(df_precos)}")

# Se não houver notícias, usar abordagem alternativa
if len(df_noticias) == 0:
    st.warning("⚠️ Nenhuma notícia encontrada nos últimos 12 meses. Usando dados simulados para demonstração.")
    # Usar apenas dados de preço
    df = df_precos.copy()
    df.rename(columns={'DATA_NEGOCIACAO': 'DATA_NEGOCIACAO', 'VOLUME': 'VOLUME_ACOES'}, inplace=True)
    df['SENTIMENTO_MEDIO'] = 0.0
    df['RELEVANCIA_MEDIA'] = 0.5
    df['VOLUME_NOTICIAS'] = 0
else:
    # Agrupar notícias por semana em pandas
    df_noticias['SEMANA'] = pd.to_datetime(df_noticias['DATA_PUBLICACAO']).dt.to_period('W').apply(lambda r: r.start_time)
    df_sentimento = df_noticias.groupby('SEMANA').agg({
        'SENTIMENTO_POLARITY': 'mean',
        'RELEVANCIA': 'mean',
        'DATA_PUBLICACAO': 'count'
    }).reset_index()
    
    df_sentimento.rename(columns={
        'SENTIMENTO_POLARITY': 'SENTIMENTO_MEDIO',
        'RELEVANCIA': 'RELEVANCIA_MEDIA',
        'DATA_PUBLICACAO': 'VOLUME_NOTICIAS'
    }, inplace=True)
    
    # Agrupar preços por semana
    df_precos['SEMANA'] = pd.to_datetime(df_precos['DATA_NEGOCIACAO']).dt.to_period('W').apply(lambda r: r.start_time)
    df_precos_semanal = df_precos.groupby('SEMANA').agg({
        'PRECO_FECHAMENTO': 'mean',
        'VOLUME': 'sum'
    }).reset_index()
    
    # Fazer merge dos dataframes (LEFT JOIN para manter todos os preços)
    df = pd.merge(
        df_precos_semanal,
        df_sentimento,
        on='SEMANA',
        how='left'
    )
    
    # Preencher valores ausentes
    df['SENTIMENTO_MEDIO'] = df['SENTIMENTO_MEDIO'].fillna(0)
    df['RELEVANCIA_MEDIA'] = df['RELEVANCIA_MEDIA'].fillna(0.5)
    df['VOLUME_NOTICIAS'] = df['VOLUME_NOTICIAS'].fillna(0)
    
    # Renomear colunas para compatibilidade
    df.rename(columns={
        'SEMANA': 'DATA_NEGOCIACAO',
        'VOLUME': 'VOLUME_ACOES'
    }, inplace=True)

st.write(f"✅ Dados finais para o gráfico: {len(df)} semanas")

# ============================================================
# 2. CRIAR GRÁFICO DE CORRELAÇÃO (DOIS EIXOS Y)
# ============================================================

fig = make_subplots(specs=[[{"secondary_y": True}]])

# Linha de Preço (eixo esquerdo)
fig.add_trace(
    go.Scatter(
        x=df['DATA_NEGOCIACAO'],
        y=df['PRECO_FECHAMENTO'],
        name='Preço Fechamento',
        line=dict(color='cyan', width=2),
        yaxis='y'
    ),
    secondary_y=False
)

# Barras de Sentimento (eixo direito)
colors = ['green' if s > 0 else 'red' if s < 0 else 'gray' 
          for s in df['SENTIMENTO_MEDIO']]

fig.add_trace(
    go.Bar(
        x=df['DATA_NEGOCIACAO'],
        y=df['SENTIMENTO_MEDIO'],
        name='Sentimento Médio',
        marker_color=colors,
        opacity=0.6,
        yaxis='y2'
    ),
    secondary_y=True
)

# Bolhas de Volume de Notícias (tamanho = quantidade, cor = relevância)
fig.add_trace(
    go.Scatter(
        x=df['DATA_NEGOCIACAO'],
        y=df['PRECO_FECHAMENTO'],
        mode='markers',
        name='Volume Notícias',
        marker=dict(
            size=df['VOLUME_NOTICIAS'] * 3,  # Amplificar para visualização
            color=df['RELEVANCIA_MEDIA'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Relevância"),
            line=dict(width=0.5, color='white')
        ),
        text=[f"{int(v)} notícias<br>Relevância: {r:.2f}" 
              for v, r in zip(df['VOLUME_NOTICIAS'], df['RELEVANCIA_MEDIA'])],
        hovertemplate='%{text}<extra></extra>'
    ),
    secondary_y=False
)

# ============================================================
# 3. CONFIGURAR LAYOUT
# ============================================================

fig.update_layout(
    title='BBAS3 - Correlação entre Sentimento de Notícias e Preço',
    template='plotly_dark',
    height=600,
    hovermode='x unified',
    legend=dict(x=0.01, y=0.99)
)

fig.update_xaxes(title_text="Data")
fig.update_yaxes(title_text="Preço (R$)", secondary_y=False)
fig.update_yaxes(title_text="Sentimento (-1 a +1)", secondary_y=True)

st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 4. ANÁLISE DE CORRELAÇÃO
# ============================================================

st.subheader("📈 Análise de Correlação")

# Calcular correlação com tratamento de erro
try:
    if df['SENTIMENTO_MEDIO'].std() == 0 or df['PRECO_FECHAMENTO'].std() == 0:
        correlacao = 0.0
        st.warning("⚠️ Não há variação suficiente nos dados para calcular correlação")
    else:
        correlacao = df['SENTIMENTO_MEDIO'].corr(df['PRECO_FECHAMENTO'])
        if pd.isna(correlacao):
            correlacao = 0.0
except:
    correlacao = 0.0
    st.warning("⚠️ Erro ao calcular correlação")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Correlação Pearson", f"{correlacao:.4f}")
    
with col2:
    sentimento_positivo = len(df[df['SENTIMENTO_MEDIO'] > 0])
    st.metric("Dias com Sentimento Positivo", f"{sentimento_positivo}/{len(df)}")
    
with col3:
    st.metric("Total de Notícias", f"{int(df['VOLUME_NOTICIAS'].sum())}")

# Interpretação
if correlacao > 0.5:
    interpretacao = "🟢 **Forte correlação positiva**: Notícias positivas tendem a acompanhar aumento de preço"
elif correlacao > 0.2:
    interpretacao = "🟡 **Correlação positiva moderada**: Há alguma relação entre sentimento e preço"
elif correlacao > -0.2:
    interpretacao = "⚪ **Correlação fraca**: Sentimento e preço não apresentam relação clara"
else:
    interpretacao = "🔴 **Correlação negativa**: Padrão inverso entre sentimento e preço"

st.info(interpretacao)
