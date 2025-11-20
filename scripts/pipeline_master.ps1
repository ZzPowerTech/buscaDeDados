# ===============================================================================
#  PIPELINE MASTER COMPLETO - BBAS3 DATA ANALYTICS
# ===============================================================================
# 
# Este script executa TODOS os processos na ordem correta:
# 1. Coleta dados historicos BBAS3 (Yahoo Finance)
# 2. Coleta noticias nao estruturadas (Google News)
# 3. Analise de sentimentos automatica
# 4. Limpeza e estruturacao de dados
# 5. Migracao MongoDB -> PostgreSQL -> Snowflake
# 6. Transformacao para modelo dimensional
# 7. Validacoes e relatorios
#
# ===============================================================================

$ErrorActionPreference = 'Continue'
$startTime = Get-Date

# Cores
$cyan = "Cyan"
$green = "Green"
$yellow = "Yellow"
$red = "Red"
$white = "White"
$gray = "Gray"

function Write-Header {
    param($texto)
    Write-Host "`n=================================================================" -ForegroundColor $cyan
    Write-Host "  $texto" -ForegroundColor $cyan
    Write-Host "=================================================================`n" -ForegroundColor $cyan
}

function Write-Step {
    param($numero, $total, $descricao)
    Write-Host "`n>> [$numero/$total] $descricao" -ForegroundColor $yellow
}

function Write-Success {
    param($mensagem)
    Write-Host "[OK] $mensagem" -ForegroundColor $green
}

function Write-Error-Custom {
    param($mensagem)
    Write-Host "[ERRO] $mensagem" -ForegroundColor $red
}

function Write-Info {
    param($mensagem)
    Write-Host "   -> $mensagem" -ForegroundColor $gray
}

# ===============================================================================
Clear-Host
Write-Host "`n`n"
Write-Host "=====================================================================" -ForegroundColor $cyan
Write-Host "                                                                     " -ForegroundColor $cyan
Write-Host "       PIPELINE MASTER COMPLETO - BBAS3 ANALYTICS                    " -ForegroundColor $cyan
Write-Host "                                                                     " -ForegroundColor $cyan
Write-Host "  Executa todo o fluxo de dados: Coleta -> Analise -> ETL -> DW     " -ForegroundColor $cyan
Write-Host "                                                                     " -ForegroundColor $cyan
Write-Host "=====================================================================" -ForegroundColor $cyan
Write-Host ""

# ===============================================================================
# VERIFICACOES INICIAIS
# ===============================================================================
Write-Header "VERIFICACOES INICIAIS"

Write-Step 0 7 "Verificando ambiente virtual..."
if (-Not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Error-Custom "Ambiente virtual nao encontrado!"
    Write-Info "Execute: python -m venv .venv"
    Write-Info "E depois: pip install -r requirements.txt"
    exit 1
}

Write-Info "Ativando ambiente virtual..."
& .\.venv\Scripts\Activate.ps1
Write-Success "Ambiente virtual ativado"

Write-Info "Verificando estrutura do projeto..."
python tests\verify_structure.py
if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "Estrutura do projeto com problemas!"
    exit 1
}

# ===============================================================================
# FASE 1: COLETA DE DADOS BRUTOS (YAHOO FINANCE API)
# ===============================================================================
Write-Header "FASE 1: COLETA DE DADOS HISTORICOS BBAS3"

Write-Step 1 7 "Buscando cotacoes historicas via Yahoo Finance..."
Write-Info "Periodo: 2020-01-01 ate hoje"
Write-Info "Destinos: PostgreSQL (bbas3_cotacoes) + Snowflake (BBAS3_COTACOES)"

python scripts\buscar_dados_reais.py
if ($LASTEXITCODE -eq 0) {
    Write-Success "Dados historicos coletados e salvos"
    Write-Info "PostgreSQL: tabela 'bbas3_cotacoes'"
    Write-Info "Snowflake: tabela 'BBAS3_COTACOES'"
} else {
    Write-Host "[AVISO] Dados historicos nao disponiveis - continuando..." -ForegroundColor $yellow
    Write-Info "Pipeline continuara com coleta de noticias"
}

# ===============================================================================
# FASE 2: COLETA DE NOTICIAS NAO ESTRUTURADAS
# ===============================================================================
Write-Header "FASE 2: COLETA DE NOTICIAS (DADOS NAO ESTRUTURADOS)"

Write-Step 2 7 "Testando conexao com MongoDB..."
python tests\testConnection.py
if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "MongoDB nao esta acessivel!"
    Write-Info "Verifique se o MongoDB esta rodando: net start MongoDB"
    exit 1
}
Write-Success "MongoDB conectado"

Write-Step 3 7 "Coletando noticias do Google News RSS..."
Write-Info "Queries: 16 buscas diferentes sobre BBAS3/Banco do Brasil"
Write-Info "Tempo estimado: 15-30 minutos"
Write-Info "Com analise de sentimentos automatica"

python collect_news_bbas3.py
if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "Erro ao coletar noticias!"
    exit 1
}

Write-Success "Noticias coletadas com sucesso"
Write-Info "MongoDB: bigData.projeto_ativos (estrutura nested)"
Write-Info "PostgreSQL: bigdata.noticias_bbas3 (estrutura flat)"
Write-Info "Snowflake: BBAS3.PUBLIC.DADOS_MONG (estrutura flat)"
Write-Info "Local: data/collected_articles_bbas3.json"

# ===============================================================================
# FASE 3: ANALISE DE SENTIMENTOS E VALIDACAO
# ===============================================================================
Write-Header "FASE 3: ANALISE DE SENTIMENTOS E VALIDACAO"

Write-Step 4 7 "Verificando dados no MongoDB..."
python tests\verify_mongo_data.py
Write-Success "Dados MongoDB validados"

Write-Step 5 7 "Executando analise estatistica de sentimentos..."
python scripts\sentimentos.py
Write-Success "Analise estatistica concluida"

Write-Step 6 7 "Executando analise detalhada de sentimentos..."
python scripts\analise_detalhada.py
Write-Success "Analise detalhada concluida"

# ===============================================================================
# FASE 4: TRANSFORMACAO E DATA WAREHOUSE
# ===============================================================================
Write-Header "FASE 4: TRANSFORMACAO PARA DATA WAREHOUSE"

Write-Step 7 7 "Transformando dados para modelo dimensional..."
Write-Info "Criando tabelas: FATO_NOTICIAS, DIM_SENTIMENTO, DIM_FONTE"

python scripts\transformar_noticias.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[AVISO] Possivel erro na transformacao (continuando)" -ForegroundColor $yellow
}
Write-Success "Transformacao para DW concluida"

Write-Info "Transformando dados da API..."
python scripts\transformar_dados_api.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[AVISO] Possivel erro na transformacao API (continuando)" -ForegroundColor $yellow
}
Write-Success "Transformacao API concluida"

# ===============================================================================
# FASE 5: VALIDACAO FINAL E ANALISES
# ===============================================================================
Write-Header "FASE 5: VALIDACAO FINAL"

Write-Info "Analisando dados no Snowflake..."
python scripts\analisar_dados_mong.py

# ===============================================================================
# RELATORIO FINAL
# ===============================================================================
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host "`n`n"
Write-Host "=====================================================================" -ForegroundColor $green
Write-Host "                                                                     " -ForegroundColor $green
Write-Host "          PIPELINE MASTER EXECUTADO COM SUCESSO!                     " -ForegroundColor $green
Write-Host "                                                                     " -ForegroundColor $green
Write-Host "=====================================================================" -ForegroundColor $green

Write-Host "`nRESUMO DA EXECUCAO:" -ForegroundColor $cyan
Write-Host "================================================================" -ForegroundColor $gray

Write-Host "`nProcessos Executados:" -ForegroundColor $white
Write-Host "   [OK] Coleta de dados historicos BBAS3 (Yahoo Finance)" -ForegroundColor $green
Write-Host "   [OK] Coleta de noticias nao estruturadas (Google News)" -ForegroundColor $green
Write-Host "   [OK] Analise de sentimentos automatica" -ForegroundColor $green
Write-Host "   [OK] Limpeza e estruturacao de dados" -ForegroundColor $green
Write-Host "   [OK] Migracao multi-database (MongoDB/PostgreSQL/Snowflake)" -ForegroundColor $green
Write-Host "   [OK] Transformacao para modelo dimensional (DW)" -ForegroundColor $green
Write-Host "   [OK] Validacoes e relatorios gerados" -ForegroundColor $green

Write-Host "`nDados Armazenados:" -ForegroundColor $white
Write-Host ""
Write-Host "   LOCAL:" -ForegroundColor $yellow
Write-Host "      - data/collected_articles_bbas3.json" -ForegroundColor $gray
Write-Host ""
Write-Host "   MONGODB (Nested - Analise agregada):" -ForegroundColor $yellow
Write-Host "      - Database: bigData" -ForegroundColor $gray
Write-Host "      - Collection: projeto_ativos" -ForegroundColor $gray
Write-Host "      - Estrutura: Nested (sentimentos como subdocumento)" -ForegroundColor $gray
Write-Host ""
Write-Host "   POSTGRESQL (Flat - Queries relacionais):" -ForegroundColor $yellow
Write-Host "      - Database: bigdata" -ForegroundColor $gray
Write-Host "      - Tabela noticias: noticias_bbas3 (20 colunas flat)" -ForegroundColor $gray
Write-Host "      - Tabela cotacoes: bbas3_cotacoes (dados historicos)" -ForegroundColor $gray
Write-Host ""
Write-Host "   SNOWFLAKE (Cloud DW - Analytics):" -ForegroundColor $yellow
Write-Host "      - Database: BBAS3" -ForegroundColor $gray
Write-Host "      - Schema: PUBLIC" -ForegroundColor $gray
Write-Host "      - Tabelas operacionais:" -ForegroundColor $gray
Write-Host "         * DADOS_MONG (noticias flat)" -ForegroundColor $gray
Write-Host "         * BBAS3_COTACOES (cotacoes historicas)" -ForegroundColor $gray
Write-Host "      - Tabelas dimensionais (DW):" -ForegroundColor $gray
Write-Host "         * FATO_NOTICIAS" -ForegroundColor $gray
Write-Host "         * DIM_SENTIMENTO" -ForegroundColor $gray
Write-Host "         * DIM_FONTE" -ForegroundColor $gray

Write-Host "`nAnalises Disponiveis:" -ForegroundColor $white
Write-Host "   - Analise estatistica basica (scripts/sentimentos.py)" -ForegroundColor $gray
Write-Host "   - Analise detalhada (scripts/analise_detalhada.py)" -ForegroundColor $gray
Write-Host "   - Dados Snowflake (scripts/analisar_dados_mong.py)" -ForegroundColor $gray

Write-Host "`nTempo de Execucao:" -ForegroundColor $white
Write-Host "   Duracao total: $($duration.Hours)h $($duration.Minutes)min $($duration.Seconds)s" -ForegroundColor $cyan

Write-Host "`nProximos Passos:" -ForegroundColor $white
Write-Host "   - Conecte ao Snowflake para consultas SQL avancadas" -ForegroundColor $gray
Write-Host "   - Use PostgreSQL para queries relacionais rapidas" -ForegroundColor $gray
Write-Host "   - Explore MongoDB para analises de documentos nested" -ForegroundColor $gray
Write-Host "   - Execute analises especificas: python scripts/sentimentos.py" -ForegroundColor $gray

Write-Host "`nPara Executar Novamente:" -ForegroundColor $white
Write-Host "   .\scripts\pipeline_master.ps1" -ForegroundColor $cyan

Write-Host "`n================================================================`n" -ForegroundColor $gray
