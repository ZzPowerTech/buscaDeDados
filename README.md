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
- Analisa **sentimento** do snippet (positivo, negativo, neutro) usando TextBlob.
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
  "article_extraction": {
      "title": "BBAS3 já sobe 20% desde mínima do ano endossada por medidas do governo",
      "pubdate": "2025-09-11T14:21:48+00:00",
      "text": "Texto completo da notícia...",
      "snippet": "BBAS3 já sobe 20% desde mínima do ano endossada por medidas do governo...",
      "sentiment": {
          "polarity": 0.0,
          "subjectivity": 0.0,
          "label": "neutral"
      },
      "paywalled": false,
      "allowed_by_robots": true
  }
}
```

---

## Observações

- O snippet é limitado a 25 palavras do **texto real**, não do título.
- A data `fetched` indica o momento do download.
- A data `pubdate` é extraída do RSS ou do HTML da notícia.
- O script respeita **robots.txt** e não contorna paywalls.

---

## Melhorias Futuras

- Adicionar detecção automática de **idioma**.
- Integração com **pipeline de análise financeira**.
- Extração de **valores numéricos** (lucro, dividendos, ROE) diretamente do texto.
- Parallelização para acelerar o download de múltiplos URLs.

---

## Autor

Murillo Weiss Kist  
Projeto Big Data - 2025