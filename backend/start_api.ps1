# Script PowerShell pour démarrer l'API
Write-Host "🚀 Démarrage de l'API SnapMyFit..." -ForegroundColor Green
Set-Location $PSScriptRoot
Write-Host "📍 Répertoire: $(Get-Location)" -ForegroundColor Cyan
Write-Host "🌐 L'API sera accessible sur: http://localhost:8000" -ForegroundColor Yellow
Write-Host "⏳ Chargement de CLIP (cela peut prendre 30-60 secondes la première fois)..." -ForegroundColor Yellow
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

