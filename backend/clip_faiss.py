import os
import shutil
from pathlib import Path
import torch
import faiss
import clip
from PIL import Image
import numpy as np

# =========================
# 0. Préparation
# =========================
# ✅ Évite les conflits OpenMP sur Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
faiss.omp_set_num_threads(1)

# =========================
# 1. Charger le modèle CLIP
# =========================
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)
print(f"✅ Device utilisé : {device}")
print("✅ Modèle CLIP chargé")

# =========================
# 2. Charger les images de référence
# =========================
IMG_DIR = "images"  # dossier qui contient tes images de base
image_paths = [str(Path(IMG_DIR) / f) for f in os.listdir(IMG_DIR) if f.lower().endswith(".jpg")]
print(f"✅ {len(image_paths)} images trouvées dans {IMG_DIR}")

# =========================
# 3. Extraire les embeddings CLIP
# =========================
def get_embedding(image_path: str) -> np.ndarray:
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    with torch.no_grad():
        emb = model.encode_image(image)
    return emb.cpu().numpy()

embeddings = [get_embedding(p) for p in image_paths]
embeddings = np.vstack(embeddings).astype("float32")
print(f"✅ Embeddings extraits : {embeddings.shape[0]} images, dimension {embeddings.shape[1]}")

# =========================
# 4. Construire l'index FAISS
# =========================
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)  # Similarité Euclidienne
index.add(embeddings)
print("✅ Index FAISS construit")

# =========================
# 5. Fonction de recherche
# =========================
def search(query_img: str, k: int = 5):
    query_emb = get_embedding(query_img)
    D, I = index.search(query_emb, k)
    return [image_paths[i] for i in I[0]]

# =========================
# 6. Test avec une image
# =========================
query = "test.jpg"  # ⚡ mets ici le chemin de l'image requête
results = search(query, k=5)

print(f"\n🔎 Résultats similaires pour {query} :")
for r in results:
    print("   ", r)

# =========================
# 7. Sauvegarde des résultats
# =========================
query_name = Path(query).stem
save_dir = Path("results") / query_name
save_dir.mkdir(parents=True, exist_ok=True)

for r in results:
    shutil.copy(r, save_dir / Path(r).name)

print(f"\n✅ {len(results)} images copiées dans : {save_dir.resolve()}")
