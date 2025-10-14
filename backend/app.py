# app.py
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import uuid
from search_engine import search_image

app = FastAPI()

# ⚡ Dossiers de stockage
UPLOAD_DIR = Path("uploads")
RESULTS_DIR = Path("results")
UPLOAD_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# Endpoint test
@app.get("/")
def root():
    return {"message": "SnapMyFit API is running!"}

# Endpoint upload
@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    # 1️⃣ Sauvegarder l'image uploadée
    ext = Path(file.filename).suffix
    unique_name = f"{uuid.uuid4().hex}{ext}"
    upload_path = UPLOAD_DIR / unique_name
    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2️⃣ Chercher les images similaires filtrées par type
    results = search_image(str(upload_path), k=5)

    # 3️⃣ Copier les résultats dans un dossier dédié
    result_folder = RESULTS_DIR / Path(unique_name).stem
    result_folder.mkdir(exist_ok=True)
    for r in results:
        shutil.copy(r, result_folder / Path(r).name)

    # 4️⃣ Retourner le JSON
    return JSONResponse({
        "uploaded_image": str(upload_path),
        "similar_images": [str(result_folder / Path(r).name) for r in results]
    })

