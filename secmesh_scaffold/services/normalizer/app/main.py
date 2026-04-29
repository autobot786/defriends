from __future__ import annotations

from fastapi import FastAPI
from app.api import router

app = FastAPI(title="SecMesh Normalizer", version="0.1.0")
app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "normalizer"}
