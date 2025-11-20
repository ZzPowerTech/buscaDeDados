# Configuração de Variáveis de Ambiente
# Copie este arquivo para config_local.ps1 e ajuste suas credenciais

# ===============================
# MONGODB
# ===============================
$env:MONGO_URI="mongodb://localhost:27017/"
$env:MONGO_DB="bigData"
$env:MONGO_COLLECTION="projeto_ativos"

# ===============================
# POSTGRESQL
# ===============================
$env:PG_USER="postgres"
$env:PG_PASSWORD="sua_senha_aqui"
$env:PG_HOST="localhost"
$env:PG_PORT="5432"
$env:PG_DB="bigdata"

# ===============================
# SNOWFLAKE
# ===============================
$env:SF_USER="SEU_USUARIO"
$env:SF_PASSWORD="SUA_SENHA"
$env:SF_ACCOUNT="SUA_CONTA"  # Exemplo: RYQPYZE-FW60752
$env:SF_WAREHOUSE="COMPUTE_WH"
$env:SF_DATABASE="BBAS3"
$env:SF_SCHEMA="PUBLIC"

Write-Host "✅ Variáveis de ambiente configuradas!" -ForegroundColor Green
Write-Host ""
Write-Host "Para usar, execute:" -ForegroundColor Cyan
Write-Host "  . .\config_local.ps1" -ForegroundColor White
Write-Host "  python collect_news_bbas3.py" -ForegroundColor White
