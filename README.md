# Coletor de Notícias BBAS3 / Banco do Brasil

Este software coleta notícias relacionadas à ação **BBAS3** e ao **Banco do Brasil**, incluindo temas como resultados financeiros, inadimplência no agronegócio e sanções internacionais (OFAC / Magnitsky). O script utiliza RSS do **Google News**, extrai o texto completo das matérias, gera snippets, analisa sentimento e armazena os dados no **MongoDB** e em JSON local.

---

## Funcionalidades

- Busca por múltiplas queries em **Google News RSS**.
- Respeita **robots.txt** (não contorna restrições de scraping).
- Extrai texto principal da notícia usando:
  - [newspaper3k](https://pypi.org/project/newspaper3k/)
  - [readability-lxml](https://pypi.org/project/readability-lxml/)
  - fallback com BeautifulSoup.
- Detecta **paywalls** e evita inserir conteúdo bloqueado.
- Gera **snippets literais** de até 25 palavras do texto.
- Analisa **sentimento** usando TextBlob + palavras-chave financeiras contextualizadas:
  - Detecção de palavras-chave positivas/negativas em português
  - Análise de polaridade ajustada para contexto financeiro brasileiro
  - Métricas de confiança e subjetividade
  - Categorização: positivo, negativo, neutro
- Armazena os dados em:
  - MongoDB (evita duplicatas pelo URL)
  - Arquivo JSON local (`collected_articles_bbas3.json`)

---

## Requisitos

- Python 3.11+
- MongoDB local ou remoto
- Bibliotecas Python:

```bash
pip install requests feedparser newspaper3k readability-lxml beautifulsoup4 textblob pymongo tqdm python-dateutil
```

> **Nota:** Se estiver usando `newspaper3k` no Windows, pode ser necessário instalar `nltk` corpora:

```python
import nltk
nltk.download('punkt')
```

---

## Configuração

1. **MongoDB**  
   Defina a URI do MongoDB se diferente do padrão (`mongodb://localhost:27017/`):

No Linux/macOS:

```bash
export MONGO_URI="mongodb://usuario:senha@host:porta/"
export MONGO_DB="projeto_bigdata"
export MONGO_COLLECTION="projeto-ativos"
```

No Windows PowerShell:

```powershell
$env:MONGO_URI="mongodb://localhost:27017/"
$env:MONGO_DB="projeto_bigdata"
$env:MONGO_COLLECTION="projeto-ativos"
```

## Quick setup (Windows PowerShell)

### Setup Inicial (primeira vez)

```powershell
# 1. Criar ambiente virtual e instalar dependências
.\setup_env.ps1

# 2. (Opcional) Testar conexão com MongoDB
python testConnection.py
```

### Execução Automática (recomendado)

**Pipeline Completo** - Coleta + Análises (15-30 min):

```powershell
.\pipeline_completo.ps1
```

Este script executa automaticamente:

1. ✅ Testa conexão com MongoDB
2. 📰 Coleta notícias de todas as queries
3. 🗄️ Verifica inserção no MongoDB
4. 📊 Executa análise estatística básica
5. 📈 Executa análise detalhada por tema

**Análise Rápida** - Apenas análises dos dados existentes (1-2 min):

```powershell
.\analise_rapida.ps1
```

Use quando já tiver dados coletados e quiser apenas reprocessar as análises.

### Execução Manual (avançado)

```powershell
# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Coletar notícias
python collect_news_bbas3.py

# Verificar MongoDB
python verify_mongo_data.py

# Análises
python sentimentos.py
python analise_detalhada.py
```

2. **Queries**  
   As queries padrão estão definidas no script, podendo ser ajustadas conforme necessidade:

```python
QUERIES = [
    "BBAS3 Banco do Brasil resultados 2025",
    "Banco do Brasil agribusiness inadimplencia 2025",
    "OFAC sanctions Brazil Banco do Brasil",
    "Magnitsky act Brazil Banco do Brasil",
    ...
]
```

---

## Uso

No terminal, dentro do ambiente virtual Python:

```bash
python collect_news_bbas3.py
```

O script:

1. Busca RSS das queries.
2. Para cada notícia:
   - Verifica robots.txt
   - Baixa HTML
   - Extrai texto e snippet
   - Analisa sentimento
   - Salva em JSON e MongoDB

---

## Estrutura do JSON gerado

Exemplo de item:

```json
{
  "query": "BBAS3 Banco do Brasil resultados 2025",
  "rss_title": "BBAS3 já sobe 20% desde mínima do ano endossada por medidas do governo",
  "rss_published": "Thu, 11 Sep 2025 14:21:48 GMT",
  "fetched": "2025-09-13T19:49:08.738828+00:00",
  "url": "https://news.google.com/rss/articles/...",
  "titulo_noticia": "BBAS3 já sobe 20% desde mínima do ano endossada por medidas do governo",
  "publicada": "2025-09-11T14:21:48+00:00",
  "busca_feita": "2025-11-20T02:15:08.738828+00:00",
  "resumo": "BBAS3 já sobe 20% desde mínima do ano endossada por medidas do governo...",
  "sentimentos": {
    "polarity": 0.15,
    "subjectivity": 0.32,
    "label": "positive",
    "confidence": 0.42,
    "positive_keywords": 2,
    "negative_keywords": 0
  }
}
```

---

## Observações

- O snippet é limitado a 25 palavras do **texto real**, não do título.
- A data `busca_feita` indica o momento do download.
- A data `publicada` é extraída do RSS feed.
- **Análise de Sentimentos**:
  - `polarity`: -1.0 (muito negativo) a +1.0 (muito positivo)
  - `subjectivity`: 0.0 (objetivo) a 1.0 (subjetivo)
  - `label`: positive/negative/neutral (baseado em threshold de ±0.05)
  - `confidence`: nível de confiança da análise (0.0 a 1.0)
  - `positive_keywords` e `negative_keywords`: contagem de palavras-chave financeiras detectadas
- O script respeita **robots.txt**.

---

## Scripts de Análise

### `sentimentos.py` - Análise estatística básica

```powershell
python sentimentos.py
```

Fornece:

- Distribuição de sentimentos (positivo/negativo/neutro)
- Métricas de polaridade (média, mediana, desvio padrão)
- Sentimento médio por query
- Top artigos mais positivos e negativos
- Distribuição temporal

### `analise_detalhada.py` - Análise avançada

```powershell
python analise_detalhada.py
```

Fornece:

- Análise de palavras-chave detectadas
- Top 10 artigos mais polarizados
- Análise temporal ano a ano
- Categorização por tema (Resultados, Inadimplência, Sanções, etc.)
- Artigos com alta confiança de análise

### `verify_mongo_data.py` - Verificação do MongoDB

```powershell
python verify_mongo_data.py
```

Verifica:

- Conexão com MongoDB
- Contagem de documentos
- Exemplos de dados inseridos
- Distribuição de sentimentos no banco

---

## Melhorias Implementadas

### Análise de Sentimentos Aprimorada

- ✅ Análise contextualizada para notícias financeiras brasileiras
- ✅ Detecção de 18 palavras-chave positivas (lucro, crescimento, alta, etc.)
- ✅ Detecção de 18 palavras-chave negativas (prejuízo, queda, inadimplência, etc.)
- ✅ Ajuste de polaridade baseado em keywords + TextBlob
- ✅ Métricas de confiança da análise
- ✅ Threshold ajustado (±0.05) para melhor classificação

### Scripts de Análise

- ✅ `sentimentos.py`: Estatísticas gerais e métricas de polaridade
- ✅ `analise_detalhada.py`: Análise por tema, temporal e alta confiança
- ✅ `verify_mongo_data.py`: Verificação de dados no MongoDB

---

## Melhorias Futuras

- Adicionar detecção automática de **idioma**.
- Integração com **pipeline de análise financeira**.
- Extração de **valores numéricos** (lucro, dividendos, ROE) diretamente do texto.
- Paralelização para acelerar o download de múltiplos URLs.
- Visualizações gráficas (matplotlib/plotly) dos sentimentos ao longo do tempo.

---

## Autor

Murillo Weiss Kist  
Projeto Big Data - 2025
