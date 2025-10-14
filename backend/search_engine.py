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

# Types de vêtements possibles
TYPES = ["robe", "jupe", "t-shirt", "pantalon", "short", "veste", "chemise"]

def initialize():
    global model, preprocess, index, image_paths, image_labels

    if model is not None:
        return  # déjà initialisé

    print("🔄 Initialisation de CLIP et FAISS...")
    # Charger CLIP
    model, preprocess = clip.load("ViT-B/32", device=device)

    # Charger les images de référence
    IMG_DIR = "images"
    image_paths = [str(Path(IMG_DIR) / f) for f in os.listdir(IMG_DIR) if f.lower().endswith(".jpg")]

    # Charger ou générer les labels
    LABELS_FILE = Path("image_labels.json")
    if LABELS_FILE.exists():
        with open(LABELS_FILE, "r") as f:
            image_labels = json.load(f)
    else:
        # Si pas de fichier, on prédit avec CLIP et on sauvegarde
        image_labels = {}
        for img_path in image_paths:
            image_labels[img_path] = get_type_of_image(img_path)
        with open(LABELS_FILE, "w") as f:
            json.dump(image_labels, f)
    
    # Extraire embeddings
    embeddings = np.vstack([get_embedding(p) for p in image_paths]).astype("float32")

    # Construire index FAISS
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    print(f"✅ Index prêt avec {len(image_paths)} images.")

def get_embedding(image_path: str) -> np.ndarray:
    global model, preprocess
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    with torch.no_grad():
        emb = model.encode_image(image)
    return emb.cpu().numpy()

def get_type_of_image(image_path: str) -> str:
    """
    Utilise CLIP pour prédire le type de vêtement.
    Retourne un des TYPES.
    """
    global model, preprocess
    text_tokens = clip.tokenize(TYPES).to(device)
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)

    with torch.no_grad():
        image_features = model.encode_image(image)
        text_features = model.encode_text(text_tokens)

        # Normaliser
        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)

        # Similarité cosinus
        similarity = (image_features @ text_features.T).cpu().numpy()
        idx = similarity.argmax()
        return TYPES[idx]

def search_image(query_img: str, k: int = 5):
    global index, image_paths, image_labels
    if index is None:
        initialize()  # initialise seulement au premier appel

    # 1️⃣ Détecter le type du vêtement uploadé
    query_type = get_type_of_image(query_img)

    # 2️⃣ Chercher les images similaires avec FAISS
    query_emb = get_embedding(query_img)
    D, I = index.search(query_emb, k*10)  # prend plus pour filtrer

    # 3️⃣ Filtrer les résultats par type
    filtered = [image_paths[i] for i in I[0] if image_labels.get(image_paths[i]) == query_type]

    return filtered[:k]
