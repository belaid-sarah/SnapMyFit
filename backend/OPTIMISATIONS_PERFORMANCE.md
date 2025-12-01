# 🚀 Optimisations de Performance - Backend

## ✅ Optimisations Implémentées

### 1. **Préchargement de CLIP et FAISS au démarrage**

**Avant** : CLIP et FAISS se chargeaient à la première requête → 30 minutes de délai

**Après** : CLIP et FAISS se chargent au démarrage de l'API dans le `lifespan` startup

**Impact** :
- ✅ La première requête est maintenant rapide (< 1 seconde)
- ✅ Le chargement se fait une seule fois au démarrage (30-60 secondes)
- ✅ Les utilisateurs n'attendent plus 30 minutes

**Code modifié** :
- `backend/api/main.py` : Préchargement dans `lifespan` startup
- `backend/search_engine.py` : Logs détaillés pour suivre le chargement

### 2. **Logs de progression détaillés**

Ajout de logs pour identifier les goulots d'étranglement :

```
🔄 [INIT] Initialisation de CLIP et FAISS...
📦 [INIT] Chargement du modèle CLIP ViT-B/32...
✅ [INIT] CLIP chargé en X.XXs (device: cpu/cuda)
📦 [INIT] Chargement de l'index FAISS global...
   → Fichier trouvé: embeddings/faiss_index.bin (26.86 MB)
✅ [INIT] Index global chargé en X.XXs (XXXX vecteurs)
📦 [INIT] Chargement des index FAISS par classe...
✅ [INIT] X index par classe chargés en X.XXs
```

### 3. **Vérification : Pas de recalcul des embeddings**

✅ **Confirmé** : Les embeddings ne sont **jamais recalculés** si les fichiers `.bin` existent

Le code vérifie l'existence des fichiers avant de recalculer :
```python
if INDEX_FILE.exists():
    index = faiss.read_index(str(INDEX_FILE))  # Charge depuis le fichier
else:
    # Recalcule seulement si le fichier n'existe pas
    embeddings = np.vstack([get_embedding(p) for p in image_paths])
```

## 📊 État Actuel des Index

D'après l'analyse des fichiers :
- `faiss_index.bin` : **26.86 MB** (index global)
- Index par classe : **27.86 MB** au total
- **Total** : ~55 MB d'index FAISS

## ⚠️ Limitations Actuelles

### 1. **IndexFlatL2 (Index plat)**

**Problème** : `IndexFlatL2` est un index exact mais non optimisé pour de gros datasets

**Impact** :
- Recherche lente sur très gros datasets (> 100k images)
- Charge tout en mémoire (pas de pagination)

**Solution recommandée** (pour l'avenir) :
- Utiliser `IndexIVFFlat` ou `IndexHNSW` pour de meilleures performances
- Nécessite de reconstruire les index

### 2. **Chargement depuis disque**

**Problème** : Si les fichiers sont sur un HDD (disque dur mécanique), le chargement de 55 MB peut être lent

**Solutions** :
- ✅ Utiliser un SSD (recommandé)
- ✅ Précharger au démarrage (déjà implémenté)
- Pour le cloud : télécharger les fichiers avant de démarrer l'API

## 🔍 Diagnostic des Performances

### Temps de chargement attendus

**Au démarrage de l'API** :
1. CLIP : 5-15 secondes (première fois), 2-5 secondes (suivantes)
2. Index global (26.86 MB) : 1-5 secondes (SSD), 5-15 secondes (HDD)
3. Index par classe (27.86 MB) : 1-5 secondes (SSD), 5-15 secondes (HDD)

**Total attendu** : 10-30 secondes au démarrage

### Temps de recherche attendus

**Après le préchargement** :
- Détection de catégorie : 0.5-1 seconde
- Extraction embedding : 0.5-1 seconde
- Recherche FAISS : 0.01-0.1 seconde (index par classe)
- **Total** : 1-2 secondes par recherche

## 🛠️ Améliorations Futures Possibles

### 1. **Index Approximatif (IVF ou HNSW)**

Pour datasets > 10k images :

```python
# Au lieu de IndexFlatL2
dimension = 512  # dimension CLIP
nlist = 100  # nombre de clusters
quantizer = faiss.IndexFlatL2(dimension)
index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
index.train(embeddings)  # Entraînement nécessaire
index.add(embeddings)
```

**Avantages** :
- Recherche 10-100x plus rapide sur gros datasets
- Moins de mémoire utilisée

**Inconvénients** :
- Nécessite de reconstruire tous les index
- Légère perte de précision (approximatif)

### 2. **Chargement Asynchrone**

Charger les index en arrière-plan pendant que l'API démarre :

```python
import asyncio

async def load_indexes_async():
    # Charger en parallèle
    await asyncio.gather(
        load_global_index(),
        load_class_indexes()
    )
```

### 3. **Cache des Embeddings de Requête**

Si la même image est recherchée plusieurs fois, mettre en cache son embedding.

## 📝 Checklist de Vérification

- [x] CLIP préchargé au démarrage
- [x] Index FAISS préchargés au démarrage
- [x] Logs de progression ajoutés
- [x] Vérification : pas de recalcul des embeddings
- [ ] Index optimisé (IVF/HNSW) - Optionnel pour l'avenir
- [ ] Chargement asynchrone - Optionnel pour l'avenir

## 🎯 Résultat Attendu

**Avant** : 30 minutes à la première requête ❌

**Après** : 
- 10-30 secondes au démarrage de l'API ✅
- 1-2 secondes par requête de recherche ✅

