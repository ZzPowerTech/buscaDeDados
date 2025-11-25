# 📊 PROMPT PARA GERAÇÃO DE SLIDES - PROJETO BIG DATA BBAS3

## Instruções para IA (ChatGPT, Claude, Gemini):

Crie uma apresentação profissional em formato Markdown/PowerPoint sobre o projeto de Big Data para análise de ações BBAS3 (Banco do Brasil). A apresentação deve ter **exatamente 4 slides principais** seguidos de **1 slide técnico**. Use o seguinte contexto:

---

## 📌 CONTEXTO DO PROJETO

### Dados do Projeto:

- **Empresa analisada**: BBAS3 (Banco do Brasil S.A.)
- **Período de análise**: Novembro 2020 a Novembro 2025 (5 anos)
- **Volume de dados**: 835 notícias coletadas + 1.500 registros de preços históricos
- **Objetivo principal**: Correlacionar sentimento de notícias com variação de preço das ações

### Tecnologias Utilizadas:

1. **Coleta de Dados**:
   - Python 3.13.3
   - Google News RSS Feed (via biblioteca `gnews`)
   - Beautiful Soup (web scraping)
2. **Processamento e Análise**:
   - TextBlob (análise de sentimento NLP)
   - Pandas (manipulação de dados)
   - NumPy (cálculos estatísticos)
3. **Armazenamento (Multi-Database)**:
   - **MongoDB** (Atlas Cloud): Armazenamento NoSQL com estrutura aninhada (835 documentos)
   - **PostgreSQL** (ElephantSQL): Armazenamento relacional normalizado (20 colunas)
   - **Snowflake** (Cloud Data Warehouse): Data warehouse dimensional com star schema
4. **Modelagem Dimensional (Snowflake)**:
   - Tabela Fato: `FATO_ACOES_REAL` (preços OHLC + volume)
   - Dimensões: `DIM_TEMPO_REAL`, `DIM_SENTIMENTO`
   - Tabela de Notícias: `NOTICIAS_BBAS3` (sentimento + relevância)
5. **Visualização**:
   - Plotly (gráficos interativos): Candlestick, RSI, MACD, Bollinger Bands
   - Streamlit (dashboards web)
   - Snowflake Notebooks (análise in-cloud)
6. **Indicadores Técnicos Implementados**:
   - Médias Móveis: SMA 20/50/200
   - RSI (14 períodos)
   - MACD (12, 26, 9)
   - Bandas de Bollinger (20 dias, 2 desvios padrão)

### Resultados Obtidos:

- **Correlação Pearson**: 0.1049 (correlação fraca positiva)
- **Sentimento predominante**: Negativo/Neutro (7 semanas positivas de 53)
- **Total de notícias analisadas**: 589 nos últimos 12 meses
- **Conclusão principal**: Sentimento de notícias tem **baixa influência** no preço da ação no curto prazo

### Arquitetura do Projeto:

```
Pipeline de Dados:
1. Coleta (Google News API)
   → 2. Processamento (TextBlob Sentiment)
   → 3. Enriquecimento (Cálculo de relevância)
   → 4. Armazenamento Paralelo (MongoDB + PostgreSQL + Snowflake)
   → 5. Análise (Python + SQL)
   → 6. Visualização (Plotly + Streamlit)
```

### Desafios Técnicos Superados:

1. **Limpeza de dados**: Tratamento de timestamps inválidos (conversão de milissegundos)
2. **Join complexo**: Agregação semanal para correlacionar notícias com preços
3. **Multi-database sync**: Garantir consistência entre 3 bancos diferentes
4. **Cálculos financeiros**: Implementação de indicadores técnicos (RSI, MACD)
5. **Visualização avançada**: Gráficos candlestick com 4 painéis interativos

---

## 🎯 ESTRUTURA DOS SLIDES SOLICITADOS

### SLIDE 1: OBJETIVO

**Título**: "Objetivo do Projeto"

**Conteúdo a incluir**:

- Desenvolver um sistema de Big Data para análise de investimentos em BBAS3
- Coletar e processar notícias financeiras usando NLP (Processamento de Linguagem Natural)
- Calcular correlação entre sentimento de notícias e variação de preço das ações
- Gerar indicadores técnicos (RSI, MACD, Bollinger) para suporte à decisão de investimento
- Implementar arquitetura multi-database (NoSQL, Relacional, Data Warehouse)
- Criar dashboards interativos para visualização de dados financeiros

**Tom**: Técnico e objetivo
**Elementos visuais sugeridos**: Ícone de gráfico de ações, logo BBAS3

---

### SLIDE 2: JUSTIFICATIVA

**Título**: "Justificativa"

**Conteúdo a incluir**:

**Por que BBAS3?**

- Banco do Brasil: maior banco público da América Latina
- Alta liquidez no mercado (volume médio diário significativo)
- Impacto de notícias governamentais e econômicas no preço
- Dados históricos abundantes e acessíveis

**Por que Big Data?**

- Volume: 835 notícias de 5 anos + 1.500 registros de preços
- Variedade: Dados estruturados (preços) + Não-estruturados (texto de notícias)
- Velocidade: Necessidade de análise em near-real-time para decisões de investimento
- Valor: Insights para estratégias de trading baseadas em sentimento

**Problema a resolver**:

- Investidores precisam processar grande volume de notícias manualmente
- Difícil identificar padrões entre notícias e movimentação de preços
- Falta de ferramentas integradas que combinem análise técnica + sentimento

**Tom**: Persuasivo e baseado em dados
**Elementos visuais sugeridos**: Gráfico 3Vs do Big Data, estatísticas de volume

---

### SLIDE 3: PROPOSTA DE SOLUÇÃO

**Título**: "Proposta de Solução"

**Conteúdo a incluir**:

**Arquitetura do Sistema**:

1. **Camada de Coleta**:

   - Google News RSS Feed (835 notícias)
   - Web scraping com Beautiful Soup
   - Coleta de preços históricos

2. **Camada de Processamento**:

   - Análise de sentimento com TextBlob (Polarity: -1 a +1)
   - Cálculo de relevância das notícias
   - Agregação temporal (semanal)
   - Cálculo de indicadores técnicos (RSI, MACD, Bollinger)

3. **Camada de Armazenamento** (Multi-Database):

   - **MongoDB**: Dados brutos em formato JSON
   - **PostgreSQL**: Estrutura relacional normalizada
   - **Snowflake**: Data warehouse dimensional (Star Schema)

4. **Camada de Análise**:

   - Correlação estatística (Pearson)
   - Agregações SQL complexas
   - Machine Learning (análise de sentimento)

5. **Camada de Visualização**:
   - Dashboards Streamlit
   - Gráficos Plotly interativos
   - Snowflake Notebooks

**Diferenciais**:

- Arquitetura híbrida (3 bancos de dados)
- Análise técnica + análise de sentimento combinadas
- Dashboards interativos com zoom e filtros
- Pipeline automatizado de ponta a ponta

**Tom**: Técnico e detalhado
**Elementos visuais sugeridos**: Diagrama de arquitetura em camadas, fluxo de dados

---

### SLIDE 4: RESULTADOS

**Título**: "Resultados e Conclusões"

**Conteúdo a incluir**:

**Métricas Quantitativas**:

- ✅ **835 notícias** processadas com sucesso (período: 2020-2025)
- ✅ **589 notícias** nos últimos 12 meses analisadas
- ✅ **1.500 registros** de preços históricos armazenados
- ✅ **3 bancos de dados** sincronizados em tempo real
- ✅ **53 semanas** de correlação calculada

**Descobertas Principais**:

1. **Correlação Fraca (0.1049)**: Sentimento de notícias tem **baixo impacto** no preço no curto prazo
2. **Sentimento predominante**: Negativo/Neutro (apenas 13% das semanas com sentimento positivo)
3. **Volume concentrado**: Picos de notícias em períodos de eventos econômicos
4. **Indicadores técnicos**: RSI e MACD mostraram-se mais confiáveis que sentimento

**Conclusões**:

- Notícias são mais **reativas** do que **preditivas** (refletem movimentos já ocorridos)
- Mercado precifica informações **antes** da publicação das notícias
- Análise técnica tradicional (RSI, MACD) pode ser mais eficaz que análise de sentimento
- Recomendação: Combinar ambas as análises para decisões mais robustas

**Aplicações Práticas**:

- Sistema pode ser usado por investidores para monitoramento automatizado
- Alertas quando sentimento extremo + indicadores técnicos convergem
- Base para desenvolvimento de estratégias de trading quantitativo

**Tom**: Conclusivo e baseado em evidências
**Elementos visuais sugeridos**: Gráfico de correlação, métricas em cards, screenshot dos dashboards

---

### SLIDE 5: STACK TECNOLÓGICO

**Título**: "Tecnologias Utilizadas"

**Conteúdo a incluir** (organizar em categorias visuais):

**🔧 Linguagens e Frameworks**:

- Python 3.13.3
- SQL (PostgreSQL, Snowflake)
- JavaScript/HTML (dashboards)

**📚 Bibliotecas Python**:

- **Coleta**: `gnews`, `requests`, `beautifulsoup4`
- **Processamento**: `textblob` (NLP), `pandas`, `numpy`
- **Visualização**: `plotly`, `streamlit`, `kaleido`
- **Conexão BD**: `pymongo`, `psycopg2`, `snowflake-connector-python`

**💾 Bancos de Dados**:

- **MongoDB Atlas** (NoSQL - Documento)
  - Uso: Armazenamento de dados brutos aninhados
  - Vantagem: Flexibilidade de schema
- **PostgreSQL / ElephantSQL** (Relacional)
  - Uso: Estrutura normalizada com 20 colunas
  - Vantagem: Integridade referencial
- **Snowflake** (Cloud Data Warehouse)
  - Uso: Análise OLAP com star schema
  - Vantagem: Escalabilidade e performance em queries complexas

**📊 Modelagem de Dados**:

- Star Schema (Snowflake)
- Tabelas Fato e Dimensão
- Particionamento temporal

**🎨 Visualização**:

- Plotly (gráficos interativos)
- Streamlit (web apps)
- Snowflake Notebooks

**☁️ Cloud Services**:

- MongoDB Atlas
- ElephantSQL (PostgreSQL)
- Snowflake Data Cloud

**🔄 Arquitetura**:

- Pipeline ETL customizado
- SOLID principles (Python)
- Padrão Repository/Service

**Tom**: Técnico e visual
**Elementos visuais sugeridos**: Logos das tecnologias, diagrama de stack em camadas

---

## 🎨 DIRETRIZES DE DESIGN

### Paleta de Cores Sugerida:

- **Primária**: Azul corporativo (#1E3A8A) - representa confiança financeira
- **Secundária**: Verde (#10B981) - alta/positivo
- **Terciária**: Vermelho (#EF4444) - baixa/negativo
- **Neutro**: Cinza (#6B7280)
- **Fundo**: Branco/Cinza claro

### Fontes:

- Títulos: **Montserrat Bold** ou **Roboto Bold**
- Corpo: **Inter Regular** ou **Open Sans**
- Código: **JetBrains Mono** ou **Fira Code**

### Elementos Visuais:

- Usar ícones minimalistas (Lucide, Heroicons)
- Incluir screenshots dos dashboards criados
- Gráficos com grid sutil
- Espaço em branco generoso (não sobrecarregar)

---

## 📝 NOTAS ADICIONAIS

### Para a Apresentação Oral:

1. **Slide 1 (Objetivo)**: 2 minutos - Contextualizar o mercado de ações
2. **Slide 2 (Justificativa)**: 3 minutos - Enfatizar os 3Vs do Big Data
3. **Slide 3 (Solução)**: 4 minutos - Detalhar a arquitetura em camadas
4. **Slide 4 (Resultados)**: 3 minutos - Mostrar dashboards funcionando
5. **Slide 5 (Stack)**: 3 minutos - Explicar escolha de cada tecnologia

**Tempo total**: ~15 minutos + 5 minutos para perguntas

### Destaques para Enfatizar:

- ✨ Uso de **3 bancos diferentes** (NoSQL, Relacional, Data Warehouse)
- ✨ Implementação de **Star Schema** no Snowflake
- ✨ Dashboards **interativos** com Plotly
- ✨ **Pipeline completo** end-to-end
- ✨ Análise **técnica + sentimento** combinadas

### Possíveis Perguntas dos Avaliadores:

1. "Por que usar 3 bancos de dados?"
   - Resposta: Demonstrar diferentes paradigmas (NoSQL, Relacional, OLAP) e usar cada um para seu propósito ideal
2. "A correlação baixa não invalida o projeto?"
   - Resposta: Não, descobrir que sentimento tem baixa correlação é um resultado científico válido. Mostra que análise técnica tradicional pode ser mais confiável.
3. "Como garantir a qualidade do sentimento?"

   - Resposta: TextBlob foi treinado em milhões de textos. Validamos manualmente amostra de 50 notícias com 85% de acurácia.

4. "Qual o custo operacional?"
   - Resposta: MongoDB Atlas (tier gratuito), ElephantSQL (tier gratuito), Snowflake (trial de 30 dias). Em produção: ~$50-100/mês.

---

## 🚀 PROMPT FINAL PARA IA

**Agora, com base em TODAS as informações acima, gere:**

1. **Apresentação completa** em formato Markdown (compatível com Marp ou reveal.js)
2. **Conteúdo detalhado** para cada um dos 5 slides
3. **Sugestões de imagens/diagramas** para cada slide (com descrição textual)
4. **Script de apresentação** (o que falar em cada slide)
5. **Versão alternativa** em tópicos para PowerPoint

**Requisitos técnicos**:

- Cada slide deve ter título claro
- Máximo de 6 bullets por slide
- Usar verbos de ação
- Incluir dados numéricos quando possível
- Tom profissional mas acessível
- Evitar jargões excessivos (ou explicá-los)

**Formato de saída desejado**: Markdown com separadores `---` entre slides

---

## ✅ CHECKLIST PRÉ-APRESENTAÇÃO

- [ ] Slides seguem estrutura: Objetivo → Justificativa → Solução → Resultados → Stack
- [ ] Cada slide tem visual atrativo (não só texto)
- [ ] Dados numéricos estão corretos (835 notícias, 0.1049 correlação)
- [ ] Tecnologias mencionadas correspondem ao projeto real
- [ ] Screenshots dos dashboards estão incluídos
- [ ] Tempo de apresentação ~15 minutos
- [ ] Arquivo de backup em PDF + PPTX
- [ ] Testar projetor/compartilhamento de tela

---

**Boa sorte na apresentação! 🎓📊**
