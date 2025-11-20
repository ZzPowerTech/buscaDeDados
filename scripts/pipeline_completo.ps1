# Script automático para coleta e análise de notícias BBAS3
# Executa: coleta -> verificação MongoDB -> análises de sentimentos

$ErrorActionPreference = 'Continue'

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  PIPELINE AUTOMÁTICO - BBAS3/BB NEWS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Verificar se venv existe
if (-Not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "⚠️  Ambiente virtual não encontrado. Execute .\setup_env.ps1 primeiro." -ForegroundColor Yellow
    exit 1
}

# Ativar venv
Write-Host "🔧 Ativando ambiente virtual..." -ForegroundColor Blue
.\venv\Scripts\Activate.ps1

# Passo 1: Testar conexão MongoDB
Write-Host "`n📡 [1/4] Testando conexão com MongoDB..." -ForegroundColor Green
python testConnection.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro na conexão com MongoDB. Verifique se o MongoDB está rodando." -ForegroundColor Red
    exit 1
}

# Passo 2: Coletar notícias
Write-Host "`n📰 [2/4] Coletando notícias (15-30 min)..." -ForegroundColor Green
Write-Host "   → Salvando automaticamente em MongoDB, PostgreSQL e Snowflake" -ForegroundColor Gray
python collect_news_bbas3.py
$endTime = Get-Date
$duration = $endTime - $startTime

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro durante a coleta de notícias." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Coleta concluída em $($duration.Minutes) minutos e $($duration.Seconds) segundos" -ForegroundColor Green
Write-Host "   ✅ Dados salvos em MongoDB" -ForegroundColor Gray
Write-Host "   ✅ Dados salvos em PostgreSQL (dados_mong)" -ForegroundColor Gray
Write-Host "   ✅ Dados salvos em Snowflake (DADOS_MONG)" -ForegroundColor Gray

# Passo 3: Verificar dados no MongoDB
Write-Host "`n🗄️  [3/4] Verificando dados inseridos no MongoDB..." -ForegroundColor Green
python verify_mongo_data.py

# Passo 4: Executar análises
Write-Host "`n📊 [4/4] Executando análises de sentimentos..." -ForegroundColor Green

Write-Host "`n--- Análise Estatística Básica ---" -ForegroundColor Yellow
python sentimentos.py

Write-Host "`n`n--- Análise Detalhada ---" -ForegroundColor Yellow
python analise_detalhada.py

# Resumo final
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ✅ PIPELINE CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n📁 Arquivos gerados:" -ForegroundColor White
Write-Host "   • collected_articles_bbas3.json (arquivo local)" -ForegroundColor Gray
Write-Host "   • MongoDB: bigData.projeto_ativos (banco de dados)" -ForegroundColor Gray

Write-Host "`n⏱️  Tempo total de execução: $($duration.Minutes) min $($duration.seconds) seg" -ForegroundColor White

Write-Host "`n💡 Dica: Para executar novamente:" -ForegroundColor Cyan
Write-Host "   .\pipeline_completo.ps1`n" -ForegroundColor White
