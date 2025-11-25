"""
📊 STREAMLIT APP - ANÁLISE DE INVESTIMENTO BBAS3
Aplicação completa para análise de ações do Banco do Brasil com suporte à decisão de investimento

🚀 COMO USAR NO SNOWFLAKE:
1. Vá em Projects → Streamlit → + Streamlit App
2. Cole este código completo
3. Em Packages, adicione: plotly, pandas, numpy
4. Clique em "Run"
5. Compartilhe a URL com investidores

📌 Banco de Dados: BBAS3.PUBLIC
   - FATO_ACOES_REAL (preços históricos)
   - NOTICIAS_BBAS3 (sentimento de notícias)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from snowflake.snowpark.context import get_active_session

# Configuração da página
st.set_page_config(
    page_title="BBAS3 Investment Analyzer",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Obter sessão Snowflake
session = get_active_session()

# ==================== FUNÇÕES DE DADOS ====================

@st.cache_data
def carregar_dados_precos(dias=365):
    """Carrega dados de preços dos últimos N dias"""
    query = f"""
    SELECT 
        DATA_NEGOCIACAO,
        PRECO_ABERTURA,
        PRECO_MAXIMO,
        PRECO_MINIMO,
        PRECO_FECHAMENTO,
        VOLUME
    FROM BBAS3.PUBLIC.FATO_ACOES_REAL
    WHERE DATA_NEGOCIACAO >= DATEADD(day, -{dias}, CURRENT_DATE())
    ORDER BY DATA_NEGOCIACAO
    """
    df = session.sql(query).to_pandas()
    df['DATA_NEGOCIACAO'] = pd.to_datetime(df['DATA_NEGOCIACAO'])
    return df

@st.cache_data
def carregar_noticias(meses=12):
    """Carrega notícias dos últimos N meses"""
    query = f"""
    SELECT 
        ANO_PUBLICACAO,
        MES_PUBLICACAO,
        SENTIMENTO_POLARITY,
        RELEVANCIA,
        FONTE_NOTICIA
    FROM BBAS3.PUBLIC.NOTICIAS_BBAS3
    WHERE ANO_PUBLICACAO * 12 + MES_PUBLICACAO >= 
          YEAR(DATEADD(month, -{meses}, CURRENT_DATE())) * 12 + MONTH(DATEADD(month, -{meses}, CURRENT_DATE()))
    ORDER BY ANO_PUBLICACAO DESC, MES_PUBLICACAO DESC
    """
    df = session.sql(query).to_pandas()
    
    # Converter para data
    df['DATA_PUBLICACAO'] = pd.to_datetime(
        df['ANO_PUBLICACAO'].astype(str) + '-' + 
        df['MES_PUBLICACAO'].astype(str).str.zfill(2) + '-01'
    )
    return df

# ==================== INDICADORES TÉCNICOS ====================

def calcular_medias_moveis(df):
    """Calcula médias móveis 20, 50, 200"""
    df['SMA_20'] = df['PRECO_FECHAMENTO'].rolling(window=20).mean()
    df['SMA_50'] = df['PRECO_FECHAMENTO'].rolling(window=50).mean()
    df['SMA_200'] = df['PRECO_FECHAMENTO'].rolling(window=200).mean()
    return df

def calcular_rsi(df, periodo=14):
    """Calcula RSI (Relative Strength Index)"""
    delta = df['PRECO_FECHAMENTO'].diff()
    ganho = (delta.where(delta > 0, 0)).rolling(window=periodo).mean()
    perda = (-delta.where(delta < 0, 0)).rolling(window=periodo).mean()
    rs = ganho / perda
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

def calcular_macd(df):
    """Calcula MACD (Moving Average Convergence Divergence)"""
    ema_12 = df['PRECO_FECHAMENTO'].ewm(span=12, adjust=False).mean()
    ema_26 = df['PRECO_FECHAMENTO'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema_12 - ema_26
    df['SIGNAL'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['HISTOGRAM'] = df['MACD'] - df['SIGNAL']
    return df

def calcular_bollinger(df, periodo=20, num_std=2):
    """Calcula Bandas de Bollinger"""
    df['BB_MIDDLE'] = df['PRECO_FECHAMENTO'].rolling(window=periodo).mean()
    std = df['PRECO_FECHAMENTO'].rolling(window=periodo).std()
    df['BB_UPPER'] = df['BB_MIDDLE'] + (std * num_std)
    df['BB_LOWER'] = df['BB_MIDDLE'] - (std * num_std)
    return df

def gerar_sinais(df):
    """Gera sinais de compra/venda baseado em indicadores"""
    sinais = []
    
    ultimo = df.iloc[-1]
    penultimo = df.iloc[-2] if len(df) > 1 else ultimo
    
    # Sinal 1: Cruzamento de Médias (Golden Cross / Death Cross)
    if pd.notna(ultimo['SMA_20']) and pd.notna(ultimo['SMA_50']):
        if penultimo['SMA_20'] <= penultimo['SMA_50'] and ultimo['SMA_20'] > ultimo['SMA_50']:
            sinais.append({
                'tipo': 'COMPRA',
                'indicador': 'Golden Cross (SMA 20 > SMA 50)',
                'forca': 'FORTE',
                'prioridade': 1
            })
        elif penultimo['SMA_20'] >= penultimo['SMA_50'] and ultimo['SMA_20'] < ultimo['SMA_50']:
            sinais.append({
                'tipo': 'VENDA',
                'indicador': 'Death Cross (SMA 20 < SMA 50)',
                'forca': 'FORTE',
                'prioridade': 1
            })
    
    # Sinal 2: RSI (Sobrecompra/Sobrevenda)
    if pd.notna(ultimo['RSI']):
        if ultimo['RSI'] < 30:
            sinais.append({
                'tipo': 'COMPRA',
                'indicador': f'RSI Sobrevenda ({ultimo["RSI"]:.1f})',
                'forca': 'MÉDIA',
                'prioridade': 2
            })
        elif ultimo['RSI'] > 70:
            sinais.append({
                'tipo': 'VENDA',
                'indicador': f'RSI Sobrecompra ({ultimo["RSI"]:.1f})',
                'forca': 'MÉDIA',
                'prioridade': 2
            })
    
    # Sinal 3: MACD (Cruzamento)
    if pd.notna(ultimo['MACD']) and pd.notna(ultimo['SIGNAL']):
        if penultimo['MACD'] <= penultimo['SIGNAL'] and ultimo['MACD'] > ultimo['SIGNAL']:
            sinais.append({
                'tipo': 'COMPRA',
                'indicador': 'MACD cruzou Signal para cima',
                'forca': 'MÉDIA',
                'prioridade': 2
            })
        elif penultimo['MACD'] >= penultimo['SIGNAL'] and ultimo['MACD'] < ultimo['SIGNAL']:
            sinais.append({
                'tipo': 'VENDA',
                'indicador': 'MACD cruzou Signal para baixo',
                'forca': 'MÉDIA',
                'prioridade': 2
            })
    
    # Sinal 4: Bollinger Bands
    if pd.notna(ultimo['BB_LOWER']) and pd.notna(ultimo['BB_UPPER']):
        if ultimo['PRECO_FECHAMENTO'] < ultimo['BB_LOWER']:
            sinais.append({
                'tipo': 'COMPRA',
                'indicador': 'Preço abaixo da Banda Inferior',
                'forca': 'FRACA',
                'prioridade': 3
            })
        elif ultimo['PRECO_FECHAMENTO'] > ultimo['BB_UPPER']:
            sinais.append({
                'tipo': 'VENDA',
                'indicador': 'Preço acima da Banda Superior',
                'forca': 'FRACA',
                'prioridade': 3
            })
    
    return sinais

# ==================== INTERFACE PRINCIPAL ====================

# Sidebar - Navegação
st.sidebar.title("💹 BBAS3 Analyzer")
st.sidebar.markdown("---")

pagina = st.sidebar.radio(
    "Navegação",
    ["📊 Dashboard Executivo", "📈 Análise Técnica", "📰 Sentimento de Mercado", "🎯 Sinais de Trading"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Configurações")
periodo_dias = st.sidebar.slider("Período de análise (dias)", 30, 365, 180)

# Carregar dados
with st.spinner("Carregando dados..."):
    df_precos = carregar_dados_precos(periodo_dias)
    df_noticias = carregar_noticias(12)
    
    # Calcular indicadores
    df_precos = calcular_medias_moveis(df_precos)
    df_precos = calcular_rsi(df_precos)
    df_precos = calcular_macd(df_precos)
    df_precos = calcular_bollinger(df_precos)

# ==================== PÁGINA 1: DASHBOARD EXECUTIVO ====================

if pagina == "📊 Dashboard Executivo":
    st.title("📊 Dashboard Executivo - BBAS3")
    st.markdown("### Visão geral e recomendação de investimento")
    
    # Dados atuais
    ultimo_preco = df_precos.iloc[-1]
    penultimo_preco = df_precos.iloc[-2]
    variacao_dia = ((ultimo_preco['PRECO_FECHAMENTO'] - penultimo_preco['PRECO_FECHAMENTO']) / penultimo_preco['PRECO_FECHAMENTO']) * 100
    
    primeiro_preco = df_precos.iloc[0]['PRECO_FECHAMENTO']
    variacao_periodo = ((ultimo_preco['PRECO_FECHAMENTO'] - primeiro_preco) / primeiro_preco) * 100
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Preço Atual",
            f"R$ {ultimo_preco['PRECO_FECHAMENTO']:.2f}",
            f"{variacao_dia:+.2f}%"
        )
    
    with col2:
        st.metric(
            f"Variação {periodo_dias}d",
            f"{variacao_periodo:+.2f}%",
            "Alta" if variacao_periodo > 0 else "Queda"
        )
    
    with col3:
        sentimento_medio = df_noticias['SENTIMENTO_POLARITY'].mean()
        st.metric(
            "Sentimento Médio",
            f"{sentimento_medio:.3f}",
            "Positivo" if sentimento_medio > 0 else "Negativo"
        )
    
    with col4:
        rsi_atual = ultimo_preco['RSI']
        if pd.notna(rsi_atual):
            status_rsi = "Sobrecompra" if rsi_atual > 70 else "Sobrevenda" if rsi_atual < 30 else "Neutro"
            st.metric(
                "RSI (14)",
                f"{rsi_atual:.1f}",
                status_rsi
            )
    
    st.markdown("---")
    
    # Recomendação de Investimento
    sinais = gerar_sinais(df_precos)
    
    compras = [s for s in sinais if s['tipo'] == 'COMPRA']
    vendas = [s for s in sinais if s['tipo'] == 'VENDA']
    
    # Decisão baseada em scoring
    score_compra = sum([3 if s['forca'] == 'FORTE' else 2 if s['forca'] == 'MÉDIA' else 1 for s in compras])
    score_venda = sum([3 if s['forca'] == 'FORTE' else 2 if s['forca'] == 'MÉDIA' else 1 for s in vendas])
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🎯 Recomendação de Investimento")
        
        if score_compra > score_venda:
            st.success(f"""
            ### ✅ RECOMENDAÇÃO: COMPRA
            
            **Score**: {score_compra} pontos de compra vs {score_venda} pontos de venda
            
            **Sinais identificados**:
            """)
            for sinal in compras:
                st.markdown(f"- **{sinal['indicador']}** (Força: {sinal['forca']})")
        
        elif score_venda > score_compra:
            st.error(f"""
            ### ⛔ RECOMENDAÇÃO: VENDA/AGUARDAR
            
            **Score**: {score_venda} pontos de venda vs {score_compra} pontos de compra
            
            **Sinais identificados**:
            """)
            for sinal in vendas:
                st.markdown(f"- **{sinal['indicador']}** (Força: {sinal['forca']})")
        
        else:
            st.warning(f"""
            ### ⚠️ RECOMENDAÇÃO: NEUTRO (AGUARDAR)
            
            **Score**: Empate ({score_compra} x {score_venda})
            
            Sinais conflitantes. Aguardar confirmação de tendência.
            """)
    
    with col2:
        st.markdown("### 📊 Score de Sinais")
        
        # Gráfico de pizza com score
        fig_score = go.Figure(data=[go.Pie(
            labels=['Compra', 'Venda', 'Neutro'],
            values=[score_compra, score_venda, max(0, 10 - score_compra - score_venda)],
            marker=dict(colors=['#10B981', '#EF4444', '#6B7280']),
            hole=0.4
        )])
        
        fig_score.update_layout(
            height=250,
            margin=dict(t=0, b=0, l=0, r=0),
            showlegend=True
        )
        
        st.plotly_chart(fig_score, use_container_width=True)
    
    st.markdown("---")
    
    # Gráfico de preço simplificado
    st.markdown("### 📈 Evolução do Preço")
    
    fig_preco = go.Figure()
    
    fig_preco.add_trace(go.Scatter(
        x=df_precos['DATA_NEGOCIACAO'],
        y=df_precos['PRECO_FECHAMENTO'],
        name='Preço',
        line=dict(color='#1E3A8A', width=2),
        fill='tozeroy',
        fillcolor='rgba(30, 58, 138, 0.1)'
    ))
    
    fig_preco.add_trace(go.Scatter(
        x=df_precos['DATA_NEGOCIACAO'],
        y=df_precos['SMA_20'],
        name='SMA 20',
        line=dict(color='#10B981', width=1, dash='dash')
    ))
    
    fig_preco.add_trace(go.Scatter(
        x=df_precos['DATA_NEGOCIACAO'],
        y=df_precos['SMA_50'],
        name='SMA 50',
        line=dict(color='#F59E0B', width=1, dash='dash')
    ))
    
    fig_preco.update_layout(
        height=400,
        xaxis_title="Data",
        yaxis_title="Preço (R$)",
        hovermode='x unified',
        template='plotly_white'
    )
    
    st.plotly_chart(fig_preco, use_container_width=True)

# ==================== PÁGINA 2: ANÁLISE TÉCNICA ====================

elif pagina == "📈 Análise Técnica":
    st.title("📈 Análise Técnica Completa - BBAS3")
    
    # Candlestick + Volume + RSI + MACD
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.5, 0.15, 0.2, 0.15],
        subplot_titles=('Preço + Médias Móveis + Bollinger', 'Volume', 'RSI (14)', 'MACD')
    )
    
    # 1. Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df_precos['DATA_NEGOCIACAO'],
            open=df_precos['PRECO_ABERTURA'],
            high=df_precos['PRECO_MAXIMO'],
            low=df_precos['PRECO_MINIMO'],
            close=df_precos['PRECO_FECHAMENTO'],
            name='BBAS3',
            increasing_line_color='#10B981',
            decreasing_line_color='#EF4444'
        ),
        row=1, col=1
    )
    
    # Médias Móveis
    fig.add_trace(
        go.Scatter(x=df_precos['DATA_NEGOCIACAO'], y=df_precos['SMA_20'],
                   name='SMA 20', line=dict(color='cyan', width=1)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df_precos['DATA_NEGOCIACAO'], y=df_precos['SMA_50'],
                   name='SMA 50', line=dict(color='orange', width=1)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df_precos['DATA_NEGOCIACAO'], y=df_precos['SMA_200'],
                   name='SMA 200', line=dict(color='purple', width=1)),
        row=1, col=1
    )
    
    # Bollinger Bands
    fig.add_trace(
        go.Scatter(x=df_precos['DATA_NEGOCIACAO'], y=df_precos['BB_UPPER'],
                   name='BB Superior', line=dict(color='gray', width=1, dash='dot'),
                   showlegend=False),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df_precos['DATA_NEGOCIACAO'], y=df_precos['BB_LOWER'],
                   name='BB Inferior', line=dict(color='gray', width=1, dash='dot'),
                   fill='tonexty', fillcolor='rgba(128, 128, 128, 0.1)',
                   showlegend=False),
        row=1, col=1
    )
    
    # 2. Volume
    colors_volume = ['#10B981' if df_precos.iloc[i]['PRECO_FECHAMENTO'] >= df_precos.iloc[i]['PRECO_ABERTURA'] 
                     else '#EF4444' for i in range(len(df_precos))]
    
    fig.add_trace(
        go.Bar(x=df_precos['DATA_NEGOCIACAO'], y=df_precos['VOLUME'],
               name='Volume', marker_color=colors_volume),
        row=2, col=1
    )
    
    # 3. RSI
    fig.add_trace(
        go.Scatter(x=df_precos['DATA_NEGOCIACAO'], y=df_precos['RSI'],
                   name='RSI', line=dict(color='purple', width=2)),
        row=3, col=1
    )
    
    # Linhas de referência RSI
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1, annotation_text="Sobrecompra (70)")
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1, annotation_text="Sobrevenda (30)")
    fig.add_hline(y=50, line_dash="dot", line_color="gray", row=3, col=1)
    
    # 4. MACD
    fig.add_trace(
        go.Scatter(x=df_precos['DATA_NEGOCIACAO'], y=df_precos['MACD'],
                   name='MACD', line=dict(color='blue', width=2)),
        row=4, col=1
    )
    fig.add_trace(
        go.Scatter(x=df_precos['DATA_NEGOCIACAO'], y=df_precos['SIGNAL'],
                   name='Signal', line=dict(color='orange', width=2)),
        row=4, col=1
    )
    
    # Histograma MACD
    colors_macd = ['#10B981' if val >= 0 else '#EF4444' for val in df_precos['HISTOGRAM']]
    fig.add_trace(
        go.Bar(x=df_precos['DATA_NEGOCIACAO'], y=df_precos['HISTOGRAM'],
               name='Histograma', marker_color=colors_macd),
        row=4, col=1
    )
    
    fig.update_layout(
        height=1000,
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        template='plotly_dark'
    )
    
    fig.update_yaxes(title_text="Preço (R$)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_yaxes(title_text="RSI", row=3, col=1)
    fig.update_yaxes(title_text="MACD", row=4, col=1)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela de indicadores atuais
    st.markdown("### 📊 Indicadores Atuais")
    
    ultimo = df_precos.iloc[-1]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Médias Móveis**")
        st.write(f"SMA 20: R$ {ultimo['SMA_20']:.2f}")
        st.write(f"SMA 50: R$ {ultimo['SMA_50']:.2f}")
        st.write(f"SMA 200: R$ {ultimo['SMA_200']:.2f}")
    
    with col2:
        st.markdown("**Osciladores**")
        st.write(f"RSI (14): {ultimo['RSI']:.2f}")
        st.write(f"MACD: {ultimo['MACD']:.4f}")
        st.write(f"Signal: {ultimo['SIGNAL']:.4f}")
    
    with col3:
        st.markdown("**Bollinger Bands**")
        st.write(f"Superior: R$ {ultimo['BB_UPPER']:.2f}")
        st.write(f"Médio: R$ {ultimo['BB_MIDDLE']:.2f}")
        st.write(f"Inferior: R$ {ultimo['BB_LOWER']:.2f}")

# ==================== PÁGINA 3: SENTIMENTO DE MERCADO ====================

elif pagina == "📰 Sentimento de Mercado":
    st.title("📰 Análise de Sentimento - BBAS3")
    st.markdown("### Correlação entre notícias e preço da ação")
    
    # Agregação semanal
    df_noticias['SEMANA'] = pd.to_datetime(df_noticias['DATA_PUBLICACAO']).dt.to_period('W').apply(lambda r: r.start_time)
    
    df_sentimento = df_noticias.groupby('SEMANA').agg({
        'SENTIMENTO_POLARITY': 'mean',
        'RELEVANCIA': 'mean',
        'ANO_PUBLICACAO': 'count'
    }).reset_index()
    df_sentimento.columns = ['SEMANA', 'SENTIMENTO_MEDIO', 'RELEVANCIA_MEDIA', 'TOTAL_NOTICIAS']
    
    # Preços semanais
    df_precos['SEMANA'] = pd.to_datetime(df_precos['DATA_NEGOCIACAO']).dt.to_period('W').apply(lambda r: r.start_time)
    df_precos_semanal = df_precos.groupby('SEMANA').agg({
        'PRECO_FECHAMENTO': 'last',
        'VOLUME': 'sum'
    }).reset_index()
    
    # Merge
    df_correlacao = pd.merge(df_precos_semanal, df_sentimento, on='SEMANA', how='left')
    df_correlacao['SENTIMENTO_MEDIO'] = df_correlacao['SENTIMENTO_MEDIO'].fillna(0)
    df_correlacao['TOTAL_NOTICIAS'] = df_correlacao['TOTAL_NOTICIAS'].fillna(0)
    
    # Calcular correlação
    if df_correlacao['SENTIMENTO_MEDIO'].std() > 0:
        correlacao = df_correlacao['SENTIMENTO_MEDIO'].corr(df_correlacao['PRECO_FECHAMENTO'])
    else:
        correlacao = 0.0
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Notícias", len(df_noticias))
    
    with col2:
        sentimento_geral = df_noticias['SENTIMENTO_POLARITY'].mean()
        st.metric("Sentimento Geral", f"{sentimento_geral:.3f}",
                  "Positivo" if sentimento_geral > 0 else "Negativo")
    
    with col3:
        st.metric("Correlação Pearson", f"{correlacao:.4f}",
                  "Positiva" if correlacao > 0 else "Negativa")
    
    with col4:
        semanas_positivas = (df_correlacao['SENTIMENTO_MEDIO'] > 0).sum()
        total_semanas = len(df_correlacao)
        st.metric("Semanas Positivas", f"{semanas_positivas}/{total_semanas}")
    
    st.markdown("---")
    
    # Gráfico de correlação
    fig_correlacao = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3],
        subplot_titles=('Preço vs Sentimento Semanal', 'Volume de Notícias')
    )
    
    # Linha de preço
    fig_correlacao.add_trace(
        go.Scatter(
            x=df_correlacao['SEMANA'],
            y=df_correlacao['PRECO_FECHAMENTO'],
            name='Preço de Fechamento',
            line=dict(color='cyan', width=2),
            yaxis='y1'
        ),
        row=1, col=1
    )
    
    # Barras de sentimento
    cores_sentimento = ['#10B981' if s > 0 else '#EF4444' if s < 0 else '#6B7280' 
                        for s in df_correlacao['SENTIMENTO_MEDIO']]
    
    fig_correlacao.add_trace(
        go.Bar(
            x=df_correlacao['SEMANA'],
            y=df_correlacao['SENTIMENTO_MEDIO'],
            name='Sentimento Médio',
            marker_color=cores_sentimento,
            yaxis='y2',
            opacity=0.6
        ),
        row=1, col=1
    )
    
    # Volume de notícias
    fig_correlacao.add_trace(
        go.Bar(
            x=df_correlacao['SEMANA'],
            y=df_correlacao['TOTAL_NOTICIAS'],
            name='Qtd. Notícias',
            marker_color='#F59E0B'
        ),
        row=2, col=1
    )
    
    fig_correlacao.update_layout(
        height=700,
        hovermode='x unified',
        template='plotly_white',
        yaxis=dict(title='Preço (R$)', side='left'),
        yaxis2=dict(title='Sentimento', overlaying='y', side='right')
    )
    
    st.plotly_chart(fig_correlacao, use_container_width=True)
    
    # Distribuição de sentimento
    st.markdown("### 📊 Distribuição de Sentimento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Histograma
        fig_hist = go.Figure(data=[go.Histogram(
            x=df_noticias['SENTIMENTO_POLARITY'],
            nbinsx=30,
            marker_color='#1E3A8A'
        )])
        
        fig_hist.update_layout(
            title="Distribuição de Sentimento das Notícias",
            xaxis_title="Sentimento Polarity",
            yaxis_title="Frequência",
            height=400
        )
        
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        # Top fontes
        top_fontes = df_noticias['FONTE_NOTICIA'].value_counts().head(10)
        
        fig_fontes = go.Figure(data=[go.Bar(
            x=top_fontes.values,
            y=top_fontes.index,
            orientation='h',
            marker_color='#10B981'
        )])
        
        fig_fontes.update_layout(
            title="Top 10 Fontes de Notícias",
            xaxis_title="Quantidade",
            yaxis_title="Fonte",
            height=400
        )
        
        st.plotly_chart(fig_fontes, use_container_width=True)
    
    # Últimas notícias
    st.markdown("### 📰 Notícias Recentes (Resumo por Mês)")
    
    ultimas_noticias = df_noticias.groupby(['ANO_PUBLICACAO', 'MES_PUBLICACAO']).agg({
        'SENTIMENTO_POLARITY': 'mean',
        'RELEVANCIA': 'mean',
        'FONTE_NOTICIA': 'count'
    }).reset_index().sort_values(['ANO_PUBLICACAO', 'MES_PUBLICACAO'], ascending=False).head(10)
    
    ultimas_noticias.columns = ['Ano', 'Mês', 'Sentimento Médio', 'Relevância Média', 'Qtd. Notícias']
    
    for _, noticia in ultimas_noticias.iterrows():
        sentimento = noticia['Sentimento Médio']
        sentimento_emoji = "🟢" if sentimento > 0.1 else "🔴" if sentimento < -0.1 else "⚪"
        
        with st.expander(f"{sentimento_emoji} {int(noticia['Mês']):02d}/{int(noticia['Ano'])} - {int(noticia['Qtd. Notícias'])} notícias"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Período**: {int(noticia['Mês']):02d}/{int(noticia['Ano'])}")
            with col2:
                st.write(f"**Sentimento**: {noticia['Sentimento Médio']:.3f}")
            with col3:
                st.write(f"**Qtd**: {int(noticia['Qtd. Notícias'])} notícias")

# ==================== PÁGINA 4: SINAIS DE TRADING ====================

elif pagina == "🎯 Sinais de Trading":
    st.title("🎯 Sinais de Trading - BBAS3")
    st.markdown("### Sistema de alertas para compra e venda")
    
    sinais = gerar_sinais(df_precos)
    
    if not sinais:
        st.info("🔵 Nenhum sinal forte identificado no momento. Mercado em consolidação.")
    else:
        # Separar por tipo
        compras = [s for s in sinais if s['tipo'] == 'COMPRA']
        vendas = [s for s in sinais if s['tipo'] == 'VENDA']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ✅ Sinais de COMPRA")
            if compras:
                for sinal in sorted(compras, key=lambda x: x['prioridade']):
                    cor = "#10B981" if sinal['forca'] == 'FORTE' else "#F59E0B" if sinal['forca'] == 'MÉDIA' else "#6B7280"
                    st.markdown(f"""
                    <div style='padding: 10px; background-color: {cor}22; border-left: 4px solid {cor}; margin: 10px 0;'>
                        <strong>{sinal['indicador']}</strong><br>
                        <small>Força: {sinal['forca']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhum sinal de compra no momento")
        
        with col2:
            st.markdown("### ⛔ Sinais de VENDA")
            if vendas:
                for sinal in sorted(vendas, key=lambda x: x['prioridade']):
                    cor = "#EF4444" if sinal['forca'] == 'FORTE' else "#F59E0B" if sinal['forca'] == 'MÉDIA' else "#6B7280"
                    st.markdown(f"""
                    <div style='padding: 10px; background-color: {cor}22; border-left: 4px solid {cor}; margin: 10px 0;'>
                        <strong>{sinal['indicador']}</strong><br>
                        <small>Força: {sinal['forca']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhum sinal de venda no momento")
    
    st.markdown("---")
    
    # Painel de controle
    st.markdown("### 🎛️ Painel de Controle")
    
    ultimo = df_precos.iloc[-1]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        tendencia = "Alta" if ultimo['SMA_20'] > ultimo['SMA_50'] else "Baixa"
        cor_tendencia = "#10B981" if tendencia == "Alta" else "#EF4444"
        st.markdown(f"**Tendência**: <span style='color:{cor_tendencia}'>{tendencia}</span>", unsafe_allow_html=True)
        st.write(f"Preço: R$ {ultimo['PRECO_FECHAMENTO']:.2f}")
    
    with col2:
        status_rsi = "Sobrecompra" if ultimo['RSI'] > 70 else "Sobrevenda" if ultimo['RSI'] < 30 else "Neutro"
        cor_rsi = "#EF4444" if status_rsi == "Sobrecompra" else "#10B981" if status_rsi == "Sobrevenda" else "#6B7280"
        st.markdown(f"**RSI**: <span style='color:{cor_rsi}'>{status_rsi}</span>", unsafe_allow_html=True)
        st.write(f"Valor: {ultimo['RSI']:.1f}")
    
    with col3:
        status_macd = "Compra" if ultimo['MACD'] > ultimo['SIGNAL'] else "Venda"
        cor_macd = "#10B981" if status_macd == "Compra" else "#EF4444"
        st.markdown(f"**MACD**: <span style='color:{cor_macd}'>{status_macd}</span>", unsafe_allow_html=True)
        st.write(f"Histograma: {ultimo['HISTOGRAM']:.4f}")
    
    with col4:
        posicao_bb = "Acima" if ultimo['PRECO_FECHAMENTO'] > ultimo['BB_UPPER'] else "Abaixo" if ultimo['PRECO_FECHAMENTO'] < ultimo['BB_LOWER'] else "Dentro"
        cor_bb = "#EF4444" if posicao_bb == "Acima" else "#10B981" if posicao_bb == "Abaixo" else "#6B7280"
        st.markdown(f"**Bollinger**: <span style='color:{cor_bb}'>{posicao_bb}</span>", unsafe_allow_html=True)
        st.write(f"Largura: R$ {(ultimo['BB_UPPER'] - ultimo['BB_LOWER']):.2f}")
    
    st.markdown("---")
    
    # Histórico de performance
    st.markdown("### 📊 Análise de Performance")
    
    # Calcular retornos
    df_precos['RETORNO_DIARIO'] = df_precos['PRECO_FECHAMENTO'].pct_change() * 100
    
    retorno_medio = df_precos['RETORNO_DIARIO'].mean()
    volatilidade = df_precos['RETORNO_DIARIO'].std()
    max_alta = df_precos['RETORNO_DIARIO'].max()
    max_queda = df_precos['RETORNO_DIARIO'].min()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Retorno Médio Diário", f"{retorno_medio:.2f}%")
    with col2:
        st.metric("Volatilidade", f"{volatilidade:.2f}%")
    with col3:
        st.metric("Maior Alta", f"{max_alta:.2f}%", delta_color="normal")
    with col4:
        st.metric("Maior Queda", f"{max_queda:.2f}%", delta_color="inverse")
    
    # Gráfico de distribuição de retornos
    fig_retornos = go.Figure()
    
    fig_retornos.add_trace(go.Histogram(
        x=df_precos['RETORNO_DIARIO'].dropna(),
        nbinsx=50,
        marker_color='#1E3A8A',
        name='Retornos Diários'
    ))
    
    fig_retornos.update_layout(
        title="Distribuição de Retornos Diários",
        xaxis_title="Retorno (%)",
        yaxis_title="Frequência",
        height=400,
        template='plotly_white'
    )
    
    st.plotly_chart(fig_retornos, use_container_width=True)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
### 📝 Notas
- Dados atualizados do Snowflake
- Indicadores calculados em tempo real
- Recomendações são sugestões, não garantias
- Sempre faça sua própria análise
""")

st.sidebar.markdown("---")
st.sidebar.info("💹 **BBAS3 Investment Analyzer** v1.0")
