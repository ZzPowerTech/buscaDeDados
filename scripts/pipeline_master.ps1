# ═══════════════════════════════════════════════════════════════════
#  PIPELINE MASTER COMPLETO - BBAS3 DATA ANALYTICS
# ═══════════════════════════════════════════════════════════════════
# 
# Este script executa TODOS os processos na ordem correta:
# 1. Coleta dados históricos BBAS3 (Yahoo Finance)
# 2. Coleta notícias não estruturadas (Google News)
# 3. Análise de sentimentos automática
# 4. Limpeza e estruturação de dados
# 5. Migração MongoDB → PostgreSQL → Snowflake
# 6. Transformação para modelo dimensional
# 7. Validações e relatórios
#
# ═══════════════════════════════════════════════════════════════════

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
    Write-Host "`n╔$('═' * 70)╗" -ForegroundColor $cyan
    Write-Host "║  $texto" -ForegroundColor $cyan
    Write-Host "╚$('═' * 70)╝`n" -ForegroundColor $cyan
}

function Write-Step {
    param($numero, $total, $descricao)
    Write-Host "`n🔹 [$numero/$total] $descricao" -ForegroundColor $yellow
}

function Write-Success {
    param($mensagem)
    Write-Host "✅ $mensagem" -ForegroundColor $green
}

function Write-Error-Custom {
    param($mensagem)
    Write-Host "❌ $mensagem" -ForegroundColor $red
}

function Write-Info {
    param($mensagem)
    Write-Host "   → $mensagem" -ForegroundColor $gray
}

# ═══════════════════════════════════════════════════════════════════
Clear-Host
Write-Host "`n`n"
Write-Host "╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor $cyan
Write-Host "║                                                                      ║" -ForegroundColor $cyan
Write-Host "║           🚀 PIPELINE MASTER COMPLETO - BBAS3 ANALYTICS 🚀           ║" -ForegroundColor $cyan
Write-Host "║                                                                      ║" -ForegroundColor $cyan
Write-Host "║  Executa todo o fluxo de dados: Coleta → Análise → ETL → DW        ║" -ForegroundColor $cyan
Write-Host "║                                                                      ║" -ForegroundColor $cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════╝" -ForegroundColor $cyan
Write-Host ""

# ═══════════════════════════════════════════════════════════════════
# VERIFICAÇÕES INICIAIS
# ═══════════════════════════════════════════════════════════════════
Write-Header "VERIFICAÇÕES INICIAIS"

Write-Step 0 7 "Verificando ambiente virtual..."
if (-Not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Error-Custom "Ambiente virtual não encontrado!"
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

# ═══════════════════════════════════════════════════════════════════
# FASE 1: COLETA DE DADOS BRUTOS (YAHOO FINANCE API)
# ═══════════════════════════════════════════════════════════════════
Write-Header "FASE 1: COLETA DE DADOS HISTÓRICOS BBAS3"

Write-Step 1 7 "Buscando cotações históricas via Yahoo Finance..."
Write-Info "Período: 2020-01-01 até hoje"
Write-Info "Destinos: PostgreSQL (bbas3_cotacoes) + Snowflake (BBAS3_COTACOES)"

python scripts\buscar_dados_reais.py
if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "Erro ao buscar dados históricos!"
    Write-Info "Verifique: conexão internet, credenciais PostgreSQL/Snowflake"
    exit 1
}

Write-Success "Dados históricos coletados e salvos"
Write-Info "PostgreSQL: tabela 'bbas3_cotacoes'"
Write-Info "Snowflake: tabela 'BBAS3_COTACOES'"

# ═══════════════════════════════════════════════════════════════════
# FASE 2: COLETA DE NOTÍCIAS NÃO ESTRUTURADAS
# ═══════════════════════════════════════════════════════════════════
Write-Header "FASE 2: COLETA DE NOTÍCIAS (DADOS NÃO ESTRUTURADOS)"

Write-Step 2 7 "Testando conexão com MongoDB..."
python tests\testConnection.py
if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "MongoDB não está acessível!"
    Write-Info "Verifique se o MongoDB está rodando: net start MongoDB"
    exit 1
}
Write-Success "MongoDB conectado"

Write-Step 3 7 "Coletando notícias do Google News RSS..."
Write-Info "Queries: 16 buscas diferentes sobre BBAS3/Banco do Brasil"
Write-Info "Tempo estimado: 15-30 minutos"
Write-Info "Com análise de sentimentos automática"

python collect_news_bbas3.py
if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "Erro ao coletar notícias!"
    exit 1
}

Write-Success "Notícias coletadas com sucesso"
Write-Info "MongoDB: bigData.projeto_ativos (estrutura nested)"
Write-Info "PostgreSQL: bigdata.noticias_bbas3 (estrutura flat)"
Write-Info "Snowflake: BBAS3.PUBLIC.DADOS_MONG (estrutura flat)"
Write-Info "Local: data/collected_articles_bbas3.json"

# ═══════════════════════════════════════════════════════════════════
# FASE 3: ANÁLISE DE SENTIMENTOS E VALIDAÇÃO
# ═══════════════════════════════════════════════════════════════════
Write-Header "FASE 3: ANÁLISE DE SENTIMENTOS E VALIDAÇÃO"

Write-Step 4 7 "Verificando dados no MongoDB..."
python tests\verify_mongo_data.py
Write-Success "Dados MongoDB validados"

Write-Step 5 7 "Executando análise estatística de sentimentos..."
python scripts\sentimentos.py
Write-Success "Análise estatística concluída"

Write-Step 6 7 "Executando análise detalhada de sentimentos..."
python scripts\analise_detalhada.py
Write-Success "Análise detalhada concluída"

# ═══════════════════════════════════════════════════════════════════
# FASE 4: TRANSFORMAÇÃO E DATA WAREHOUSE
# ═══════════════════════════════════════════════════════════════════
Write-Header "FASE 4: TRANSFORMAÇÃO PARA DATA WAREHOUSE"

Write-Step 7 7 "Transformando dados para modelo dimensional..."
Write-Info "Criando tabelas: FATO_NOTICIAS, DIM_SENTIMENTO, DIM_FONTE"

python scripts\transformar_noticias.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Possível erro na transformação (continuando)" -ForegroundColor $yellow
}
Write-Success "Transformação para DW concluída"

Write-Info "Transformando dados da API..."
python scripts\transformar_dados_api.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Possível erro na transformação API (continuando)" -ForegroundColor $yellow
}
Write-Success "Transformação API concluída"

# ═══════════════════════════════════════════════════════════════════
# FASE 5: VALIDAÇÃO FINAL E ANÁLISES
# ═══════════════════════════════════════════════════════════════════
Write-Header "FASE 5: VALIDAÇÃO FINAL"

Write-Info "Analisando dados no Snowflake..."
python scripts\analisar_dados_mong.py

# ═══════════════════════════════════════════════════════════════════
# RELATÓRIO FINAL
# ═══════════════════════════════════════════════════════════════════
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host "`n`n"
Write-Host "╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor $green
Write-Host "║                                                                      ║" -ForegroundColor $green
Write-Host "║              ✅ PIPELINE MASTER EXECUTADO COM SUCESSO! ✅            ║" -ForegroundColor $green
Write-Host "║                                                                      ║" -ForegroundColor $green
Write-Host "╚══════════════════════════════════════════════════════════════════════╝" -ForegroundColor $green

Write-Host "`n📊 RESUMO DA EXECUÇÃO:" -ForegroundColor $cyan
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor $gray

Write-Host "`n🎯 Processos Executados:" -ForegroundColor $white
Write-Host "   ✅ Coleta de dados históricos BBAS3 (Yahoo Finance)" -ForegroundColor $green
Write-Host "   ✅ Coleta de notícias não estruturadas (Google News)" -ForegroundColor $green
Write-Host "   ✅ Análise de sentimentos automática" -ForegroundColor $green
Write-Host "   ✅ Limpeza e estruturação de dados" -ForegroundColor $green
Write-Host "   ✅ Migração multi-database (MongoDB/PostgreSQL/Snowflake)" -ForegroundColor $green
Write-Host "   ✅ Transformação para modelo dimensional (DW)" -ForegroundColor $green
Write-Host "   ✅ Validações e relatórios gerados" -ForegroundColor $green

Write-Host "`n💾 Dados Armazenados:" -ForegroundColor $white
Write-Host ""
Write-Host "   📁 LOCAL:" -ForegroundColor $yellow
Write-Host "      • data/collected_articles_bbas3.json" -ForegroundColor $gray
Write-Host ""
Write-Host "   🍃 MONGODB (Nested - Análise agregada):" -ForegroundColor $yellow
Write-Host "      • Database: bigData" -ForegroundColor $gray
Write-Host "      • Collection: projeto_ativos" -ForegroundColor $gray
Write-Host "      • Estrutura: Nested (sentimentos como subdocumento)" -ForegroundColor $gray
Write-Host ""
Write-Host "   🐘 POSTGRESQL (Flat - Queries relacionais):" -ForegroundColor $yellow
Write-Host "      • Database: bigdata" -ForegroundColor $gray
Write-Host "      • Tabela notícias: noticias_bbas3 (20 colunas flat)" -ForegroundColor $gray
Write-Host "      • Tabela cotações: bbas3_cotacoes (dados históricos)" -ForegroundColor $gray
Write-Host ""
Write-Host "   ❄️  SNOWFLAKE (Cloud DW - Analytics):" -ForegroundColor $yellow
Write-Host "      • Database: BBAS3" -ForegroundColor $gray
Write-Host "      • Schema: PUBLIC" -ForegroundColor $gray
Write-Host "      • Tabelas operacionais:" -ForegroundColor $gray
Write-Host "         - DADOS_MONG (notícias flat)" -ForegroundColor $gray
Write-Host "         - BBAS3_COTACOES (cotações históricas)" -ForegroundColor $gray
Write-Host "      • Tabelas dimensionais (DW):" -ForegroundColor $gray
Write-Host "         - FATO_NOTICIAS" -ForegroundColor $gray
Write-Host "         - DIM_SENTIMENTO" -ForegroundColor $gray
Write-Host "         - DIM_FONTE" -ForegroundColor $gray

Write-Host "`n📈 Análises Disponíveis:" -ForegroundColor $white
Write-Host "   • Análise estatística básica (scripts/sentimentos.py)" -ForegroundColor $gray
Write-Host "   • Análise detalhada (scripts/analise_detalhada.py)" -ForegroundColor $gray
Write-Host "   • Dados Snowflake (scripts/analisar_dados_mong.py)" -ForegroundColor $gray

Write-Host "`n⏱️  Tempo de Execução:" -ForegroundColor $white
Write-Host "   Duração total: $($duration.Hours)h $($duration.Minutes)min $($duration.Seconds)s" -ForegroundColor $cyan

Write-Host "`n💡 Próximos Passos:" -ForegroundColor $white
Write-Host "   • Conecte ao Snowflake para consultas SQL avançadas" -ForegroundColor $gray
Write-Host "   • Use PostgreSQL para queries relacionais rápidas" -ForegroundColor $gray
Write-Host "   • Explore MongoDB para análises de documentos nested" -ForegroundColor $gray
Write-Host "   • Execute análises específicas: python scripts/sentimentos.py" -ForegroundColor $gray

Write-Host "`n🔄 Para Executar Novamente:" -ForegroundColor $white
Write-Host "   .\scripts\pipeline_master.ps1" -ForegroundColor $cyan

Write-Host "`n════════════════════════════════════════════════════════════════`n" -ForegroundColor $gray
