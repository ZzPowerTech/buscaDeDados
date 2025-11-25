"""
Heatmap de Correlação: Sentimento × Performance
Mostra meses com melhor/pior alinhamento
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.config import settings
from snowflake.connector import connect

print("🔥 Gerando Heatmap de Correlação...")

conn = connect(
    user=settings.snowflake.user,
    password=settings.snowflake.password,
    account=settings.snowflake.account,
    warehouse=settings.snowflake.warehouse,
    database=settings.snowflake.database,
    schema=settings.snowflake.schema
)

query = """
WITH metricas_mensais AS (
    SELECT 
        YEAR(DATA_NEGOCIACAO) as ano,
        MONTH(DATA_NEGOCIACAO) as mes,
        AVG(VARIACAO_PERCENTUAL) as retorno_medio,
        STDDEV(VARIACAO_PERCENTUAL) as volatilidade
    FROM BBAS3.PUBLIC.FATO_ACOES_REAL
    GROUP BY ano, mes
),
sentimento_mensal AS (
    SELECT 
        YEAR(TO_DATE(TO_TIMESTAMP(PUBLICADA / 1000))) as ano,
        MONTH(TO_DATE(TO_TIMESTAMP(PUBLICADA / 1000))) as mes,
        AVG(SENTIMENTO_POLARITY) as sentimento,
        COUNT(*) as volume_noticias
    FROM BBAS3.PUBLIC.NOTICIAS_BBAS3
    GROUP BY ano, mes
)
SELECT 
    m.ano,
    m.mes,
    ROUND(m.retorno_medio, 2) as retorno,
    ROUND(m.volatilidade, 2) as volatilidade,
    ROUND(COALESCE(s.sentimento, 0), 3) as sentimento,
    COALESCE(s.volume_noticias, 0) as noticias,
    ROUND((m.retorno_medio * 10) + (COALESCE(s.sentimento, 0) * 5), 2) as score_oportunidade
FROM metricas_mensais m
LEFT JOIN sentimento_mensal s ON m.ano = s.ano AND m.mes = s.mes
ORDER BY m.ano, m.mes
"""

df = pd.read_sql(query, conn)
conn.close()

# Preparar dados para heatmap
df['periodo'] = df['ANO'].astype(str) + '-' + df['MES'].astype(str).str.zfill(2)
meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

# Pivot para heatmap
pivot_retorno = df.pivot(index='ANO', columns='MES', values='RETORNO')
pivot_sentimento = df.pivot(index='ANO', columns='MES', values='SENTIMENTO')
pivot_score = df.pivot(index='ANO', columns='MES', values='SCORE_OPORTUNIDADE')

print(f"✅ {len(df)} meses analisados")

# Criar subplots para 3 heatmaps
fig = make_subplots(
    rows=3, cols=1,
    subplot_titles=(
        'Retorno Mensal (%)',
        'Sentimento Médio',
        'Score de Oportunidade (Combinado)'
    ),
    vertical_spacing=0.08
)

# Heatmap 1: Retorno
fig.add_trace(
    go.Heatmap(
        z=pivot_retorno.values,
        x=meses[:len(pivot_retorno.columns)],
        y=pivot_retorno.index,
        colorscale='RdYlGn',
        text=pivot_retorno.values,
        texttemplate='%{text:.1f}%',
        colorbar=dict(title="Retorno %", x=1.12, len=0.3, y=0.85),
        hoverongaps=False
    ),
    row=1, col=1
)

# Heatmap 2: Sentimento
fig.add_trace(
    go.Heatmap(
        z=pivot_sentimento.values,
        x=meses[:len(pivot_sentimento.columns)],
        y=pivot_sentimento.index,
        colorscale='RdBu',
        text=pivot_sentimento.values,
        texttemplate='%{text:.2f}',
        colorbar=dict(title="Sentimento", x=1.12, len=0.3, y=0.5),
        hoverongaps=False
    ),
    row=2, col=1
)

# Heatmap 3: Score Combinado
fig.add_trace(
    go.Heatmap(
        z=pivot_score.values,
        x=meses[:len(pivot_score.columns)],
        y=pivot_score.index,
        colorscale='Viridis',
        text=pivot_score.values,
        texttemplate='%{text:.1f}',
        colorbar=dict(title="Score", x=1.12, len=0.3, y=0.15),
        hoverongaps=False
    ),
    row=3, col=1
)

fig.update_layout(
    title='Análise Temporal: Retorno vs Sentimento - BBAS3',
    template='plotly_dark',
    height=900,
    showlegend=False
)

fig.update_xaxes(title_text="Mês")
fig.update_yaxes(title_text="Ano")

output_file = root_dir / 'data' / 'heatmap_correlacao.html'
fig.write_html(str(output_file))
print(f"\n✅ Heatmap salvo em: {output_file}")
print("🌐 Abrindo no navegador...")
fig.show()
