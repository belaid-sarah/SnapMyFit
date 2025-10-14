from fastapi import FastAPI

app = FastAPI(title="SnapMyFit API")

@app.get("/")
def root():
    return {"status": "ok", "message": "SnapMyFit API running 🚀"}
