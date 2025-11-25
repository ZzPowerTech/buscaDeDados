-- ============================================================
-- QUERIES SQL PARA SNOWSIGHT DASHBOARDS
-- ============================================================
-- Cole cada query em um tile separado do dashboard

-- ============================================================
-- 1. CORRELAÇÃO SEMANAL: SENTIMENTO × PREÇO
-- ============================================================
-- Tipo de gráfico: Line Chart (dual axis)
-- Eixo Y1: PRECO_MEDIO | Eixo Y2: SENTIMENTO_MEDIO

WITH noticias_semanal AS (
    SELECT 
        DATE_TRUNC('WEEK', DATEADD(DAY, 1, 
            DATEADD(MONTH, MES_PUBLICACAO - 1, 
                DATEADD(YEAR, ANO_PUBLICACAO - 1970, '1970-01-01'::DATE)
            )
        )) AS semana,
        AVG(SENTIMENTO_POLARITY) AS sentimento_medio,
        COUNT(*) AS volume_noticias,
        AVG(RELEVANCIA) AS relevancia_media
    FROM BBAS3.PUBLIC.NOTICIAS_BBAS3
    WHERE ANO_PUBLICACAO IS NOT NULL 
      AND MES_PUBLICACAO IS NOT NULL
    GROUP BY semana
),
precos_semanal AS (
    SELECT 
        DATE_TRUNC('WEEK', DATA_NEGOCIACAO) AS semana,
        AVG(PRECO_FECHAMENTO) AS preco_medio,
        SUM(VOLUME) AS volume_acoes
    FROM BBAS3.PUBLIC.FATO_ACOES_REAL
    WHERE DATA_NEGOCIACAO >= DATEADD(month, -12, CURRENT_DATE())
    GROUP BY semana
)
SELECT 
    p.semana AS DATA,
    p.preco_medio AS PRECO_MEDIO,
    COALESCE(n.sentimento_medio, 0) AS SENTIMENTO_MEDIO,
    COALESCE(n.volume_noticias, 0) AS VOLUME_NOTICIAS,
    p.volume_acoes AS VOLUME_ACOES
FROM precos_semanal p
LEFT JOIN noticias_semanal n ON p.semana = n.semana
ORDER BY p.semana;

-- ============================================================
-- 2. DISTRIBUIÇÃO DE SENTIMENTO
-- ============================================================
-- Tipo de gráfico: Bar Chart

SELECT 
    CASE 
        WHEN SENTIMENTO_POLARITY > 0.1 THEN 'Positivo'
        WHEN SENTIMENTO_POLARITY < -0.1 THEN 'Negativo'
        ELSE 'Neutro'
    END AS CATEGORIA_SENTIMENTO,
    COUNT(*) AS TOTAL_NOTICIAS,
    ROUND(AVG(SENTIMENTO_POLARITY), 4) AS SENTIMENTO_MEDIO,
    ROUND(AVG(RELEVANCIA), 4) AS RELEVANCIA_MEDIA
FROM BBAS3.PUBLIC.NOTICIAS_BBAS3
GROUP BY CATEGORIA_SENTIMENTO
ORDER BY TOTAL_NOTICIAS DESC;

-- ============================================================
-- 3. VOLUME DE NOTÍCIAS POR MÊS
-- ============================================================
-- Tipo de gráfico: Bar Chart

SELECT 
    TO_DATE(ANO_PUBLICACAO || '-' || LPAD(MES_PUBLICACAO::VARCHAR, 2, '0') || '-01') AS MES,
    COUNT(*) AS TOTAL_NOTICIAS,
    AVG(SENTIMENTO_POLARITY) AS SENTIMENTO_MEDIO
FROM BBAS3.PUBLIC.NOTICIAS_BBAS3
WHERE ANO_PUBLICACAO >= YEAR(DATEADD(month, -12, CURRENT_DATE()))
GROUP BY ANO_PUBLICACAO, MES_PUBLICACAO
ORDER BY ANO_PUBLICACAO, MES_PUBLICACAO;

-- ============================================================
-- 4. MÉTRICAS PRINCIPAIS (KPIs)
-- ============================================================
-- Tipo: Scorecard (usar 4 tiles separados)

-- KPI 1: Correlação Pearson
WITH dados_correlacao AS (
    SELECT 
        p.PRECO_FECHAMENTO,
        COALESCE(n.sentimento_medio, 0) AS sentimento
    FROM BBAS3.PUBLIC.FATO_ACOES_REAL p
    LEFT JOIN (
        SELECT 
            DATE_TRUNC('WEEK', DATEADD(DAY, 1, 
                DATEADD(MONTH, MES_PUBLICACAO - 1, 
                    DATEADD(YEAR, ANO_PUBLICACAO - 1970, '1970-01-01'::DATE)
                )
            )) AS semana,
            AVG(SENTIMENTO_POLARITY) AS sentimento_medio
        FROM BBAS3.PUBLIC.NOTICIAS_BBAS3
        GROUP BY semana
    ) n ON DATE_TRUNC('WEEK', p.DATA_NEGOCIACAO) = n.semana
    WHERE p.DATA_NEGOCIACAO >= DATEADD(month, -12, CURRENT_DATE())
)
SELECT 
    ROUND(CORR(PRECO_FECHAMENTO, sentimento), 4) AS CORRELACAO_PEARSON
FROM dados_correlacao;

-- KPI 2: Total de Notícias (12 meses)
SELECT 
    COUNT(*) AS TOTAL_NOTICIAS_12M
FROM BBAS3.PUBLIC.NOTICIAS_BBAS3
WHERE TO_DATE(ANO_PUBLICACAO || '-' || LPAD(MES_PUBLICACAO::VARCHAR, 2, '0') || '-01') 
    >= DATEADD(month, -12, CURRENT_DATE());

-- KPI 3: Sentimento Médio Geral
SELECT 
    ROUND(AVG(SENTIMENTO_POLARITY), 4) AS SENTIMENTO_MEDIO_GERAL
FROM BBAS3.PUBLIC.NOTICIAS_BBAS3;

-- KPI 4: Variação de Preço (12 meses)
WITH precos AS (
    SELECT 
        PRECO_FECHAMENTO,
        ROW_NUMBER() OVER (ORDER BY DATA_NEGOCIACAO) AS rn,
        COUNT(*) OVER () AS total
    FROM BBAS3.PUBLIC.FATO_ACOES_REAL
    WHERE DATA_NEGOCIACAO >= DATEADD(month, -12, CURRENT_DATE())
)
SELECT 
    ROUND(
        ((MAX(CASE WHEN rn = total THEN PRECO_FECHAMENTO END) / 
          MAX(CASE WHEN rn = 1 THEN PRECO_FECHAMENTO END)) - 1) * 100, 
        2
    ) AS VARIACAO_PERCENTUAL_12M
FROM precos;

-- ============================================================
-- 5. TOP 10 SEMANAS COM MAIOR VOLUME DE NOTÍCIAS
-- ============================================================
-- Tipo de gráfico: Bar Chart

SELECT 
    DATE_TRUNC('WEEK', DATEADD(DAY, 1, 
        DATEADD(MONTH, MES_PUBLICACAO - 1, 
            DATEADD(YEAR, ANO_PUBLICACAO - 1970, '1970-01-01'::DATE)
        )
    )) AS SEMANA,
    COUNT(*) AS VOLUME_NOTICIAS,
    AVG(SENTIMENTO_POLARITY) AS SENTIMENTO_MEDIO
FROM BBAS3.PUBLIC.NOTICIAS_BBAS3
GROUP BY SEMANA
ORDER BY VOLUME_NOTICIAS DESC
LIMIT 10;

-- ============================================================
-- 6. ANÁLISE POR FONTE DE NOTÍCIA
-- ============================================================
-- Tipo de gráfico: Horizontal Bar Chart

SELECT 
    FONTE_NOTICIA,
    COUNT(*) AS TOTAL_NOTICIAS,
    AVG(SENTIMENTO_POLARITY) AS SENTIMENTO_MEDIO,
    AVG(RELEVANCIA) AS RELEVANCIA_MEDIA
FROM BBAS3.PUBLIC.NOTICIAS_BBAS3
GROUP BY FONTE_NOTICIA
ORDER BY TOTAL_NOTICIAS DESC
LIMIT 10;
