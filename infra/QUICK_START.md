# Guide de Démarrage Rapide - SnapMyFit avec Docker

## ✅ Vérification de la Configuration

Avant de lancer les conteneurs, vérifiez que vous avez :

1. ✅ **Docker Desktop** installé et en cours d'exécution
2. ✅ Les dossiers suivants existent dans `backend/` :
   - `images/` - Contient les images de référence pour la recherche
   - `results/` - Sera créé automatiquement pour stocker les résultats
   - `uploads/` - Sera créé automatiquement pour stocker les images uploadées
3. ✅ Les fichiers d'index FAISS sont présents (optionnel, seront créés au premier lancement si absents)

## 🚀 Démarrage

### Option 1 : Démarrage Simple

```bash
cd infra
docker-compose up -d
```

### Option 2 : Démarrage avec Logs

```bash
cd infra
docker-compose up
```

### Option 3 : Rebuild des Images

Si vous avez modifié le code :

```bash
cd infra
docker-compose up --build -d
```

## 📍 Accès aux Services

Une fois démarré, accédez à :

- **Frontend** : http://localhost
- **Backend API** : http://localhost:8000
- **API Docs (Swagger)** : http://localhost:8000/docs
- **MinIO Console** : http://localhost:9001
  - Username: `minio`
  - Password: `minio123`
- **PostgreSQL** : `localhost:5432`
  - User: `snap`
  - Password: `snap`
  - Database: `snapdb`
- **Redis** : `localhost:6379`

## 🔍 Vérification du Statut

```bash
# Voir les conteneurs en cours d'exécution
docker-compose ps

# Voir les logs
docker-compose logs -f

# Voir les logs d'un service spécifique
docker-compose logs -f backend
```

## 🛑 Arrêt

```bash
# Arrêter les conteneurs
docker-compose down

# Arrêter et supprimer les volumes (⚠️ supprime les données)
docker-compose down -v
```

## 🐛 Dépannage

### Le backend ne démarre pas

1. Vérifiez les logs : `docker-compose logs backend`
2. Vérifiez que le dossier `backend/images/` contient des images
3. Vérifiez que les fichiers d'index FAISS existent ou peuvent être créés

### Le frontend ne se connecte pas à l'API

1. Vérifiez que le backend est accessible : http://localhost:8000
2. Vérifiez les logs du backend pour les erreurs CORS
3. Vérifiez la variable d'environnement `VITE_API_BASE` dans le frontend

### Erreurs de permissions

Sur Linux/Mac :
```bash
sudo chown -R $USER:$USER ../backend/images
sudo chown -R $USER:$USER ../backend/results
```

### Rebuild complet

Si vous avez des problèmes persistants :
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## 📝 Notes Importantes

1. **Premier démarrage** : Le backend peut prendre quelques minutes pour :
   - Télécharger le modèle CLIP
   - Construire les index FAISS (si absents)

2. **Stockage des résultats** : Chaque recherche sauvegarde automatiquement :
   - L'image uploadée dans `backend/uploads/`
   - Les résultats dans `backend/results/{searchId}/`

3. **Volumes** : Les données sont persistées dans des volumes Docker :
   - Base de données PostgreSQL
   - Données MinIO
   - Les dossiers `images/`, `results/`, `uploads/` sont montés directement

## 🔄 Mise à Jour

Pour mettre à jour après des changements de code :

```bash
cd infra
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 📊 Monitoring

Pour surveiller l'utilisation des ressources :

```bash
# Utilisation des ressources
docker stats

# Espace disque utilisé
docker system df
```


