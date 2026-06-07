"""FastAPI application for PreemptCore."""

from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from preemptcore import __version__
from preemptcore.api.routes_reports import router as reports_router
from preemptcore.api.routes_scans import router as scans_router
from preemptcore.storage.db import create_db_and_tables

app = FastAPI(
    title="PreemptCore API",
    description=(
        "Cryptographic inventory and post-quantum readiness scanner API. "
        "Scans repositories and TLS endpoints, calculates Q-Score, and generates reports."
    ),
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()

app.include_router(scans_router, prefix="/api/scans", tags=["scans"])
app.include_router(reports_router, prefix="/api/reports", tags=["reports"])

@app.get("/api/health", tags=["health"])
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "version": __version__}

# Serve React Dashboard
dashboard_dir = Path(__file__).parent.parent.parent / "dashboard" / "dist"
if dashboard_dir.exists():
    app.mount("/assets", StaticFiles(directory=dashboard_dir / "assets"), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_dashboard(full_path: str):
        # Serve index.html for all non-API paths to support React Router
        if full_path.startswith("api/"):
            # Should not happen because API routes are defined above, but just in case
            return {"error": "API route not found"}
        
        index_path = dashboard_dir / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"error": "Dashboard index.html not found"}
