# 📰 BBAS3 News Collector & Sentiment Analysis

Sistema de coleta e análise de sentimento de notícias sobre BBAS3 (Banco do Brasil) com armazenamento multi-database.

## 🏗️ Arquitetura

Projeto organizado seguindo princípios **SOLID** e **Clean Code**:

```
buscaDeDados/
├── src/                          # Código fonte principal
│   ├── config.py                 # Configurações via .env
│   ├── models.py                 # Modelos de dados
│   ├── repositories.py           # Acesso a dados (MongoDB, PostgreSQL, Snowflake)
│   └── services.py               # Lógica de negócio
│
├── scripts/                      # Scripts PowerShell
│   ├── pipeline_completo.ps1
│   ├── pipeline_data_warehouse.ps1
│   └── setup_env.ps1
│
├── data/                         # Dados coletados
│   └── collected_articles_bbas3.json
│
├── docs/                         # Documentação
│   ├── ARQUITETURA.md           # Detalhes da arquitetura
│   ├── ARQUITETURA_DW.md        # Data Warehouse
│   └── CHANGELOG.md             # Histórico de mudanças
│
├── tests/                        # Testes (futuros)
│
├── .env                          # Configurações (não versionado)
├── .env.example                  # Template de configuração
│
├── collect_news_bbas3.py        # Script principal de coleta
├── sentimentos.py               # Análise estatística
├── analise_detalhada.py         # Análise detalhada
│
└── requirements.txt             # Dependências Python
```

## 🚀 Quick Start

### 1️⃣ Instalação

```powershell
# Criar ambiente virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt
```

### 2️⃣ Configuração

```powershell
# Copiar template de configuração
cp .env.example .env

# Editar com suas credenciais
notepad .env
```

### 3️⃣ Executar Pipeline Completo (RECOMENDADO)

```powershell
# Executa TODO o processo automaticamente:
# ✅ Coleta dados históricos BBAS3
# ✅ Coleta notícias
# ✅ Análise de sentimentos
# ✅ Estruturação e limpeza
# ✅ Migração multi-database
# ✅ Transformação DW

.\scripts\pipeline_master.ps1
```

**Tempo:** 20-40 minutos | **Saída:** Dados em MongoDB, PostgreSQL, Snowflake

📖 **Guia completo:** [docs/GUIA_EXECUCAO.md](docs/GUIA_EXECUCAO.md)

---

### 🔧 Execuções Parciais (Opcional)

#### Apenas Coletar Notícias:

```powershell
python collect_news_bbas3.py
```

#### Apenas Análises:

```powershell
python scripts\sentimentos.py          # Análise básica
python scripts\analise_detalhada.py    # Análise detalhada
```

## 🔧 Configuração (.env)

```bash
# MongoDB
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=bigData
MONGO_COLLECTION=projeto_ativos
MONGO_ENABLED=true

# PostgreSQL
PG_USER=postgres
PG_PASSWORD=sua_senha
PG_HOST=localhost
PG_PORT=5432
PG_DB=bigdata
PG_TABLE=noticias_bbas3
PG_ENABLED=true

# Snowflake
SF_USER=seu_usuario
SF_PASSWORD=sua_senha
SF_ACCOUNT=sua_conta
SF_ENABLED=true

# Aplicação
MAX_PER_QUERY=100
SAVE_JSON_LOCAL=true
```

## 📊 Funcionalidades

### Coleta de Notícias

- ✅ Google News RSS
- ✅ 16 queries configuradas (2020-2025)
- ✅ Rate limiting
- ✅ Deduplicação por URL

### Análise de Sentimento

- ✅ TextBlob + Keywords (português)
- ✅ 18 palavras-chave positivas
- ✅ 18 palavras-chave negativas
- ✅ Polaridade, subjetividade, confiança

### Armazenamento Multi-Database

- ✅ **MongoDB**: Estrutura nested
- ✅ **PostgreSQL**: 25+ colunas flat
- ✅ **Snowflake**: Data warehouse
- ✅ **JSON**: Backup local

### Feature Engineering

- `url_hash`: Deduplicação
- `pub_year/month/day`: Análise temporal
- `sentiment_score`: Polarity + keywords
- `relevance`: Score calculado
- `query_category`: Classificação automática

## 📈 Análises SQL

```sql
-- Sentimento médio por ano
SELECT pub_year, AVG(polarity), COUNT(*)
FROM noticias_bbas3
GROUP BY pub_year;

-- Top artigos relevantes
SELECT titulo_noticia, relevance, sentiment_score
FROM noticias_bbas3
ORDER BY relevance DESC
LIMIT 10;

-- Distribuição de sentimentos
SELECT sentiment_label, COUNT(*)
FROM noticias_bbas3
GROUP BY sentiment_label;
```

## 🧪 Testes

```powershell
# Testar conexões
python testConnection.py

# Verificar dados MongoDB
python verify_mongo_data.py
```

## 📚 Documentação

- **[docs/ARQUITETURA.md](docs/ARQUITETURA.md)** - Arquitetura SOLID detalhada
- **[docs/ARQUITETURA_DW.md](docs/ARQUITETURA_DW.md)** - Data Warehouse
- **[docs/CHANGELOG.md](docs/CHANGELOG.md)** - Histórico de mudanças

## 🛠️ Scripts Úteis

```powershell
# Pipeline completo
.\scripts\pipeline_completo.ps1

# Data Warehouse
.\scripts\pipeline_data_warehouse.ps1

# Setup inicial
.\scripts\setup_env.ps1
```

## 🔒 Segurança

- ✅ Credenciais em `.env` (não versionado)
- ✅ `.env.example` como template
- ✅ `.gitignore` configurado

## 📦 Dependências Principais

- `feedparser` - RSS parsing
- `textblob` - Análise de sentimento
- `pymongo` - MongoDB
- `sqlalchemy` - PostgreSQL
- `snowflake-connector-python` - Snowflake
- `python-dotenv` - Variáveis de ambiente

## 🎯 Próximos Passos

- [ ] Testes unitários
- [ ] CI/CD pipeline
- [ ] Docker containerization
- [ ] API REST
- [ ] Dashboard de visualização

## 📝 Licença

Projeto acadêmico - 6º Período - Big Data

## 👥 Autor

ZzPowerTech

---

**Versão**: 2.0.0  
**Arquitetura**: SOLID/Clean Code  
**Python**: 3.11+
