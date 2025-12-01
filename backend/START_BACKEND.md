# 🚀 Guide de démarrage du Backend

## 📋 Prérequis

- Python 3.11 ou supérieur
- pip (gestionnaire de paquets Python)

## 🔧 Installation des dépendances

### 1. Installer les dépendances de base

```powershell
cd backend
pip install -r requirements.txt
```

**Note importante** : L'installation de PyTorch et CLIP peut prendre plusieurs minutes.

### 2. Installation alternative (si problème avec requirements.txt)

Si vous rencontrez des problèmes, installez les dépendances séparément :

```powershell
# Dépendances FastAPI
pip install fastapi uvicorn[standard] sqlalchemy psycopg2-binary redis pydantic python-multipart Pillow numpy

# PyTorch (CPU version)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# FAISS et CLIP
pip install faiss-cpu
pip install git+https://github.com/openai/CLIP.git
```

## 🚀 Démarrage du backend

### Option 1 : Script PowerShell (Recommandé)

```powershell
cd backend
.\start_api.ps1
```

### Option 2 : Script Batch (Windows)

```cmd
cd backend
start_api.bat
```

### Option 3 : Commande directe

```powershell
cd backend
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

## ⏳ Temps de chargement

- **Première fois** : 30-60 secondes (téléchargement et chargement de CLIP)
- **Suivantes** : 5-10 secondes (modèle déjà en cache)

## ✅ Vérification

Une fois démarré, vous devriez voir :

```
🚀 [STARTUP] API démarrée - CLIP se chargera à la première requête
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

## 🌐 Test dans le navigateur

Ouvrez : `http://localhost:8000/`

Vous devriez voir :
```json
{"status":"ok","message":"SnapMyFit API running 🚀"}
```

## 📁 Structure des dossiers

Assurez-vous que ces dossiers existent :
- `backend/images/` - Images de référence pour la recherche
- `backend/embeddings/` - Index FAISS (.bin)
- `backend/metadata/` - Fichiers JSON (image_labels.json, image_metadata.json, image_paths.json)
- `backend/uploads/` - Images uploadées (créé automatiquement)
- `backend/results/` - Résultats de recherche (créé automatiquement)

## ⚠️ Problèmes courants

### 1. Port déjà utilisé

**Erreur** : `Address already in use`

**Solution** :
```powershell
# Trouver le processus utilisant le port 8000
netstat -ano | findstr :8000

# Tuer le processus (remplacer PID par le numéro trouvé)
taskkill /PID <PID> /F
```

### 2. Module non trouvé

**Erreur** : `ModuleNotFoundError: No module named 'xxx'`

**Solution** :
```powershell
# Vérifier que vous êtes dans le bon répertoire
cd backend

# Réinstaller les dépendances
pip install -r requirements.txt
```

### 3. CLIP ne se charge pas

**Erreur** : Erreur lors du chargement de CLIP

**Solution** :
- Vérifier votre connexion Internet (CLIP télécharge le modèle la première fois)
- Vérifier que PyTorch est bien installé : `python -c "import torch; print(torch.__version__)"`

### 4. Erreur FAISS

**Erreur** : Problème avec FAISS

**Solution** :
```powershell
# Réinstaller FAISS
pip uninstall faiss-cpu
pip install faiss-cpu
```

## 🔍 Endpoints disponibles

- `GET /` - Vérification de l'état de l'API
- `POST /search` - Recherche d'images similaires
  - Body: `multipart/form-data` avec un fichier image
  - Response: JSON avec les résultats de recherche

## 📝 Notes

- Le backend utilise le mode "lazy loading" : CLIP se charge à la première requête de recherche
- Les index FAISS sont chargés depuis `embeddings/`
- Les métadonnées sont chargées depuis `metadata/`
- CORS est configuré pour accepter les requêtes depuis `http://localhost:5173` (frontend Vite)

