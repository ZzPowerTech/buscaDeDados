# 📁 Estrutura do Projeto

```
buscaDeDados/
│
├── 📂 src/                                # Código fonte principal (SOLID)
│   ├── __init__.py                        # Package initialization
│   ├── config.py                          # Configurações via .env
│   ├── models.py                          # NewsArticle, SentimentAnalysis
│   ├── repositories.py                    # MongoDB, PostgreSQL, Snowflake
│   └── services.py                        # Business logic
│
├── 📂 scripts/                            # Scripts PowerShell
│   ├── pipeline_completo.ps1              # Pipeline completo de coleta
│   ├── pipeline_data_warehouse.ps1        # Pipeline DW
│   ├── analise_rapida.ps1                 # Análise rápida
│   ├── setup_env.ps1                      # Setup inicial
│   ├── run.ps1                            # Executor genérico
│   └── config_example.ps1                 # Exemplo de config
│
├── 📂 data/                               # Dados coletados
│   └── collected_articles_bbas3.json      # Notícias em JSON
│
├── 📂 docs/                               # Documentação
│   ├── ARQUITETURA.md                     # Arquitetura SOLID
│   ├── ARQUITETURA_DW.md                  # Data Warehouse
│   └── CHANGELOG.md                       # Histórico de mudanças
│
├── 📂 tests/                              # Testes (futuro)
│   └── (testes unitários)
│
├── 📄 .env                                # Configurações (NÃO versionado)
├── 📄 .env.example                        # Template de configuração
├── 📄 .gitignore                          # Arquivos ignorados pelo Git
│
├── 🐍 collect_news_bbas3.py              # ⭐ Script principal de coleta
├── 🐍 sentimentos.py                      # Análise estatística de sentimentos
├── 🐍 analise_detalhada.py               # Análise detalhada por tema/tempo
│
├── 🐍 transformar_noticias.py            # Transforma notícias para star schema
├── 🐍 transformar_dados_api.py           # Transforma dados API para DW
├── 🐍 migrar.py                          # Migração PostgreSQL → Snowflake
│
├── 🐍 buscar_dados_reais.py              # Coleta dados Yahoo Finance
├── 🐍 analisar_dados_mong.py             # Análise de dados MongoDB
├── 🐍 verificar_estrutura_api.py         # Verifica estrutura da API
│
├── 🐍 testConnection.py                  # Testa conexões de banco
├── 🐍 verify_mongo_data.py               # Verifica dados MongoDB
│
├── 📄 requirements.txt                    # Dependências Python
└── 📄 README.md                           # Documentação principal
```

## 📊 Fluxo de Dados

```
Google News RSS
      ↓
collect_news_bbas3.py (coleta + sentiment)
      ↓
┌─────────────┬──────────────┬──────────────┬──────────────┐
│  MongoDB    │  PostgreSQL  │  Snowflake   │  JSON Local  │
│  (nested)   │  (flat)      │  (flat)      │  (backup)    │
└─────────────┴──────────────┴──────────────┴──────────────┘
      ↓             ↓              ↓
 sentimentos.py    transformar_noticias.py
 (análise)         (star schema)
```

## 🎯 Arquivos Principais

### Coleta e Análise

- **collect_news_bbas3.py**: Coleta notícias + análise sentimento + salva em 4 destinos
- **sentimentos.py**: Estatísticas agregadas de sentimento
- **analise_detalhada.py**: Análise por tema e período temporal

### Data Warehouse

- **transformar_noticias.py**: Transforma para star schema (dim_tempo, dim_sentimento, fato_noticias)
- **transformar_dados_api.py**: Transforma dados API para star schema
- **migrar.py**: Migra PostgreSQL → Snowflake

### Utilitários

- **testConnection.py**: Testa conexões MongoDB/PostgreSQL/Snowflake
- **verify_mongo_data.py**: Verifica integridade dados MongoDB
- **buscar_dados_reais.py**: Coleta dados financeiros (Yahoo Finance)

### Scripts PowerShell

- **scripts/pipeline_completo.ps1**: Executa pipeline end-to-end
- **scripts/setup_env.ps1**: Setup inicial do ambiente

## 🔧 Configuração

Todas as configurações estão centralizadas em `.env`:

```bash
# Bancos de dados
MONGO_ENABLED=true
PG_ENABLED=true
SF_ENABLED=true

# Aplicação
MAX_PER_QUERY=100
SAVE_JSON_LOCAL=true
OUTPUT_JSON=data/collected_articles_bbas3.json
```

## 📦 Dependências

Ver `requirements.txt` para lista completa. Principais:

- `feedparser` - RSS parsing
- `textblob` - Análise sentimento
- `pymongo` - MongoDB
- `sqlalchemy` - PostgreSQL
- `snowflake-connector-python` - Snowflake
- `python-dotenv` - Variáveis ambiente
- `yfinance` - Dados financeiros
- `pandas` - Manipulação dados

## 🚀 Como Usar

1. **Setup**:

   ```powershell
   .\scripts\setup_env.ps1
   ```

2. **Configurar**:

   ```powershell
   cp .env.example .env
   notepad .env
   ```

3. **Coletar**:

   ```powershell
   python collect_news_bbas3.py
   ```

4. **Analisar**:

   ```powershell
   python sentimentos.py
   python analise_detalhada.py
   ```

5. **Pipeline Completo**:
   ```powershell
   .\scripts\pipeline_completo.ps1
   ```

## 📝 Notas

- Arquivos em `data/` não são versionados (ver `.gitignore`)
- `.env` contém credenciais e não deve ser commitado
- Documentação detalhada em `docs/`
- Testes futuros em `tests/`
