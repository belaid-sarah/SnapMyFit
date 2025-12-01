# Infrastructure Docker pour SnapMyFit

Ce dossier contient les fichiers Docker pour déployer SnapMyFit localement ou sur le cloud.

## Structure

- `Dockerfile.backend` - Image Docker pour l'API backend (FastAPI + CLIP + FAISS)
- `Dockerfile.frontend` - Image Docker pour le frontend (React + Vite + Nginx)
- `docker-compose.yml` - Orchestration complète avec tous les services
- `DEPLOYMENT_GCP.md` - Guide de déploiement sur Google Cloud Platform

## Démarrage Rapide

### Prérequis
- Docker Desktop installé
- Docker Compose v2

### Lancer l'application

```bash
# Depuis la racine du projet
cd infra
docker-compose up -d
```

L'application sera accessible sur :
- **Frontend** : http://localhost
- **Backend API** : http://localhost:8000
- **MinIO Console** : http://localhost:9001 (minio/minio123)
- **PostgreSQL** : localhost:5432
- **Redis** : localhost:6379

### Arrêter l'application

```bash
docker-compose down
```

### Voir les logs

```bash
# Tous les services
docker-compose logs -f

# Un service spécifique
docker-compose logs -f backend
```

## Services Inclus

1. **backend** - API FastAPI avec CLIP/FAISS pour la recherche d'images
2. **frontend** - Interface React servie par Nginx
3. **db** - PostgreSQL pour la base de données
4. **redis** - Cache Redis
5. **minio** - Stockage d'objets compatible S3 (pour migration vers GCP)

## Volumes

Les volumes suivants sont montés pour persister les données :

- `db_data` - Données PostgreSQL
- `minio_data` - Données MinIO
- `../backend/images` - Images de référence (montage direct)
- `../backend/results` - Résultats de recherche (montage direct)
- `../backend/uploads` - Images uploadées (montage direct)

## Build des Images

### Build manuel

```bash
# Backend
docker build -f infra/Dockerfile.backend -t snapmyfit-backend:latest .

# Frontend
docker build -f infra/Dockerfile.frontend -t snapmyfit-frontend:latest .
```

## Configuration

### Variables d'Environnement

Modifiez `docker-compose.yml` pour changer :
- Ports exposés
- Mots de passe de base de données
- Configuration MinIO
- Variables d'environnement des services

### CORS

Si vous accédez au frontend depuis une URL différente, mettez à jour les origines CORS dans `backend/api/main.py`.

## Dépannage

### Le backend ne démarre pas

1. Vérifiez les logs : `docker-compose logs backend`
2. Vérifiez que les dossiers `images/`, `results/`, `uploads/` existent
3. Vérifiez que les fichiers d'index FAISS sont présents

### Le frontend ne se connecte pas à l'API

1. Vérifiez que `VITE_API_BASE` est correctement configuré
2. Vérifiez les logs du backend pour les erreurs CORS
3. Vérifiez que le backend est accessible sur le port 8000

### Problèmes de permissions

Sur Linux/Mac, vous pourriez avoir besoin de :
```bash
sudo chown -R $USER:$USER ../backend/images
sudo chown -R $USER:$USER ../backend/results
```

## Production

Pour la production, consultez `DEPLOYMENT_GCP.md` pour le déploiement sur Google Cloud Platform.

**Important** : Ne pas utiliser ce docker-compose en production sans :
- Changer les mots de passe par défaut
- Configurer HTTPS
- Utiliser des secrets managés
- Configurer des backups réguliers


