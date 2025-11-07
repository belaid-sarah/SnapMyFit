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

    if model is not None:
        return  # déjà initialisé

    print("🔄 Initialisation de CLIP et FAISS...")
    # Charger CLIP
    model, preprocess = clip.load("ViT-B/32", device=device)

    # Charger les images de référence
    IMG_DIR = "images"
    img_dir = Path(IMG_DIR)
    image_paths = []
    # Charger toutes les images de la racine images/
    if img_dir.exists():
        for f in img_dir.iterdir():
            if f.is_file() and f.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
                image_paths.append(str(f))
    image_paths = sorted(set(image_paths))

    # Fichiers de cache
    INDEX_FILE = Path("faiss_index.bin")
    PATHS_FILE = Path("image_paths.json")
    LABELS_FILE = Path("image_labels.json")
    META_FILE = Path("image_metadata.json")

    # Charger chemins des images (ordre stable) si existant
    if PATHS_FILE.exists():
        with open(PATHS_FILE, "r") as f:
            image_paths = json.load(f)
    else:
        image_paths = sorted(image_paths)
        with open(PATHS_FILE, "w") as f:
            json.dump(image_paths, f)

    # Charger labels depuis JSON (format: {"images\\file.jpg": "robe", ...})
    if LABELS_FILE.exists():
        with open(LABELS_FILE, "r", encoding="utf-8") as f:
            raw_labels = json.load(f)
            # Normaliser les chemins (Windows backslash -> forward slash pour compatibilité)
            image_labels = {}
            for k, v in raw_labels.items():
                # Normaliser le chemin pour correspondre aux image_paths
                normalized = str(Path(k)).replace("\\", "/")
                # Chercher le chemin correspondant dans image_paths
                for p in image_paths:
                    if Path(p).as_posix() == Path(normalized).as_posix() or str(Path(p).name) == Path(k).name:
                        image_labels[p] = v
                        break
                else:
                    # Si pas trouvé, essayer avec le chemin original
                    if Path(k).exists():
                        image_labels[k] = v
    else:
        image_labels = {}

    # Charger métadonnées optionnelles
    if META_FILE.exists():
        with open(META_FILE, "r", encoding="utf-8") as f:
            image_metadata = json.load(f)
    else:
        image_metadata = {}

    # Construire ou charger l'index FAISS global
    if INDEX_FILE.exists():
        index = faiss.read_index(str(INDEX_FILE))
    else:
        embeddings = np.vstack([get_embedding(p) for p in image_paths]).astype("float32")
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        faiss.write_index(index, str(INDEX_FILE))

    # Construire ou charger des index FAISS par classe (si dataset organisé ou labels déjà partiels)
    class_to_indices = {t: [] for t in TYPES}
    for i, p in enumerate(image_paths):
        t = image_labels.get(p)
        if t in class_to_indices:
            class_to_indices[t].append(i)

    class_to_index = {}
    for t in TYPES:
        indices = class_to_indices.get(t, [])
        if not indices:
            continue
        idx_path = Path(f"faiss_index_{t}.bin")
        if idx_path.exists():
            class_to_index[t] = faiss.read_index(str(idx_path))
        else:
            # Reconstituer les vecteurs à partir de l'index global
            xb = np.vstack([index.reconstruct(i) for i in indices]).astype("float32")
            sub_index = faiss.IndexFlatL2(xb.shape[1])
            sub_index.add(xb)
            faiss.write_index(sub_index, str(idx_path))
            class_to_index[t] = sub_index

    print(f"✅ Index prêt avec {len(image_paths)} images.")

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
    
    if index is None:
        initialize()  # initialise seulement au premier appel

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
        with open("image_labels.json", "w", encoding="utf-8") as f:
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
