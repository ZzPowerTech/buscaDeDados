# 🏢 Arquitetura do Data Warehouse BBAS3

## 📊 Visão Geral

Este projeto implementa um **Data Warehouse completo** para análise de ações BBAS3 (Banco do Brasil), integrando:

- 📰 **Notícias** com análise de sentimento (Google News)
- 📈 **Cotações históricas** (Yahoo Finance API)
- 🗄️ **Armazenamento**: MongoDB → PostgreSQL → Snowflake
- 📊 **Modelo Dimensional** (Star Schema)

---

## 🏗️ Arquitetura de Dados

```
┌─────────────────┐
│  Google News    │ ───┐
│  RSS Feed       │    │
└─────────────────┘    │
                       ├──→ ┌──────────┐      ┌──────────────┐
┌─────────────────┐    │    │ MongoDB  │ ───→ │ PostgreSQL   │
│  Yahoo Finance  │ ───┘    │ (NoSQL)  │      │ (Relacional) │
│  API            │         └──────────┘      └──────────────┘
└─────────────────┘                                   │
                                                      │
                                                      ▼
                                            ┌──────────────────┐
                                            │   SNOWFLAKE      │
                                            │  Data Warehouse  │
                                            │                  │
                                            │  • FATO_ACOES    │
                                            │  • FATO_NOTICIAS │
                                            │  • DIM_TEMPO     │
                                            │  • DIM_SENTIMENTO│
                                            └──────────────────┘
                                                      │
                                                      ▼
                                            ┌──────────────────┐
                                            │  Power BI /      │
                                            │  Dashboards      │
                                            └──────────────────┘
```

---

## 📁 Arquivos do Projeto

### 🔧 Setup e Configuração

- `setup_env.ps1` - Cria ambiente virtual e instala dependências
- `requirements.txt` - Lista de bibliotecas Python necessárias

### 📊 Coleta de Dados

- `collect_news_bbas3.py` - Coleta notícias do Google News RSS
- `buscar_dados_reais.py` - Busca cotações da Yahoo Finance API

### 🔄 Migração e Transformação

- `migrar.py` - Migra dados do PostgreSQL para Snowflake
- `transformar_dados_api.py` - Cria modelo dimensional para cotações
- `transformar_noticias.py` - Cria modelo dimensional para notícias

### 📈 Análises

- `sentimentos.py` - Análise estatística de sentimentos
- `analise_detalhada.py` - Análise detalhada por tema e período
- `verify_mongo_data.py` - Verifica dados no MongoDB
- `analisar_dados_mong.py` - Análise exploratória Snowflake
- `verificar_estrutura_api.py` - Verifica estrutura Snowflake

### 🚀 Automação (Pipelines)

- `pipeline_completo.ps1` - Pipeline MongoDB + Análises
- `pipeline_data_warehouse.ps1` - **Pipeline completo DW** ⭐
- `analise_rapida.ps1` - Apenas análises (sem coleta)

---

## 🗄️ Modelo de Dados (Star Schema)

### Tabelas Fato

#### FATO_ACOES_REAL

```sql
- DATA_NEGOCIACAO (PK)
- PRECO_ABERTURA
- PRECO_MAXIMO
- PRECO_MINIMO
- PRECO_FECHAMENTO
- VOLUME
- VARIACAO_PERCENTUAL
```

#### FATO_NOTICIAS

```sql
- ID_NOTICIA (PK)
- DATA_BUSCA
- DATA_PUBLICACAO
- QUERY_BUSCA
- TITULO
- URL_COMPLETA
- SENTIMENTO (FK → DIM_SENTIMENTO)
- POLARIDADE
- SUBJETIVIDADE
- FONTE_NOTICIA
```

### Tabelas Dimensão

#### DIM_TEMPO_REAL

```sql
- DATA (PK)
- ANO
- TRIMESTRE
- MES
- NOME_MES
- DIA
- DIA_SEMANA
- SEMANA_ANO
```

#### DIM_SENTIMENTO

```sql
- SENTIMENTO (PK)
- SENTIMENTO_PT
- SENTIMENTO_VALOR (-1, 0, 1)
```

### Views Analíticas

| View                           | Descrição                          |
| ------------------------------ | ---------------------------------- |
| `VW_RESUMO_MENSAL_REAL`        | Performance mensal agregada        |
| `VW_ANALISE_ANUAL_REAL`        | Análise anual com volatilidade     |
| `VW_INDICADORES_TECNICOS`      | Médias móveis (7d, 20d, 50d, 200d) |
| `VW_PERFORMANCE_TRIMESTRAL`    | Performance por trimestre          |
| `VW_SENTIMENTO_POR_PERIODO`    | Sentimento agregado por dia        |
| `VW_NOTICIAS_POR_FONTE`        | Distribuição por fonte             |
| `VW_CORRELACAO_NOTICIAS_PRECO` | Correlação sentimento x preço      |

---

## 🚀 Como Usar

### 1️⃣ Setup Inicial (primeira vez)

```powershell
# Instalar dependências
.\setup_env.ps1
```

### 2️⃣ Executar Pipeline Completo

```powershell
# Pipeline completo do Data Warehouse
.\pipeline_data_warehouse.ps1
```

Este pipeline executa:

1. ✅ Coleta notícias do Google News (MongoDB)
2. ✅ Busca cotações da Yahoo Finance API (PostgreSQL + Snowflake)
3. ✅ Migra dados para Snowflake
4. ✅ Transforma em modelo dimensional (Star Schema)
5. ✅ Executa análises de sentimento

**Tempo estimado**: 20-40 minutos

### 3️⃣ Consultas no Snowflake

```sql
-- Análise anual de performance
SELECT * FROM VW_ANALISE_ANUAL_REAL ORDER BY ANO;

-- Correlação entre sentimento e preço
SELECT * FROM VW_CORRELACAO_NOTICIAS_PRECO
WHERE DATA >= '2024-01-01'
ORDER BY DATA DESC;

-- Indicadores técnicos
SELECT
    DATA_NEGOCIACAO,
    PRECO_FECHAMENTO,
    MEDIA_MOVEL_20D,
    MEDIA_MOVEL_200D,
    VOLATILIDADE_30D
FROM VW_INDICADORES_TECNICOS
ORDER BY DATA_NEGOCIACAO DESC
LIMIT 30;

-- Sentimento por fonte de notícia
SELECT * FROM VW_NOTICIAS_POR_FONTE
ORDER BY TOTAL_NOTICIAS DESC;
```

---

## 📊 Análises Disponíveis

### Análise de Sentimento

- Distribuição: positivo/negativo/neutro
- Polaridade média por período
- Correlação com variação de preço
- Análise por fonte de notícia

### Análise de Cotações

- Preços: abertura, máximo, mínimo, fechamento
- Volume negociado
- Variação percentual diária
- Médias móveis (7, 20, 50, 200 dias)
- Volatilidade histórica
- Performance mensal/trimestral/anual

### Análise Combinada

- Impacto de notícias no preço
- Sentimento vs variação de preço
- Tendências temporais

---

## 🔧 Configurações

### MongoDB

```powershell
$env:MONGO_URI="mongodb://localhost:27017/"
$env:MONGO_DB="bigData"
$env:MONGO_COLLECTION="projeto_ativos"
```

### PostgreSQL

Editar em cada arquivo Python:

```python
pg_user = "postgres"
pg_password = "sua_senha"
pg_host = "localhost"
pg_port = "5432"
pg_db = "bigdata"
```

### Snowflake

Editar em cada arquivo Python:

```python
sf_user = "SEU_USUARIO"
sf_password = "SUA_SENHA"
sf_account = "SUA_CONTA"
sf_warehouse = "COMPUTE_WH"
sf_database = "BBAS3"
sf_schema = "PUBLIC"
```

---

## 📈 Queries Analíticas Recomendadas

### 1. Média móvel e sinais de compra/venda

```sql
SELECT
    DATA_NEGOCIACAO,
    PRECO_FECHAMENTO,
    MEDIA_MOVEL_20D,
    MEDIA_MOVEL_200D,
    CASE
        WHEN MEDIA_MOVEL_20D > MEDIA_MOVEL_200D THEN 'COMPRA'
        WHEN MEDIA_MOVEL_20D < MEDIA_MOVEL_200D THEN 'VENDA'
        ELSE 'NEUTRO'
    END as SINAL
FROM VW_INDICADORES_TECNICOS
ORDER BY DATA_NEGOCIACAO DESC;
```

### 2. Dias com maior correlação notícia-preço

```sql
SELECT
    DATA,
    TOTAL_NOTICIAS,
    POLARIDADE_MEDIA_DIA,
    VARIACAO_PERCENTUAL,
    PRECO_FECHAMENTO
FROM VW_CORRELACAO_NOTICIAS_PRECO
WHERE TOTAL_NOTICIAS > 5
ORDER BY ABS(VARIACAO_PERCENTUAL) DESC
LIMIT 20;
```

### 3. Performance em dias de notícias positivas vs negativas

```sql
SELECT
    CASE
        WHEN SCORE_SENTIMENTO > 0.1 THEN 'Positivo'
        WHEN SCORE_SENTIMENTO < -0.1 THEN 'Negativo'
        ELSE 'Neutro'
    END as TIPO_SENTIMENTO,
    COUNT(*) as DIAS,
    ROUND(AVG(VARIACAO_PERCENTUAL), 2) as VAR_MEDIA,
    ROUND(STDDEV(VARIACAO_PERCENTUAL), 2) as VOLATILIDADE
FROM VW_CORRELACAO_NOTICIAS_PRECO
WHERE SCORE_SENTIMENTO IS NOT NULL
GROUP BY TIPO_SENTIMENTO;
```

---

## 🎯 Casos de Uso

1. **Análise de Risco**: Volatilidade histórica e correlação com eventos
2. **Trading**: Médias móveis e indicadores técnicos
3. **Sentiment Analysis**: Impacto de notícias no preço
4. **Relatórios**: Performance mensal/trimestral/anual
5. **Dashboards**: Power BI conectado ao Snowflake

---

## 📚 Tecnologias Utilizadas

- **Python 3.11+**
- **MongoDB** (armazenamento NoSQL)
- **PostgreSQL** (banco relacional)
- **Snowflake** (data warehouse cloud)
- **Yahoo Finance API** (dados financeiros)
- **Google News RSS** (notícias)
- **TextBlob** (análise de sentimento)
- **Pandas** (manipulação de dados)
- **SQLAlchemy** (ORM)

---

## 📞 Suporte

Para dúvidas ou problemas:

1. Consulte o `GUIA_RAPIDO.md`
2. Verifique as configurações de conexão
3. Execute os scripts de verificação individuais
