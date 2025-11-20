# 🏗️ Arquitetura do Sistema BBAS3 News Collector

## 📐 Visão Geral da Arquitetura

Este projeto segue os princípios **SOLID** e **Clean Code**, organizando o código em camadas bem definidas:

```
src/
├── __init__.py           # Package initialization
├── config.py             # Configurações centralizadas (Settings, Config classes)
├── models.py             # Modelos de dados (NewsArticle, SentimentAnalysis)
├── repositories.py       # Camada de acesso a dados (MongoDB, PostgreSQL, Snowflake)
└── services.py           # Lógica de negócio (Collector, Sentiment, Persistence)
```

## 🎯 Princípios SOLID Aplicados

### 1. **Single Responsibility Principle (SRP)**

Cada classe tem uma única responsabilidade:

- `SentimentAnalysisService`: Análise de sentimento
- `NewsCollectorService`: Coleta de notícias do RSS
- `NewsPersistenceService`: Orquestração de salvamento
- `MongoDBRepository`: Acesso ao MongoDB
- `PostgreSQLRepository`: Acesso ao PostgreSQL
- `SnowflakeRepository`: Acesso ao Snowflake

### 2. **Open/Closed Principle (OCP)**

Aberto para extensão, fechado para modificação:

- Novos repositórios podem ser adicionados implementando `INewsRepository`
- Novos serviços podem ser criados sem modificar os existentes

### 3. **Liskov Substitution Principle (LSP)**

Todos os repositórios implementam `INewsRepository` e são intercambiáveis:

```python
def save_news(repo: INewsRepository, articles: List[NewsArticle]):
    repo.save(articles)  # Funciona com qualquer implementação
```

### 4. **Interface Segregation Principle (ISP)**

Interface `INewsRepository` contém apenas métodos essenciais:

- `save(articles)`: Salva artigos
- `find_by_url(url)`: Busca por URL
- `count()`: Conta registros

### 5. **Dependency Inversion Principle (DIP)**

Dependências são injetadas, não criadas internamente:

```python
collector = NewsCollectorService(
    sentiment_service=SentimentAnalysisService(),
    max_per_query=100
)
```

## 📊 Fluxo de Dados

```
Google News RSS
      ↓
NewsCollectorService → parse RSS feed
      ↓
SentimentAnalysisService → analisa sentimento
      ↓
NewsArticle model → transforma dados
      ↓
NewsPersistenceService → coordena salvamento
      ↓
┌─────────────┬──────────────┬──────────────┐
│  MongoDB    │  PostgreSQL  │  Snowflake   │
│ (to_dict)   │ (relational) │ (relational) │
└─────────────┴──────────────┴──────────────┘
```

## 🗂️ Estrutura de Dados

### NewsArticle (src/models.py)

Possui **duas transformações** para diferentes destinos:

#### 1. MongoDB (Nested Structure)

```python
article.to_dict()
{
    "url": "https://...",
    "query": "BBAS3",
    "titulo_noticia": "Banco do Brasil...",
    "publicada": "2025-01-15T10:00:00Z",
    "busca_feita": "2025-01-15T12:00:00Z",
    "resumo": "Resumo da notícia...",
    "sentimentos": {
        "polarity": 0.3,
        "subjectivity": 0.5,
        "label": "positive",
        "confidence": 0.7,
        "positive_keywords": 3,
        "negative_keywords": 0
    }
}
```

#### 2. PostgreSQL/Snowflake (Flat Structure)

```python
article.to_relational_dict()
{
    "url": "https://...",
    "url_hash": "a1b2c3...",
    "query": "BBAS3",
    "query_category": "results",
    "titulo_noticia": "Banco do Brasil...",
    "titulo_limpo": "banco do brasil...",
    "source": "google_news",
    "publicada": "2025-01-15T10:00:00Z",
    "busca_feita": "2025-01-15T12:00:00Z",
    "pub_year": 2025,
    "pub_month": 1,
    "pub_day": 15,
    "pub_hour": 10,
    "pub_weekday": 2,
    "resumo": "Resumo da notícia...",
    "resumo_limpo": "resumo da noticia...",
    "resumo_length": 150,
    "polarity": 0.3,
    "subjectivity": 0.5,
    "sentiment_label": "positive",
    "sentiment_confidence": 0.7,
    "positive_keywords": 3,
    "negative_keywords": 0,
    "sentiment_score": 0.35,
    "relevance": 0.8
}
```

## ⚙️ Configuração com .env

Todas as configurações são centralizadas no arquivo `.env`:

```bash
# Crie seu arquivo .env
cp .env.example .env

# Edite com suas credenciais
nano .env
```

### Estrutura de Configuração

```python
# src/config.py
settings.mongodb.uri          # MongoDB connection string
settings.mongodb.enabled      # Ativa/desativa MongoDB

settings.postgresql.host      # PostgreSQL host
settings.postgresql.enabled   # Ativa/desativa PostgreSQL

settings.snowflake.account    # Snowflake account
settings.snowflake.enabled    # Ativa/desativa Snowflake

settings.app.max_articles_per_query  # Limite por query
settings.app.sleep_between_requests  # Rate limiting
```

## 🔧 Como Usar

### 1. Instalação

```powershell
# Criar ambiente virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar .env

```bash
# Copiar template
cp .env.example .env

# Editar credenciais
# MongoDB, PostgreSQL, Snowflake
```

### 3. Executar Coleta

```powershell
# Coleta completa
python collect_news_bbas3.py
```

## 📦 Repositórios (Data Access Layer)

### Interface Base

```python
class INewsRepository(ABC):
    @abstractmethod
    def save(self, articles: List[NewsArticle]) -> int:
        """Salva artigos, retorna quantidade salva"""
        pass
```

### MongoDB Repository

- **Estrutura**: Nested (JSON completo)
- **Deduplicação**: Upsert por URL
- **Método**: `update_one(..., upsert=True)`

### PostgreSQL Repository

- **Estrutura**: Flat (25+ colunas)
- **Deduplicação**: Remove duplicatas por `url_hash`
- **Método**: DataFrame → `to_sql()`

### Snowflake Repository

- **Estrutura**: Flat (25+ colunas)
- **Deduplicação**: Auto-create table com hash
- **Método**: `write_pandas()`

## 🧪 Análise de Sentimento

### Algoritmo Híbrido

1. **TextBlob**: Polaridade base (-1 a +1)
2. **Keywords**: 18 positivas + 18 negativas (português)
3. **Ajuste**: `polarity + (pos_count - neg_count) * 0.15`
4. **Thresholds**: ±0.05 para neutral

### Keywords Financeiras

**Positivas**: lucro, crescimento, alta, valorização, recuperação, expansão, dividendos...

**Negativas**: prejuízo, queda, crise, inadimplência, calote, default, provisão...

### Output

```python
SentimentAnalysis(
    polarity=0.3,           # -1 (negativo) a +1 (positivo)
    subjectivity=0.5,       # 0 (objetivo) a 1 (subjetivo)
    label='positive',       # positive, negative, neutral
    confidence=0.7,         # 0 a 1
    positive_keywords=3,    # Contagem
    negative_keywords=0     # Contagem
)
```

## 🚀 Próximos Passos

- [ ] Refatorar `sentimentos.py` para usar nova arquitetura
- [ ] Refatorar `analise_detalhada.py`
- [ ] Atualizar pipelines PowerShell para usar .env
- [ ] Criar testes unitários
- [ ] Documentação de API
- [ ] Containerização (Docker)

## 📚 Referências

- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Clean Code](https://github.com/ryanmcdermott/clean-code-javascript)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
