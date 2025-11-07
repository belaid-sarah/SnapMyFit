# 🚀 Guide de démarrage de l'API

## Démarrage de l'API

### Option 1 : Script PowerShell (Recommandé)
```powershell
cd C:\Users\MPS£\Desktop\snapFit\backend
.\start_api.ps1
```

### Option 2 : Commande directe
```powershell
cd C:\Users\MPS£\Desktop\snapFit\backend
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

## ⏳ Temps de chargement

**Première fois** : 30-60 secondes (téléchargement et chargement de CLIP)
**Suivantes** : 5-10 secondes (modèle déjà en cache)

## ✅ Vérification

Une fois démarrée, tu devrais voir :
```
🚀 [STARTUP] Préchargement de CLIP et FAISS...
✅ [STARTUP] Modèle prêt en X.XXs
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

## 🌐 Test dans le navigateur

Ouvre : `http://localhost:8000/`

Tu devrais voir :
```json
{"status":"ok","message":"SnapMyFit API running 🚀"}
```

## ⚠️ Problèmes courants

1. **Port déjà utilisé** : Tuer le processus avec `Get-Process | Where-Object {$_.Id -eq 34656} | Stop-Process`
2. **CLIP en cours de chargement** : Attendre 30-60 secondes
3. **Module non trouvé** : Vérifier que tu es dans le bon répertoire (`backend/`)

## 🔧 Dépannage

Si l'API ne démarre pas :
1. Vérifier que Python est installé : `python --version`
2. Vérifier les dépendances : `pip install -r api/requirements.txt`
3. Vérifier le répertoire : `cd backend` (doit être dans `snapFit/backend/`)

