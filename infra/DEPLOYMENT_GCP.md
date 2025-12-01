# Guide de Déploiement sur Google Cloud Platform (GCP)

Ce document explique comment déployer SnapMyFit sur GCP avec Docker et Cloud Storage pour les images.

## Architecture Recommandée sur GCP

### Services GCP à utiliser :
1. **Cloud Run** - Pour le backend et frontend (serverless, auto-scaling)
2. **Cloud SQL (PostgreSQL)** - Base de données
3. **Cloud Memorystore (Redis)** - Cache
4. **Cloud Storage** - Stockage des images (remplace MinIO)
5. **Artifact Registry** - Pour stocker les images Docker

## Étapes de Déploiement

### 1. Préparation des Images Docker

#### Build et Push vers Artifact Registry

```bash
# Configurer gcloud
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Créer un Artifact Registry
gcloud artifacts repositories create snapmyfit-repo \
    --repository-format=docker \
    --location=europe-west1

# Configurer Docker pour utiliser gcloud
gcloud auth configure-docker europe-west1-docker.pkg.dev

# Build et push du backend
cd infra
docker build -f Dockerfile.backend -t europe-west1-docker.pkg.dev/YOUR_PROJECT_ID/snapmyfit-repo/backend:latest ..
docker push europe-west1-docker.pkg.dev/YOUR_PROJECT_ID/snapmyfit-repo/backend:latest

# Build et push du frontend
docker build -f Dockerfile.frontend -t europe-west1-docker.pkg.dev/YOUR_PROJECT_ID/snapmyfit-repo/frontend:latest ..
docker push europe-west1-docker.pkg.dev/YOUR_PROJECT_ID/snapmyfit-repo/frontend:latest
```

### 2. Créer Cloud SQL (PostgreSQL)

```bash
gcloud sql instances create snapmyfit-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=europe-west1 \
    --root-password=YOUR_DB_PASSWORD

gcloud sql databases create snapdb --instance=snapmyfit-db
```

### 3. Créer Cloud Memorystore (Redis)

```bash
gcloud redis instances create snapmyfit-redis \
    --size=1 \
    --region=europe-west1 \
    --redis-version=redis_7_0
```

### 4. Créer Cloud Storage Bucket

```bash
# Créer un bucket pour les images
gsutil mb -p YOUR_PROJECT_ID -l europe-west1 gs://snapmyfit-images

# Créer un bucket pour les résultats de recherche
gsutil mb -p YOUR_PROJECT_ID -l europe-west1 gs://snapmyfit-results

# Configurer les permissions (optionnel)
gsutil iam ch allUsers:objectViewer gs://snapmyfit-images
```

### 5. Déployer sur Cloud Run

#### Backend

```bash
gcloud run deploy snapmyfit-backend \
    --image europe-west1-docker.pkg.dev/YOUR_PROJECT_ID/snapmyfit-repo/backend:latest \
    --platform managed \
    --region europe-west1 \
    --allow-unauthenticated \
    --set-env-vars="DATABASE_URL=postgresql://snap:YOUR_PASSWORD@/snapdb?host=/cloudsql/YOUR_PROJECT_ID:europe-west1:snapmyfit-db" \
    --set-env-vars="REDIS_URL=redis://YOUR_REDIS_IP:6379" \
    --set-env-vars="GCS_BUCKET_IMAGES=snapmyfit-images" \
    --set-env-vars="GCS_BUCKET_RESULTS=snapmyfit-results" \
    --add-cloudsql-instances YOUR_PROJECT_ID:europe-west1:snapmyfit-db \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300
```

#### Frontend

```bash
gcloud run deploy snapmyfit-frontend \
    --image europe-west1-docker.pkg.dev/YOUR_PROJECT_ID/snapmyfit-repo/frontend:latest \
    --platform managed \
    --region europe-west1 \
    --allow-unauthenticated \
    --set-env-vars="VITE_API_BASE=https://snapmyfit-backend-XXXXX-ew.a.run.app"
```

## Migration vers Cloud Storage

Pour utiliser Cloud Storage au lieu du système de fichiers local, vous devez modifier le code backend :

### Installation de la bibliothèque GCS

Ajoutez dans `backend/api/requirements.txt` :
```
google-cloud-storage
```

### Exemple de code pour Cloud Storage

```python
from google.cloud import storage
import os

# Initialiser le client GCS
storage_client = storage.Client()
images_bucket = storage_client.bucket(os.getenv("GCS_BUCKET_IMAGES", "snapmyfit-images"))
results_bucket = storage_client.bucket(os.getenv("GCS_BUCKET_RESULTS", "snapmyfit-results"))

def save_to_gcs(file_path: Path, bucket, destination_name: str):
    """Sauvegarder un fichier dans Cloud Storage"""
    blob = bucket.blob(destination_name)
    blob.upload_from_filename(str(file_path))
    return blob.public_url

def get_gcs_url(bucket_name: str, object_name: str):
    """Obtenir l'URL publique d'un objet dans GCS"""
    return f"https://storage.googleapis.com/{bucket_name}/{object_name}"
```

## Configuration des Variables d'Environnement

### Backend
- `DATABASE_URL` - URL de connexion Cloud SQL
- `REDIS_URL` - URL de connexion Redis
- `GCS_BUCKET_IMAGES` - Nom du bucket pour les images
- `GCS_BUCKET_RESULTS` - Nom du bucket pour les résultats
- `GOOGLE_APPLICATION_CREDENTIALS` - Chemin vers le fichier de credentials (si nécessaire)

### Frontend
- `VITE_API_BASE` - URL de base de l'API backend

## Coûts Estimés (approximatifs)

- **Cloud Run** : ~$0.40 par million de requêtes + $0.0000025 par GB-seconde
- **Cloud SQL** : ~$7-10/mois pour db-f1-micro
- **Cloud Memorystore** : ~$30/mois pour 1GB
- **Cloud Storage** : ~$0.020 par GB/mois
- **Artifact Registry** : Gratuit jusqu'à 0.5 GB, puis $0.10/GB/mois

## Notes Importantes

1. **Volumes Docker** : Cloud Run ne supporte pas les volumes persistants. Utilisez Cloud Storage pour le stockage.

2. **Index FAISS** : Les fichiers d'index FAISS doivent être soit :
   - Inclus dans l'image Docker (recommandé pour les petits index)
   - Stockés dans Cloud Storage et téléchargés au démarrage

3. **CORS** : Mettez à jour les origines CORS dans `backend/api/main.py` avec les URLs Cloud Run.

4. **Secrets** : Utilisez Secret Manager pour stocker les mots de passe et clés API.

## Alternative : Google Kubernetes Engine (GKE)

Pour un déploiement plus complexe avec contrôle total, vous pouvez utiliser GKE :

```bash
# Créer un cluster GKE
gcloud container clusters create snapmyfit-cluster \
    --num-nodes=2 \
    --zone=europe-west1-b

# Déployer avec kubectl
kubectl apply -f k8s/
```

## Support

Pour plus d'informations :
- [Documentation Cloud Run](https://cloud.google.com/run/docs)
- [Documentation Cloud Storage](https://cloud.google.com/storage/docs)
- [Documentation Cloud SQL](https://cloud.google.com/sql/docs)


