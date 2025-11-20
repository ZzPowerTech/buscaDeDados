<#
Simple runner for Windows PowerShell. Assumes venv has been created.
Usage:
  .\run.ps1
#>

try {
    .\venv\Scripts\Activate.ps1
} catch {
    Write-Host "Erro ao ativar venv. Execute .\setup_env.ps1 primeiro." -ForegroundColor Yellow
}

python collect_news_bbas3.py
