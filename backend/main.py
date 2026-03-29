"""
FastAPI backend — wraps existing ML inference, demo state, and simulation modules.
In production, also serves the built React frontend as static files.
"""

import sys
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Make project root and backend dir importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from routers import state, inference, monitor

app = FastAPI(title="ML Anomaly Detection API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(state.router, prefix="/api/state", tags=["state"])
app.include_router(inference.router, prefix="/api/inference", tags=["inference"])
app.include_router(monitor.router, prefix="/api/monitor", tags=["monitor"])


@app.get("/api/health")
def health():
    return {"status": "ok"}


# Serve built React frontend in production
FRONTEND_DIR = PROJECT_ROOT / "frontend" / "dist"
print(f"[startup] PROJECT_ROOT={PROJECT_ROOT}")
print(f"[startup] FRONTEND_DIR={FRONTEND_DIR} exists={FRONTEND_DIR.is_dir()}")
if FRONTEND_DIR.is_dir():
    print(f"[startup] Frontend files: {os.listdir(FRONTEND_DIR)}")

    # Mount /assets as static files for JS/CSS bundles
    assets_dir = FRONTEND_DIR / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
        print(f"[startup] Mounted /assets -> {assets_dir}")

    # SPA catch-all: serve index.html for all non-API, non-asset routes
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = FRONTEND_DIR / full_path
        if full_path and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(FRONTEND_DIR / "index.html"))
else:
    print(f"[startup] WARNING: Frontend dist not found at {FRONTEND_DIR}")
