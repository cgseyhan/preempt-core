"""FastAPI application for PreemptCore."""

from fastapi import FastAPI

from preemptcore import __version__
from preemptcore.api.routes_reports import router as reports_router
from preemptcore.api.routes_scans import router as scans_router

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

app.include_router(scans_router, prefix="/scans", tags=["scans"])
app.include_router(reports_router, prefix="/reports", tags=["reports"])


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "version": __version__}
