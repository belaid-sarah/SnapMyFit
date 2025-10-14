import os
import torch
import faiss
import clip
import numpy as np
from PIL import Image

# ===== 1. Charger CLIP =====
device = "cuda" if torch.cuda.is_available() else "cpu"
print("✅ Device:", device)
model, preprocess = clip.load("ViT-B/32", device=device)
print("✅ Modèle CLIP chargé")

# ===== 2. Dossier d'images =====
IMG_DIR = "images/"  # mets ton chemin
image_paths = [os.path.join(IMG_DIR, f) for f in os.listdir(IMG_DIR) if f.endswith(".jpg")]

if not image_paths:
    raise ValueError("⚠️ Aucun fichier .jpg trouvé dans dataset/images/")

# ===== 3. Extraire embeddings =====
def get_embedding(image_path):
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    with torch.no_grad():
        embedding = model.encode_image(image)
    return embedding.cpu().numpy()

embeddings = []
for img_path in image_paths:
    embeddings.append(get_embedding(img_path))

embeddings = np.vstack(embeddings).astype("float32")
print(f"✅ {len(embeddings)} embeddings extraits, dimension: {embeddings.shape[1]}")

# ===== 4. Construire FAISS =====
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)
print("✅ Index FAISS construit")

# ===== 5. Recherche par image =====
def search(query_img, k=3):
    query_emb = get_embedding(query_img)
    D, I = index.search(query_emb, k)  # distances, indices
    results = [image_paths[i] for i in I[0]]
    return results

# Exemple : prendre la première image comme requête
query = image_paths[0]
print(f"\n🔎 Recherche pour: {query}")
results = search(query)

print("📌 Résultats similaires:")
for r in results:
    print(" -", r)
