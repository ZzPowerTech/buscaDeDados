# 🚀 Guia Rápido de Execução - Pipeline Master

## 📋 O que o Pipeline Faz?

O **pipeline_master.ps1** executa **TODOS** os processos automaticamente na ordem correta:

```
1️⃣  Coleta dados históricos BBAS3 (Yahoo Finance)
    ↓
2️⃣  Coleta notícias não estruturadas (Google News)
    ↓
3️⃣  Análise de sentimentos automática
    ↓
4️⃣  Limpeza e estruturação de dados
    ↓
5️⃣  Migração MongoDB → PostgreSQL → Snowflake
    ↓
6️⃣  Transformação para modelo dimensional (DW)
    ↓
7️⃣  Validações e relatórios
```

## ⚡ Execução Rápida

### 1️⃣ **Pré-requisitos** (fazer uma única vez)

```powershell
# Instalar dependências
pip install -r requirements.txt

# Configurar .env
# Copie .env.example para .env e preencha as credenciais
```

### 2️⃣ **Executar Pipeline Completo**

```powershell
# Execute este comando:
.\scripts\pipeline_master.ps1
```

**Tempo estimado:** 20-40 minutos (dependendo da conexão)

---

## 📊 O que Acontece em Cada Etapa

### **FASE 1: Dados Históricos** (2-5 min)

- 📊 Busca cotações BBAS3 desde 2020
- 💾 Salva em PostgreSQL → `bbas3_cotacoes`
- ❄️ Salva em Snowflake → `BBAS3_COTACOES`
- 📈 Inclui: Open, High, Low, Close, Volume, Variação%

### **FASE 2: Coleta de Notícias** (15-25 min)

- 📰 Busca 16 queries no Google News RSS
- 🔍 Queries incluem: resultados financeiros, agronegócio, sanções, etc.
- 💾 Salva em 4 lugares:
  - `data/collected_articles_bbas3.json` (local)
  - MongoDB → `bigData.projeto_ativos` (nested)
  - PostgreSQL → `bigdata.noticias_bbas3` (flat, 20 colunas)
  - Snowflake → `BBAS3.PUBLIC.DADOS_MONG` (flat)

### **FASE 3: Análise de Sentimentos** (1-3 min)

- 🧠 Análise automática de polaridade (-1.0 a +1.0)
- 🏷️ Classificação: positive/negative/neutral
- 📊 Contagem de palavras-chave positivas/negativas
- 🎯 Cálculo de confiança e relevância
- 📝 Geração de relatórios estatísticos

### **FASE 4: Transformação DW** (1-2 min)

- 🔄 Cria modelo dimensional no Snowflake:
  - `FATO_NOTICIAS` (fato principal)
  - `DIM_SENTIMENTO` (dimensão sentimento)
  - `DIM_FONTE` (dimensão fonte da notícia)
- 🧹 Limpeza de URLs e dados
- 📅 Normalização de datas

### **FASE 5: Validações** (< 1 min)

- ✅ Verifica dados no MongoDB
- ✅ Testa conexões
- ✅ Valida estrutura de dados
- ✅ Gera relatórios de execução

---

## 🎯 Execuções Parciais (se necessário)

### Apenas Coletar Dados Históricos:

```powershell
python scripts\buscar_dados_reais.py
```

### Apenas Coletar Notícias:

```powershell
python collect_news_bbas3.py
```

### Apenas Análises de Sentimento:

```powershell
# Análise básica
python scripts\sentimentos.py

# Análise detalhada
python scripts\analise_detalhada.py
```

### Apenas Transformação DW:

```powershell
python scripts\transformar_noticias.py
python scripts\transformar_dados_api.py
```

---

## 💾 Onde Encontrar os Dados Depois

### 📁 **Local (JSON)**

```
data/collected_articles_bbas3.json
```

### 🍃 **MongoDB** (melhor para análises nested/agregadas)

```javascript
use bigData
db.projeto_ativos.find()
```

### 🐘 **PostgreSQL** (melhor para queries relacionais)

```sql
-- Notícias
SELECT * FROM bigdata.noticias_bbas3;

-- Cotações
SELECT * FROM bigdata.bbas3_cotacoes;
```

### ❄️ **Snowflake** (melhor para analytics/DW)

```sql
-- Dados operacionais
SELECT * FROM BBAS3.PUBLIC.DADOS_MONG;
SELECT * FROM BBAS3.PUBLIC.BBAS3_COTACOES;

-- Data Warehouse (modelo dimensional)
SELECT * FROM BBAS3.PUBLIC.FATO_NOTICIAS;
SELECT * FROM BBAS3.PUBLIC.DIM_SENTIMENTO;
SELECT * FROM BBAS3.PUBLIC.DIM_FONTE;
```

---

## 🔧 Solução de Problemas

### ❌ "Ambiente virtual não encontrado"

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### ❌ "MongoDB não está acessível"

```powershell
# Inicie o MongoDB
net start MongoDB

# Ou no Linux/Mac
sudo systemctl start mongod
```

### ❌ "Erro ao coletar notícias"

- Verifique conexão com internet
- Verifique credenciais em `.env`
- Algumas queries podem retornar 0 resultados (normal)

### ❌ "Erro Snowflake/PostgreSQL"

- Verifique credenciais em `.env`
- Teste conexão manual
- Verifique firewall/rede

---

## 📊 Estrutura de Dados Gerada

### **Notícias (20 campos):**

```
url_hash, query_category, titulo_noticia, titulo_limpo,
url, fonte, publicada, busca_feita,
sentimento_polarity, sentimento_label, sentimento_subjectivity,
sentimento_confidence, sentimento_positive_keywords,
sentimento_negative_keywords, sentimento_score,
ano_publicacao, mes_publicacao, dia_publicacao,
relevancia, palavras_chave
```

### **Cotações BBAS3:**

```
Date, Open, High, Low, Close, Volume,
Dividends, Stock_Splits, Variacao_Percentual
```

---

## 🎓 Exemplos de Análises SQL

### **Top 10 Notícias Mais Positivas:**

```sql
SELECT
    titulo_limpo,
    sentimento_polarity,
    sentimento_confidence,
    publicada
FROM BBAS3.PUBLIC.FATO_NOTICIAS
WHERE SENTIMENTO = 'Positivo'
ORDER BY POLARIDADE DESC
LIMIT 10;
```

### **Sentimento por Mês:**

```sql
SELECT
    DATE_TRUNC('month', DATA_PUBLICACAO) as MES,
    COUNT(*) as TOTAL_NOTICIAS,
    AVG(POLARIDADE) as SENTIMENTO_MEDIO,
    SUM(CASE WHEN SENTIMENTO = 'Positivo' THEN 1 ELSE 0 END) as POSITIVAS,
    SUM(CASE WHEN SENTIMENTO = 'Negativo' THEN 1 ELSE 0 END) as NEGATIVAS
FROM BBAS3.PUBLIC.FATO_NOTICIAS
GROUP BY 1
ORDER BY 1 DESC;
```

### **Correlação Sentimento x Cotação:**

```sql
SELECT
    c.Date,
    c.Close,
    c.Variacao_Percentual,
    AVG(n.POLARIDADE) as SENTIMENTO_MEDIO_DIA
FROM BBAS3.PUBLIC.BBAS3_COTACOES c
LEFT JOIN BBAS3.PUBLIC.FATO_NOTICIAS n
    ON DATE(c.Date) = DATE(n.DATA_PUBLICACAO)
GROUP BY c.Date, c.Close, c.Variacao_Percentual
ORDER BY c.Date DESC;
```

---

## 📞 Suporte

**Documentação completa:** `docs/`
**Arquitetura:** `docs/ARQUITETURA.md`
**Estrutura:** `docs/ESTRUTURA_FINAL.md`
**Testes:** `python tests/test_system.py`

---

**Criado por:** Sistema de Análise BBAS3  
**Última atualização:** 2025-01-15
