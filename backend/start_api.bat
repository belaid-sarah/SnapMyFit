@echo off
echo 🚀 Démarrage de l'API SnapMyFit...
cd /d %~dp0
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
pause

