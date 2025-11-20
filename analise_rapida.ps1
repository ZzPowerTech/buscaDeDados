# Script rápido para análises apenas (sem recoletar dados)
# Usa os dados já coletados em collected_articles_bbas3.json

$ErrorActionPreference = 'Continue'

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ANÁLISE RÁPIDA - DADOS EXISTENTES" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Verificar se arquivo JSON existe
if (-Not (Test-Path ".\collected_articles_bbas3.json")) {
    Write-Host "❌ Arquivo collected_articles_bbas3.json não encontrado." -ForegroundColor Red
    Write-Host "   Execute .\pipeline_completo.ps1 primeiro para coletar dados.`n" -ForegroundColor Yellow
    exit 1
}

# Verificar se venv existe
if (-Not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "⚠️  Ambiente virtual não encontrado. Execute .\setup_env.ps1 primeiro." -ForegroundColor Yellow
    exit 1
}

# Ativar venv
Write-Host "🔧 Ativando ambiente virtual..." -ForegroundColor Blue
.\venv\Scripts\Activate.ps1

# Verificar dados no MongoDB (opcional)
Write-Host "`n🗄️  [1/3] Verificando MongoDB..." -ForegroundColor Green
python verify_mongo_data.py

# Análise básica
Write-Host "`n📊 [2/3] Análise Estatística Básica..." -ForegroundColor Green
python sentimentos.py

# Análise detalhada
Write-Host "`n📊 [3/3] Análise Detalhada..." -ForegroundColor Green
python analise_detalhada.py

# Resumo
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ✅ ANÁLISES CONCLUÍDAS!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan
