# search_engine.py
import os
import torch
import faiss
import clip
from PIL import Image
import numpy as np
from pathlib import Path
import json

# ⚡ Évite les conflits OpenMP sur Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
faiss.omp_set_num_threads(1)

device = "cuda" if torch.cuda.is_available() else "cpu"

# Variables globales
model = None
preprocess = None
index = None
image_paths = None
image_labels = None  # labels pour chaque image (robe, jupe...)
class_to_indices = None  # map: type -> list[int]
class_to_index = None  # map: type -> FAISS Index (par classe)
image_metadata = None  # infos ref/brand/prix par image (optionnel)

# Types de vêtements possibles
TYPES = ["robe", "jupe", "t-shirt", "pantalon", "short", "veste", "chemise"]

def initialize():
    global model, preprocess, index, image_paths, image_labels, class_to_indices, image_metadata, class_to_index
    import time

    if model is not None:
        return  # déjà initialisé

    init_start = time.time()
    print("🔄 [INIT] Initialisation de CLIP et FAISS...")
    
    # Charger CLIP
    print("📦 [INIT] Chargement du modèle CLIP ViT-B/32...")
    clip_start = time.time()
    model, preprocess = clip.load("ViT-B/32", device=device)
    clip_elapsed = time.time() - clip_start
    print(f"✅ [INIT] CLIP chargé en {clip_elapsed:.2f}s (device: {device})")

    # Charger les images de référence
    IMG_DIR = "images"
    img_dir = Path(IMG_DIR)
    image_paths = []
    # Charger toutes les images de la racine images/
    if img_dir.exists():
        print(f"📂 [INIT] Scan du dossier images/...")
        for f in img_dir.iterdir():
            if f.is_file() and f.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
                image_paths.append(str(f))
        image_paths = sorted(set(image_paths))
        print(f"   → {len(image_paths)} images trouvées")
    else:
        print(f"⚠️ [INIT] Dossier images/ non trouvé")

    # Fichiers de cache
    INDEX_FILE = Path("embeddings/faiss_index.bin")
    PATHS_FILE = Path("metadata/image_paths.json")
    LABELS_FILE = Path("metadata/image_labels.json")
    META_FILE = Path("metadata/image_metadata.json")

    # Charger chemins des images (ordre stable) si existant
    print(f"📄 [INIT] Chargement des métadonnées...")
    if PATHS_FILE.exists():
        with open(PATHS_FILE, "r") as f:
            image_paths = json.load(f)
        print(f"   → {len(image_paths)} chemins chargés depuis {PATHS_FILE}")
    else:
        image_paths = sorted(image_paths)
        with open(PATHS_FILE, "w") as f:
            json.dump(image_paths, f)
        print(f"   → {len(image_paths)} chemins sauvegardés dans {PATHS_FILE}")

    # Charger labels depuis JSON (format: {"images\\file.jpg": "robe", ...})
    if LABELS_FILE.exists():
        print(f"   → Chargement des labels depuis {LABELS_FILE}...")
        import sys
        sys.stdout.flush()
        with open(LABELS_FILE, "r", encoding="utf-8") as f:
            raw_labels = json.load(f)
        print(f"   → {len(raw_labels)} labels chargés")
        sys.stdout.flush()
        # Normaliser les chemins (Windows backslash -> forward slash pour compatibilité)
        print(f"   → Mapping des labels aux chemins... (13752 labels, cela peut prendre 10-30 secondes)")
        import sys
        sys.stdout.flush()
        
        # Optimisation: créer un index des noms de fichiers pour recherche rapide
        image_labels = {}
        path_by_name = {Path(p).name: p for p in image_paths}
        path_by_posix = {Path(p).as_posix(): p for p in image_paths}
        
        mapped_count = 0
        total_labels = len(raw_labels)
        for idx, (k, v) in enumerate(raw_labels.items()):
            # Afficher progression tous les 1000 labels
            if idx % 1000 == 0 and idx > 0:
                print(f"   → Progression: {idx}/{total_labels} labels traités...")
                sys.stdout.flush()
            
            # Normaliser le chemin
            normalized = str(Path(k)).replace("\\", "/")
            normalized_posix = Path(normalized).as_posix()
            file_name = Path(k).name
            
            # Chercher d'abord par chemin complet, puis par nom de fichier
            if normalized_posix in path_by_posix:
                image_labels[path_by_posix[normalized_posix]] = v
                mapped_count += 1
            elif file_name in path_by_name:
                image_labels[path_by_name[file_name]] = v
                mapped_count += 1
            elif Path(k).exists():
                image_labels[k] = v
                mapped_count += 1
        
        print(f"   → {mapped_count} labels mappés aux chemins")
        sys.stdout.flush()
    else:
        print(f"   ⚠️ Fichier {LABELS_FILE} non trouvé, aucun label chargé")
        image_labels = {}

    # Charger métadonnées optionnelles
    if META_FILE.exists():
        print(f"   → Chargement des métadonnées depuis {META_FILE}...")
        with open(META_FILE, "r", encoding="utf-8") as f:
            image_metadata = json.load(f)
        print(f"   → {len(image_metadata)} métadonnées chargées")
    else:
        print(f"   ⚠️ Fichier {META_FILE} non trouvé, métadonnées vides")
        image_metadata = {}

    # Construire ou charger l'index FAISS global
    print("📦 [INIT] Chargement de l'index FAISS global...")
    faiss_start = time.time()
    if INDEX_FILE.exists():
        index_size_mb = INDEX_FILE.stat().st_size / (1024 * 1024)
        print(f"   → Fichier trouvé: {INDEX_FILE} ({index_size_mb:.2f} MB)")
        print(f"   → Début du chargement FAISS... (cela peut prendre 10-60 secondes sur HDD)")
        print(f"   → Si ça prend trop de temps, vérifiez votre antivirus ou le type de disque")
        
        # Afficher un message toutes les 10 secondes pour montrer que ça progresse
        import sys
        sys.stdout.flush()
        
        try:
            # Charger l'index FAISS (peut être lent sur HDD ou si antivirus scanne)
            print(f"   → Lecture du fichier en cours... (patientez)")
            sys.stdout.flush()
            
            # Essayer de charger avec un indicateur de progression
            index = faiss.read_index(str(INDEX_FILE))
            faiss_elapsed = time.time() - faiss_start
            print(f"✅ [INIT] Index global chargé en {faiss_elapsed:.2f}s ({index.ntotal} vecteurs)")
            sys.stdout.flush()
        except Exception as e:
            faiss_elapsed = time.time() - faiss_start
            print(f"❌ [INIT] Erreur lors du chargement de l'index après {faiss_elapsed:.2f}s: {e}")
            print(f"   → Tentative de reconstruction...")
            # Reconstruire l'index si le fichier est corrompu
            if image_paths and len(image_paths) > 0:
                print(f"   → Reconstruction depuis {len(image_paths)} images (cela peut prendre plusieurs minutes)...")
                embeddings = np.vstack([get_embedding(p) for p in image_paths]).astype("float32")
                dimension = embeddings.shape[1]
                index = faiss.IndexFlatL2(dimension)
                index.add(embeddings)
                faiss.write_index(index, str(INDEX_FILE))
                print(f"✅ [INIT] Index reconstruit et sauvegardé")
            else:
                print(f"⚠️ [INIT] Pas d'images disponibles, index non créé")
                index = None
    else:
        print(f"⚠️ [INIT] Index global non trouvé, construction depuis les images...")
        print(f"   → Cela peut prendre du temps pour {len(image_paths)} images...")
        embeddings = np.vstack([get_embedding(p) for p in image_paths]).astype("float32")
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        faiss.write_index(index, str(INDEX_FILE))
        faiss_elapsed = time.time() - faiss_start
        print(f"✅ [INIT] Index global construit et sauvegardé en {faiss_elapsed:.2f}s")

    # Construire ou charger des index FAISS par classe (si dataset organisé ou labels déjà partiels)
    class_to_indices = {t: [] for t in TYPES}
    for i, p in enumerate(image_paths):
        t = image_labels.get(p)
        if t in class_to_indices:
            class_to_indices[t].append(i)

    # Charger les index par classe
    print("📦 [INIT] Chargement des index FAISS par classe...")
    import sys
    sys.stdout.flush()
    class_start = time.time()
    class_to_index = {}
    loaded_classes = []
    for t in TYPES:
        indices = class_to_indices.get(t, [])
        if not indices:
            continue
        idx_path = Path(f"embeddings/faiss_index_{t}.bin")
        if idx_path.exists():
            idx_size_mb = idx_path.stat().st_size / (1024 * 1024)
            print(f"   → Chargement de l'index '{t}' ({idx_size_mb:.2f} MB)...")
            sys.stdout.flush()
            try:
                class_to_index[t] = faiss.read_index(str(idx_path))
                loaded_classes.append(f"{t} ({len(indices)} images, {idx_size_mb:.2f} MB)")
                print(f"   ✅ Index '{t}' chargé")
                sys.stdout.flush()
            except Exception as e:
                print(f"   ⚠️ Erreur lors du chargement de l'index '{t}': {e}")
                print(f"   → L'index sera reconstruit à la prochaine recherche")
                sys.stdout.flush()
        else:
            # Reconstituer les vecteurs à partir de l'index global
            print(f"   → Construction de l'index pour '{t}' ({len(indices)} images)...")
            xb = np.vstack([index.reconstruct(i) for i in indices]).astype("float32")
            sub_index = faiss.IndexFlatL2(xb.shape[1])
            sub_index.add(xb)
            faiss.write_index(sub_index, str(idx_path))
            class_to_index[t] = sub_index
            loaded_classes.append(f"{t} ({len(indices)} images, construit)")
    
    class_elapsed = time.time() - class_start
    if loaded_classes:
        print(f"✅ [INIT] {len(loaded_classes)} index par classe chargés en {class_elapsed:.2f}s")
        for cls_info in loaded_classes:
            print(f"   → {cls_info}")
    else:
        print(f"⚠️ [INIT] Aucun index par classe disponible")

    total_elapsed = time.time() - init_start
    print(f"✅ [INIT] Initialisation complète en {total_elapsed:.2f}s")
    print(f"📊 [INIT] Index prêt avec {len(image_paths)} images au total.")

def get_embedding(image_path: str) -> np.ndarray:
    global model, preprocess
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    with torch.no_grad():
        emb = model.encode_image(image)
    return emb.cpu().numpy()

# Cache pour les text_features (ne changent jamais, calculés une seule fois)
_text_features_cache = None

def get_type_of_image(image_path: str) -> str:
    """
    Utilise CLIP pour prédire le type de vêtement.
    Retourne un des TYPES.
    Optimisé: cache les text_features qui ne changent jamais.
    """
    global model, preprocess, _text_features_cache
    
    # Calculer text_features une seule fois et les mettre en cache
    if _text_features_cache is None:
        text_tokens = clip.tokenize(TYPES).to(device)
        with torch.no_grad():
            _text_features_cache = model.encode_text(text_tokens)
            _text_features_cache /= _text_features_cache.norm(dim=-1, keepdim=True)
    
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)

    with torch.no_grad():
        image_features = model.encode_image(image)
        image_features /= image_features.norm(dim=-1, keepdim=True)

        # Similarité cosinus (text_features déjà normalisés)
        similarity = (image_features @ _text_features_cache.T).cpu().numpy()
        idx = similarity.argmax()
        return TYPES[idx]

def search_image(query_img: str, k: int = 5):
    """
    Recherche d'images similaires. Retourne (results, predicted_type) pour éviter les appels redondants.
    """
    global index, image_paths, image_labels, class_to_indices, class_to_index
    import time
    
    # Vérifier que l'initialisation a été faite (normalement au démarrage)
    if index is None:
        print("⚠️ [SEARCH] Index non initialisé, initialisation en cours...")
        initialize()  # fallback si pas initialisé au démarrage

    search_start = time.time()
    
    # 1️⃣ Détecter le type du vêtement uploadé (une seule fois)
    print(f"\n🔍 [SEARCH] Détection de la catégorie pour: {Path(query_img).name}")
    type_start = time.time()
    query_type = get_type_of_image(query_img)
    type_elapsed = time.time() - type_start
    print(f"✅ [SEARCH] Catégorie détectée: {query_type} ({type_elapsed:.2f}s)")

    # 2️⃣ Extraire l'embedding de la requête (une seule fois)
    emb_start = time.time()
    query_emb = get_embedding(query_img)
    emb_elapsed = time.time() - emb_start
    print(f"📊 [SEARCH] Embedding extrait ({emb_elapsed:.2f}s)")

    # 3️⃣ Filtrer candidats par type AVANT la recherche si possible
    candidate_indices = class_to_indices.get(query_type, [])
    print(f"📊 [SEARCH] Nombre d'images dans la catégorie '{query_type}': {len(candidate_indices)}")

    # Utiliser l'index par classe si disponible (le plus rapide)
    cls_index = class_to_index.get(query_type)
    if cls_index is not None and candidate_indices:
        print(f"⚡ [SEARCH] Recherche RAPIDE: index FAISS spécifique à '{query_type}'")
        print(f"   → Recherche dans {len(candidate_indices)} images au lieu de {len(image_paths)} totales")
        faiss_start = time.time()
        D, I = cls_index.search(query_emb, min(k, len(candidate_indices)))
        faiss_elapsed = time.time() - faiss_start
        selected = [image_paths[candidate_indices[i]] for i in I[0]]
        total_elapsed = time.time() - search_start
        print(f"✅ [SEARCH] {len(selected)} résultats trouvés en {total_elapsed:.2f}s (FAISS: {faiss_elapsed:.3f}s)")
        return selected, query_type

    # 4️⃣ Fallback: recherche globale puis filtrage paresseux
    print(f"⚠️ [SEARCH] Index par classe non disponible, fallback: recherche globale")
    faiss_start = time.time()
    D, I = index.search(query_emb, min(50, len(image_paths)))  # top-50 pour limiter le coût
    faiss_elapsed = time.time() - faiss_start
    top_candidates = [image_paths[i] for i in I[0]]
    
    # Filtrer par catégorie
    updated = False
    filtered = []
    for p in top_candidates:
        lbl = image_labels.get(p)
        if not lbl:
            lbl = get_type_of_image(p)
            image_labels[p] = lbl
            updated = True
        if lbl == query_type:
            filtered.append(p)
        if len(filtered) >= k:
            break

    if updated:
        with open("metadata/image_labels.json", "w", encoding="utf-8") as f:
            json.dump(image_labels, f)

    result = filtered[:k] if filtered else top_candidates[:k]
    total_elapsed = time.time() - search_start
    print(f"✅ [SEARCH] {len(result)} résultats trouvés en {total_elapsed:.2f}s (FAISS: {faiss_elapsed:.3f}s)")
    return result, query_type

def get_metadata_for_image(image_path: str) -> dict:
    """Retourne des métadonnées optionnelles pour une image (ref, brand, price, etc.)."""
    global image_metadata
    # Essayer plusieurs variantes de chemin
    path_variants = [
        image_path,
        str(Path(image_path)),
        str(Path(image_path).as_posix()),
        f"images\\{Path(image_path).name}",
        f"images/{Path(image_path).name}",
    ]
    for variant in path_variants:
        if image_metadata and variant in image_metadata:
            return image_metadata[variant]
    # fallback: générer une ref basée sur le nom de fichier si pas de metadata
    img_name = Path(image_path).stem
    return {"ref": f"REF-{img_name}", "name": img_name}
