<#
PowerShell helper to create a virtual environment and install dependencies.
Usage (PowerShell):
  .\setup_env.ps1
#>

$ErrorActionPreference = 'Stop'

python -m venv .\venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

# newspaper3k may require the NLTK 'punkt' tokenizer on Windows
python -c "import nltk; nltk.download('punkt')"

Write-Host "Ambiente pronto. Ative o venv com: .\venv\Scripts\Activate.ps1 e execute o script principal." -ForegroundColor Green
