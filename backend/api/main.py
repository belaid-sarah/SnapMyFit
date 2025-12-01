from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path
import tempfile
import shutil
import time
import uuid

import search_engine

# Initialisation au démarrage : CLIP et FAISS se chargent immédiatement
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Précharger CLIP et FAISS pour éviter le délai à la première requête
    print("🚀 [STARTUP] Démarrage de l'API...")
    print("⏳ [STARTUP] Préchargement de CLIP et FAISS en arrière-plan...")
    import time
    import threading
    
    startup_start = time.time()
    
    # Précharger CLIP et FAISS dans un thread pour ne pas bloquer le démarrage
    def init_in_background():
        try:
            search_engine.initialize()
            startup_elapsed = time.time() - startup_start
            print(f"✅ [STARTUP] Modèle CLIP et index FAISS prêts en {startup_elapsed:.2f}s")
        except Exception as e:
            startup_elapsed = time.time() - startup_start
            print(f"⚠️ [STARTUP] Erreur lors de l'initialisation après {startup_elapsed:.2f}s: {e}")
            print(f"⚠️ [STARTUP] L'initialisation se fera à la première requête")
    
    # Démarrer l'initialisation en arrière-plan (daemon=True pour ne pas bloquer l'arrêt)
    init_thread = threading.Thread(target=init_in_background, daemon=True)
    init_thread.start()
    
    # Attendre 2 secondes pour voir si CLIP charge rapidement
    time.sleep(2)
    
    print(f"🌐 [STARTUP] API prête sur http://localhost:8000")
    print(f"   → L'initialisation complète se fait en arrière-plan (peut prendre 1-2 minutes)")
    print(f"   → Les premières requêtes peuvent être lentes jusqu'à ce que FAISS soit chargé")
    
    yield
    # Shutdown (optionnel)
    print("🛑 [SHUTDOWN] Arrêt de l'API")

app = FastAPI(title="SnapMyFit API", lifespan=lifespan)

# Ajouter CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dossiers de stockage
images_path = Path(__file__).resolve().parents[1] / "images"
results_path = Path(__file__).resolve().parents[1] / "results"
uploads_path = Path(__file__).resolve().parents[1] / "uploads"

# Créer les dossiers s'ils n'existent pas
results_path.mkdir(exist_ok=True)
uploads_path.mkdir(exist_ok=True)

# Servir le dossier images pour l'affichage côté frontend
app.mount("/images", StaticFiles(directory=str(images_path)), name="images")
# Servir le dossier results pour les résultats de recherche
app.mount("/results", StaticFiles(directory=str(results_path)), name="results")

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
        
        # Sauvegarder les résultats dans un dossier dédié
        search_id = uuid.uuid4().hex
        result_folder = results_path / search_id
        result_folder.mkdir(exist_ok=True)
        
        # Copier l'image uploadée dans uploads/ et les résultats dans results/
        uploaded_filename = f"{search_id}{suffix}"
        uploaded_path = uploads_path / uploaded_filename
        shutil.copy2(temp_path, uploaded_path)
        print(f"💾 [API] Image uploadée sauvegardée: {uploaded_path}")
        
        # Copier les images de résultats
        saved_results = []
        for p in results:
            p_path = Path(p)
            result_filename = p_path.name
            result_dest = result_folder / result_filename
            shutil.copy2(p, result_dest)
            saved_results.append(str(result_dest))
            print(f"💾 [API] Résultat copié: {result_dest}")
        
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
        
        print(f"✅ [API] Recherche {search_id} sauvegardée avec {len(saved_results)} résultats")
        return JSONResponse({
            "type": predicted_type,
            "searchId": search_id,
            "results": items
        })
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except Exception:
            pass
