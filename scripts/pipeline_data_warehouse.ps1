# Pipeline completo: MongoDB → PostgreSQL → Snowflake + API Yahoo Finance
# Executa todo o fluxo de dados automaticamente

$ErrorActionPreference = 'Continue'

Write-Host "`n" -NoNewline
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  PIPELINE COMPLETO - BBAS3 DATA WAREHOUSE" -ForegroundColor Cyan
Write-Host "  MongoDB → PostgreSQL → Snowflake + Yahoo Finance API" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Verificar venv
if (-Not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "⚠️  Ambiente virtual não encontrado. Execute .\setup_env.ps1 primeiro." -ForegroundColor Yellow
    exit 1
}

Write-Host "🔧 Ativando ambiente virtual..." -ForegroundColor Blue
.\venv\Scripts\Activate.ps1

$startTime = Get-Date

# ===================================
# FASE 1: COLETA DE NOTÍCIAS (MongoDB)
# ===================================
Write-Host "`n╔════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  FASE 1: COLETA DE NOTÍCIAS DO GOOGLE NEWS (MongoDB)  ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`n📡 [1/7] Testando conexão MongoDB..." -ForegroundColor Yellow
python testConnection.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro na conexão com MongoDB!" -ForegroundColor Red
    exit 1
}

Write-Host "`n📰 [2/7] Coletando notícias (15-30 min)..." -ForegroundColor Yellow
python collect_news_bbas3.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao coletar notícias!" -ForegroundColor Red
    exit 1
}

Write-Host "`n🗄️  [3/7] Verificando dados no MongoDB..." -ForegroundColor Yellow
python verify_mongo_data.py

# ===================================
# FASE 2: COLETA DE DADOS REAIS (API)
# ===================================
Write-Host "`n╔════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  FASE 2: COLETA DE COTAÇÕES (Yahoo Finance API)       ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`n📊 [4/7] Buscando dados reais via API..." -ForegroundColor Yellow
Write-Host "   → Salvando em PostgreSQL e Snowflake" -ForegroundColor Gray
python buscar_dados_reais.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao buscar dados da API!" -ForegroundColor Red
    exit 1
}

# ===================================
# FASE 3: MIGRAÇÃO PARA SNOWFLAKE
# ===================================
Write-Host "`n╔════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  FASE 3: MIGRAÇÃO PostgreSQL → Snowflake             ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`n❄️  [5/7] Migrando dados para Snowflake..." -ForegroundColor Yellow
python migrar.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Possível erro na migração, continuando..." -ForegroundColor Yellow
}

# ===================================
# FASE 4: TRANSFORMAÇÃO (DATA WAREHOUSE)
# ===================================
Write-Host "`n╔════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  FASE 4: TRANSFORMAÇÃO - MODELO DIMENSIONAL           ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`n🔄 [6/7] Transformando dados da API (Star Schema)..." -ForegroundColor Yellow
python transformar_dados_api.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Possível erro na transformação da API, continuando..." -ForegroundColor Yellow
}

Write-Host "`n🔄 [6/7] Transformando dados de notícias (Star Schema)..." -ForegroundColor Yellow
python transformar_noticias.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Possível erro na transformação de notícias, continuando..." -ForegroundColor Yellow
}

# ===================================
# FASE 5: ANÁLISES
# ===================================
Write-Host "`n╔════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  FASE 5: ANÁLISES DE SENTIMENTO                       ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`n📊 [7/7] Executando análises..." -ForegroundColor Yellow

Write-Host "`n   → Análise Estatística Básica" -ForegroundColor Gray
python sentimentos.py

Write-Host "`n   → Análise Detalhada por Tema" -ForegroundColor Gray
python analise_detalhada.py

# ===================================
# RESUMO FINAL
# ===================================
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host "`n" -NoNewline
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ PIPELINE COMPLETO EXECUTADO COM SUCESSO!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan

Write-Host "`n📁 Dados Disponíveis:" -ForegroundColor White
Write-Host "   ├─ MongoDB: bigData.projeto_ativos (notícias)" -ForegroundColor Gray
Write-Host "   ├─ PostgreSQL: bigdata.bbas3_dados_reais_api (cotações)" -ForegroundColor Gray
Write-Host "   ├─ PostgreSQL: bigdata.dados_mong (notícias)" -ForegroundColor Gray
Write-Host "   └─ JSON local: collected_articles_bbas3.json" -ForegroundColor Gray

Write-Host "`n❄️  Snowflake Data Warehouse:" -ForegroundColor White
Write-Host "   Database: BBAS3" -ForegroundColor Gray
Write-Host "   Schema: PUBLIC" -ForegroundColor Gray
Write-Host ""
Write-Host "   Tabelas Fato:" -ForegroundColor Cyan
Write-Host "   ├─ FATO_ACOES_REAL (cotações históricas)" -ForegroundColor Gray
Write-Host "   └─ FATO_NOTICIAS (notícias com sentimento)" -ForegroundColor Gray
Write-Host ""
Write-Host "   Tabelas Dimensão:" -ForegroundColor Cyan
Write-Host "   ├─ DIM_TEMPO_REAL (dimensão temporal)" -ForegroundColor Gray
Write-Host "   └─ DIM_SENTIMENTO (classificação de sentimento)" -ForegroundColor Gray
Write-Host ""
Write-Host "   Views Analíticas:" -ForegroundColor Cyan
Write-Host "   ├─ VW_RESUMO_MENSAL_REAL (performance mensal)" -ForegroundColor Gray
Write-Host "   ├─ VW_ANALISE_ANUAL_REAL (análise por ano)" -ForegroundColor Gray
Write-Host "   ├─ VW_INDICADORES_TECNICOS (médias móveis, volatilidade)" -ForegroundColor Gray
Write-Host "   ├─ VW_PERFORMANCE_TRIMESTRAL (análise trimestral)" -ForegroundColor Gray
Write-Host "   ├─ VW_SENTIMENTO_POR_PERIODO (sentimento por dia)" -ForegroundColor Gray
Write-Host "   ├─ VW_NOTICIAS_POR_FONTE (distribuição por fonte)" -ForegroundColor Gray
Write-Host "   └─ VW_CORRELACAO_NOTICIAS_PRECO (correlação notícias x preço)" -ForegroundColor Gray

Write-Host "`n⏱️  Tempo Total: " -NoNewline -ForegroundColor White
Write-Host "$($duration.Minutes) min $($duration.Seconds) seg" -ForegroundColor Yellow

Write-Host "`n💡 Próximos Passos:" -ForegroundColor Cyan
Write-Host "   1. Acesse o Snowflake para consultar as views criadas" -ForegroundColor White
Write-Host "   2. Execute queries analíticas combinando notícias e cotações" -ForegroundColor White
Write-Host "   3. Crie dashboards no Power BI conectando ao Snowflake" -ForegroundColor White

Write-Host "`n🔄 Para executar novamente:" -ForegroundColor Cyan
Write-Host "   .\pipeline_data_warehouse.ps1`n" -ForegroundColor White
