# 🔧 Solution : ERR_CONNECTION_REFUSED

## Problème
Le backend n'accepte pas les connexions car :
1. Il est encore en train de charger (CLIP + FAISS)
2. Il écoute sur `127.0.0.1` au lieu de `0.0.0.0`

## Solution immédiate

### 1. Attendre que le backend finisse de charger

Dans votre terminal, attendez de voir ce message :
```
✅ [STARTUP] Modèle CLIP et index FAISS prêts en XX.XXs
🌐 [STARTUP] API prête sur http://localhost:8000
INFO:     Application startup complete.
```

**Ne pas** essayer de se connecter avant ce message !

### 2. Redémarrer le backend avec la bonne configuration

1. **Arrêter le backend actuel** :
   - Appuyez sur `Ctrl+C` dans le terminal où le backend tourne

2. **Redémarrer avec le script mis à jour** :
   ```powershell
   cd backend
   .\start_api.ps1
   ```

Le script utilise maintenant `--host 0.0.0.0` qui accepte les connexions depuis `localhost` et `127.0.0.1`.

### 3. Vérifier que le backend est prêt

Une fois que vous voyez `Application startup complete`, testez dans votre navigateur :
- `http://localhost:8000/` → Devrait afficher `{"status":"ok","message":"SnapMyFit API running 🚀"}`

### 4. Tester depuis le frontend

Une fois le backend prêt, le frontend devrait pouvoir se connecter.

## Temps de chargement attendu

- **CLIP** : 2-5 secondes ✅ (déjà chargé)
- **Index FAISS global** (26.86 MB) : 5-15 secondes
- **Index par classe** (27.86 MB) : 5-15 secondes
- **Total** : 15-35 secondes après le chargement de CLIP

## Vérification

Si après avoir attendu le message de démarrage complet, vous avez encore `ERR_CONNECTION_REFUSED` :

1. Vérifier que le port 8000 n'est pas utilisé par un autre processus
2. Vérifier le firewall Windows
3. Essayer `http://127.0.0.1:8000/` au lieu de `http://localhost:8000/`

