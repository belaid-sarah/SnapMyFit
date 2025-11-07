from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path
import tempfile
import shutil
import time

import search_engine

# Initialisation lazy : CLIP se charge à la première requête (plus rapide au démarrage)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: API démarre immédiatement, CLIP se chargera à la première requête
    print("🚀 [STARTUP] API démarrée - CLIP se chargera à la première requête")
    yield
    # Shutdown (optionnel)
    print("🛑 [SHUTDOWN] Arrêt de l'API")

app = FastAPI(title="SnapMyFit API", lifespan=lifespan)

# Ajouter CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir le dossier images pour l'affichage côté frontend
images_path = Path(__file__).resolve().parents[1] / "images"
app.mount("/images", StaticFiles(directory=str(images_path)), name="images")

@app.get("/")
def root():
    return {"status": "ok", "message": "SnapMyFit API running 🚀"}

@app.post("/search")
async def search(file: UploadFile = File(...)):
    # Sauvegarder le fichier uploadé en temp
    suffix = Path(file.filename).suffix or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        temp_path = Path(tmp.name)
        shutil.copyfileobj(file.file, tmp)

    try:
        start_time = time.time()
        print(f"\n📤 [API] Image uploadée: {file.filename}")
        
        # search_image retourne maintenant (results, predicted_type) pour éviter le double appel
        search_result = search_engine.search_image(str(temp_path), k=5)
        if isinstance(search_result, tuple):
            results, predicted_type = search_result
        else:
            # Fallback pour compatibilité
            results = search_result
            predicted_type = search_engine.get_type_of_image(str(temp_path))
        
        elapsed = time.time() - start_time
        print(f"⚡ [API] Recherche terminée en {elapsed:.2f}s")
        print(f"📋 [API] Catégorie: {predicted_type}, {len(results)} résultats")
        base_url_prefix = "/images/"
        items = []
        for p in results:
            p_path = Path(p)
            # Construire l'URL pour servir l'image
            if p_path.parent == images_path or p_path.parent.name == "images":
                url = f"{base_url_prefix}{p_path.name}"
            else:
                url = f"{base_url_prefix}{p_path.name}"
            
            # Récupérer les métadonnées (inclut la référence)
            meta = search_engine.get_metadata_for_image(str(p))
            img_type = search_engine.image_labels.get(str(p)) or search_engine.image_labels.get(p_path.name)
            
            items.append({
                "imageUrl": url,
                "path": str(p_path.name),
                "type": img_type,
                "ref": meta.get("ref", f"REF-{p_path.stem}"),
                "name": meta.get("name", p_path.stem),
                "category": meta.get("category", img_type),
                "brand": meta.get("brand", "Unknown"),
                "price": meta.get("price"),
                "meta": meta  # Garder pour compatibilité
            })
        return JSONResponse({
            "type": predicted_type,
            "results": items
        })
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except Exception:
            pass
