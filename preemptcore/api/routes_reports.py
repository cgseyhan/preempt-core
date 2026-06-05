"""Report API routes — stub for future implementation."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/{scan_id}")
async def get_report(scan_id: str) -> dict[str, str]:
    """Placeholder — report retrieval to be implemented with storage layer."""
    return {"scan_id": scan_id, "status": "not_implemented"}
