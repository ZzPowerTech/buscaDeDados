# 🚀 GUIA COMPLETO: Deploy do Projeto BBAS3 no Snowflake

## 📋 Sumário

1. [Pré-requisitos](#pré-requisitos)
2. [Parte 1: Criar Pipeline Automatizado](#parte-1-criar-pipeline-automatizado)
3. [Parte 2: Deploy do Streamlit App](#parte-2-deploy-do-streamlit-app)
4. [Parte 3: Monitoramento e Manutenção](#parte-3-monitoramento-e-manutenção)
5. [Troubleshooting](#troubleshooting)

---

## 📌 Pré-requisitos

✅ Conta Snowflake ativa (trial gratuito serve)  
✅ Dados já carregados nas tabelas:

- `BBAS3.PUBLIC.NOTICIAS_BBAS3`
- `BBAS3.PUBLIC.FATO_ACOES_REAL`
  ✅ Warehouse criado (ex: `COMPUTE_WH`)

---

## 🔧 Parte 1: Criar Pipeline Automatizado

### **Passo 1.1: Acessar Snowflake SQL Editor**

1. Faça login em: https://app.snowflake.com
2. No menu lateral, clique em **"Worksheets"**
3. Clique em **"+ Worksheet"** (novo worksheet)

---

### **Passo 1.2: Criar Stored Procedure para Coleta de Notícias**

Cole este código no worksheet e execute (**Ctrl + Enter** ou botão "Run"):

```sql
-- ============================================================
-- STORED PROCEDURE: Coleta de Notícias BBAS3
-- ============================================================

CREATE OR REPLACE PROCEDURE BBAS3.PUBLIC.SP_COLETAR_NOTICIAS_BBAS3()
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('snowflake-snowpark-python', 'requests', 'beautifulsoup4', 'textblob', 'gnews')
HANDLER = 'coletar_noticias'
AS
$$
import requests
from gnews import GNews
from textblob import TextBlob
from datetime import datetime

def coletar_noticias(session):
    try:
        # Configurar GNews
        google_news = GNews(
            language='pt',
            country='BR',
            period='1d',  # Últimas 24 horas
            max_results=50
        )

        # Buscar notícias
        noticias = google_news.get_news('BBAS3 Banco do Brasil ações')

        total_inseridas = 0

        for noticia in noticias:
            try:
                # Análise de sentimento
                titulo = noticia.get('title', '')
                descricao = noticia.get('description', '')
                texto_completo = f"{titulo}. {descricao}"

                blob = TextBlob(texto_completo)
                sentimento = blob.sentiment.polarity

                # Calcular relevância
                relevancia = (len(texto_completo) / 500) * (1 - blob.sentiment.subjectivity)
                relevancia = min(max(relevancia, 0), 1)

                # Data publicação
                data_pub = noticia.get('published date')
                if data_pub:
                    dt = datetime.strptime(data_pub, '%a, %d %b %Y %H:%M:%S %Z')
                else:
                    dt = datetime.now()

                # Preparar dados
                url = noticia.get('url', '')
                fonte = noticia.get('publisher', {}).get('title', 'Desconhecido')

                # INSERT no Snowflake
                query = f"""
                INSERT INTO BBAS3.PUBLIC.NOTICIAS_BBAS3 (
                    ANO_PUBLICACAO,
                    MES_PUBLICACAO,
                    SENTIMENTO_POLARITY,
                    RELEVANCIA,
                    FONTE_NOTICIA
                )
                VALUES (
                    {dt.year},
                    {dt.month},
                    {sentimento},
                    {relevancia},
                    '{fonte.replace("'", "''")}'
                )
                """

                session.sql(query).collect()
                total_inseridas += 1

            except Exception as e:
                print(f"Erro ao processar notícia: {e}")
                continue

        return f"✅ Pipeline executado! {total_inseridas} notícias inseridas."

    except Exception as e:
        return f"❌ Erro: {str(e)}"
$$;
```

**✅ Aguarde:** A criação pode levar 30-60 segundos (Snowflake instala os pacotes).

---

### **Passo 1.3: Testar a Procedure Manualmente**

Execute este comando para testar:

```sql
CALL BBAS3.PUBLIC.SP_COLETAR_NOTICIAS_BBAS3();
```

**Resultado esperado:**

```
✅ Pipeline executado! 15 notícias inseridas.
```

Verifique se os dados foram inseridos:

```sql
SELECT *
FROM BBAS3.PUBLIC.NOTICIAS_BBAS3
ORDER BY ANO_PUBLICACAO DESC, MES_PUBLICACAO DESC
LIMIT 10;
```

---

### **Passo 1.4: Criar Task para Execução Automática**

Agora vamos agendar a execução diária:

```sql
-- ============================================================
-- TASK: Executa todo dia às 8h da manhã
-- ============================================================

CREATE OR REPLACE TASK BBAS3.PUBLIC.TASK_COLETAR_NOTICIAS
    WAREHOUSE = COMPUTE_WH
    SCHEDULE = 'USING CRON 0 8 * * * America/Sao_Paulo'
    COMMENT = 'Coleta notícias BBAS3 diariamente às 8h'
AS
    CALL BBAS3.PUBLIC.SP_COLETAR_NOTICIAS_BBAS3();
```

**⚠️ IMPORTANTE:** A task é criada **SUSPENSA** por padrão. Não ative ainda!

---

### **Passo 1.5: Verificar a Task**

```sql
-- Ver detalhes da task
SHOW TASKS IN SCHEMA BBAS3.PUBLIC;

-- Ver histórico (depois de ativar)
SELECT
    NAME,
    STATE,
    SCHEDULED_TIME,
    COMPLETED_TIME,
    RETURN_VALUE
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
    TASK_NAME => 'TASK_COLETAR_NOTICIAS'
))
ORDER BY SCHEDULED_TIME DESC;
```

---

### **Passo 1.6: Ativar a Task (quando estiver pronto)**

```sql
-- ⚠️ SÓ EXECUTE ISSO QUANDO TIVER CERTEZA
ALTER TASK BBAS3.PUBLIC.TASK_COLETAR_NOTICIAS RESUME;
```

Para **pausar** depois:

```sql
ALTER TASK BBAS3.PUBLIC.TASK_COLETAR_NOTICIAS SUSPEND;
```

---

## 📊 Parte 2: Deploy do Streamlit App

### **Passo 2.1: Acessar Streamlit no Snowflake**

1. No Snowflake, clique no menu lateral em **"Projects"**
2. Clique em **"Streamlit"**
3. Clique no botão **"+ Streamlit App"** (canto superior direito)

---

### **Passo 2.2: Configurar o App**

Você verá uma tela de configuração:

**📝 Preencha:**

- **App name:** `BBAS3_Investment_Analyzer`
- **App location:**
  - Database: `BBAS3`
  - Schema: `PUBLIC`
- **Warehouse:** `COMPUTE_WH`

**Clique em "Create"**

---

### **Passo 2.3: Colar o Código**

1. **Apague** todo o código de exemplo que aparece
2. **Abra o arquivo:** `scripts/streamlit_bbas3_app.py`
3. **Copie TODO o conteúdo** do arquivo
4. **Cole** no editor do Snowflake

---

### **Passo 2.4: Adicionar Pacotes Python**

1. No canto superior direito, clique em **"Packages"**
2. Adicione estes pacotes (um por vez):
   - `plotly`
   - `pandas`
   - `numpy`

**Como adicionar:**

- Digite o nome do pacote
- Clique em "Add"
- Repita para os outros

---

### **Passo 2.5: Executar o App**

1. Clique no botão **"Run"** (canto superior direito)
2. Aguarde 10-20 segundos (primeira execução é mais lenta)
3. **Pronto!** Seu dashboard está rodando! 🎉

---

### **Passo 2.6: Compartilhar o App**

1. Clique no botão **"Share"** (canto superior direito)
2. Copie a URL gerada
3. Compartilhe com quem tiver acesso ao Snowflake

**Exemplo de URL:**

```
https://app.snowflake.com/xxxxxxx/streamlit/BBAS3_PUBLIC/BBAS3_INVESTMENT_ANALYZER
```

---

## 🔍 Parte 3: Monitoramento e Manutenção

### **3.1: Monitorar Execuções da Task**

Execute este SQL regularmente:

```sql
-- Últimas 10 execuções
SELECT
    NAME,
    STATE,
    SCHEDULED_TIME,
    COMPLETED_TIME,
    RETURN_VALUE,
    ERROR_CODE,
    ERROR_MESSAGE
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
    SCHEDULED_TIME_RANGE_START => DATEADD('day', -7, CURRENT_TIMESTAMP()),
    TASK_NAME => 'TASK_COLETAR_NOTICIAS'
))
ORDER BY SCHEDULED_TIME DESC
LIMIT 10;
```

---

### **3.2: Verificar Novos Dados**

```sql
-- Notícias por dia (últimos 7 dias)
SELECT
    ANO_PUBLICACAO,
    MES_PUBLICACAO,
    COUNT(*) as TOTAL_NOTICIAS,
    AVG(SENTIMENTO_POLARITY) as SENTIMENTO_MEDIO
FROM BBAS3.PUBLIC.NOTICIAS_BBAS3
WHERE ANO_PUBLICACAO = YEAR(CURRENT_DATE())
  AND MES_PUBLICACAO = MONTH(CURRENT_DATE())
GROUP BY ANO_PUBLICACAO, MES_PUBLICACAO
ORDER BY ANO_PUBLICACAO DESC, MES_PUBLICACAO DESC;
```

---

### **3.3: Otimizar Custos**

```sql
-- Configurar auto-suspend do warehouse (suspende após 1 min de inatividade)
ALTER WAREHOUSE COMPUTE_WH SET AUTO_SUSPEND = 60;

-- Configurar auto-resume
ALTER WAREHOUSE COMPUTE_WH SET AUTO_RESUME = TRUE;

-- Ver uso do warehouse
SELECT
    WAREHOUSE_NAME,
    SUM(CREDITS_USED) as TOTAL_CREDITS
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE START_TIME >= DATEADD('day', -30, CURRENT_TIMESTAMP())
GROUP BY WAREHOUSE_NAME
ORDER BY TOTAL_CREDITS DESC;
```

**💰 Custo Estimado:**

- Task rodando 5 min/dia em XS warehouse = **~$1.50/mês**
- Streamlit App (pay-per-use) = **~$2-5/mês** (depende do acesso)

---

## 🛠️ Troubleshooting

### **Problema 1: Task não executa**

**Solução:**

```sql
-- Verificar se está ativa
SHOW TASKS LIKE 'TASK_COLETAR_NOTICIAS';

-- Se STATE = 'suspended', ativar:
ALTER TASK BBAS3.PUBLIC.TASK_COLETAR_NOTICIAS RESUME;
```

---

### **Problema 2: Erro "invalid identifier" no Streamlit**

**Solução:**
Verifique se as colunas existem:

```sql
DESCRIBE TABLE BBAS3.PUBLIC.NOTICIAS_BBAS3;
```

Se faltar coluna, adicione:

```sql
ALTER TABLE BBAS3.PUBLIC.NOTICIAS_BBAS3
ADD COLUMN FONTE_NOTICIA VARCHAR(200);
```

---

### **Problema 3: Streamlit lento**

**Solução:**

1. Aumente o warehouse:

```sql
ALTER WAREHOUSE COMPUTE_WH SET WAREHOUSE_SIZE = 'SMALL';
```

2. Ou adicione cache no código (já incluído com `@st.cache_data`)

---

### **Problema 4: GNews não encontra notícias**

**Possíveis causas:**

- API do Google News mudou
- Bloqueio por região
- Limite de requisições

**Solução alternativa:**
Use RSS feed direto:

```python
import feedparser

feed = feedparser.parse('https://news.google.com/rss/search?q=BBAS3&hl=pt-BR&gl=BR&ceid=BR:pt-419')
```

---

## 📊 Resumo do que você terá:

✅ **Pipeline automatizado** que coleta notícias diariamente  
✅ **Dashboard interativo** rodando 24/7 no Snowflake  
✅ **Análise de sentimento** atualizada em tempo real  
✅ **4 páginas de análise** (Executivo, Técnica, Sentimento, Sinais)  
✅ **Custo baixo** (~$3-7/mês)  
✅ **Zero manutenção** necessária

---

## 🎯 Checklist Final

Antes de apresentar o projeto:

- [ ] Task criada e testada manualmente
- [ ] Task ativada (RESUME)
- [ ] Verificar 1-2 execuções bem-sucedidas
- [ ] Streamlit App rodando sem erros
- [ ] Todas as 4 páginas funcionando
- [ ] Gráficos carregando corretamente
- [ ] URL do app compartilhável
- [ ] Screenshot/vídeo do sistema funcionando

---

## 📞 Próximos Passos

1. **Teste tudo localmente primeiro** (execute as procedures manualmente)
2. **Deploy gradual:** Streamlit primeiro, depois ativa a Task
3. **Monitore por 2-3 dias** antes de apresentar
4. **Faça backup** dos dados importantes

---

## 💡 Dicas para Apresentação

Destaque estes pontos:

✨ **Arquitetura Cloud-Native** (100% Snowflake)  
✨ **Pipeline ETL automatizado** (Task + Stored Procedure)  
✨ **Python + SQL integrados** (polyglot programming)  
✨ **Machine Learning** (análise de sentimento com NLP)  
✨ **Visualização interativa** (Streamlit + Plotly)  
✨ **Escalabilidade automática** (Snowflake warehouse)  
✨ **Custo otimizado** (pay-per-use, auto-suspend)

---

**🚀 Boa sorte com o projeto! Qualquer dúvida, consulte este guia.**
