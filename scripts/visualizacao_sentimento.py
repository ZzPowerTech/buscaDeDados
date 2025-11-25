"""
Gráfico de Correlação: Sentimento × Preço
Dual-Axis com áreas coloridas
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

print("📰 Gerando Gráfico de Correlação Sentimento × Preço...")

conn = connect(
    user=settings.snowflake.user,
    password=settings.snowflake.password,
    account=settings.snowflake.account,
    warehouse=settings.snowflake.warehouse,
    database=settings.snowflake.database,
    schema=settings.snowflake.schema
)

query = """
WITH sentimento_diario AS (
    SELECT 
        TO_DATE(TO_TIMESTAMP(PUBLICADA / 1000)) as data,
        AVG(SENTIMENTO_POLARITY) as sentimento,
        COUNT(*) as volume_noticias,
        AVG(RELEVANCIA) as relevancia
    FROM BBAS3.PUBLIC.NOTICIAS_BBAS3
    GROUP BY data
),
acoes_diarias AS (
    SELECT 
        DATA_NEGOCIACAO as data,
        PRECO_FECHAMENTO as preco,
        VARIACAO_PERCENTUAL as variacao,
        VOLUME
    FROM BBAS3.PUBLIC.FATO_ACOES_REAL
)
SELECT 
    a.data,
    a.preco,
    a.variacao,
    COALESCE(s.sentimento, 0) as sentimento,
    COALESCE(s.volume_noticias, 0) as noticias,
    COALESCE(s.relevancia, 0) as relevancia
FROM acoes_diarias a
LEFT JOIN sentimento_diario s ON a.data = s.data
WHERE a.data >= DATEADD(month, -6, CURRENT_DATE())
ORDER BY a.data
"""

df = pd.read_sql(query, conn)
conn.close()

print(f"✅ {len(df)} dias analisados")

# Criar figura com eixo Y secundário
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Preço (linha)
fig.add_trace(
    go.Scatter(
        x=df['DATA'], 
        y=df['PRECO'],
        name='Preço BBAS3',
        line=dict(color='#2196F3', width=2),
        fill='tozeroy',
        fillcolor='rgba(33, 150, 243, 0.1)'
    ),
    secondary_y=False
)

# Sentimento (área)
colors_sentimento = ['rgba(76, 175, 80, 0.6)' if x > 0 else 'rgba(244, 67, 54, 0.6)' 
                     for x in df['SENTIMENTO']]

fig.add_trace(
    go.Bar(
        x=df['DATA'],
        y=df['SENTIMENTO'],
        name='Sentimento Médio',
        marker_color=colors_sentimento,
        opacity=0.7
    ),
    secondary_y=True
)

# Volume de notícias (tamanho dos pontos)
fig.add_trace(
    go.Scatter(
        x=df['DATA'],
        y=df['SENTIMENTO'],
        mode='markers',
        name='Volume Notícias',
        marker=dict(
            size=df['NOTICIAS'] * 2,
            color=df['RELEVANCIA'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Relevância"),
            line=dict(width=1, color='white')
        ),
        text=df['NOTICIAS'],
        hovertemplate='<b>%{x}</b><br>Sentimento: %{y:.3f}<br>Notícias: %{text}<extra></extra>'
    ),
    secondary_y=True
)

# Layout
fig.update_layout(
    title='Impacto do Sentimento das Notícias no Preço BBAS3',
    template='plotly_dark',
    hovermode='x unified',
    height=600,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

fig.update_xaxes(title_text="Data")
fig.update_yaxes(title_text="Preço (R$)", secondary_y=False)
fig.update_yaxes(title_text="Sentimento", secondary_y=True)

# Adicionar linha zero no sentimento
fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.3, secondary_y=True)

output_file = root_dir / 'data' / 'correlacao_sentimento_preco.html'
fig.write_html(str(output_file))
print(f"\n✅ Gráfico salvo em: {output_file}")
print("🌐 Abrindo no navegador...")
fig.show()
