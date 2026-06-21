"""Report API routes for generating HTML/PDF reports."""

import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlmodel import Session

from preemptcore.reports.html_report import write_html_report
from preemptcore.reports.pdf_report import write_pdf_report
from preemptcore.storage.db import get_session
from preemptcore.storage.repositories import ScanRepository

router = APIRouter()


@router.get("/{scan_id}/html")
async def get_html_report(scan_id: str, session: Session = Depends(get_session)) -> FileResponse:
    """Generate and return an HTML report for a given scan."""
    repo = ScanRepository(session)
    scan_result = repo.get_scan(scan_id)
    if not scan_result:
        raise HTTPException(status_code=404, detail="Scan not found")

    tmp_dir = Path(tempfile.mkdtemp())
    try:
        html_path = write_html_report(scan_result, tmp_dir)
        # Using FileResponse will send the file, we can't delete the tmp_dir immediately.
        # For MVP, we can leave the temp file or let OS clean it up in /tmp.
        return FileResponse(html_path, media_type="text/html", filename=f"report_{scan_id}.html")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate HTML report: {e}")


@router.get("/{scan_id}/pdf")
async def get_pdf_report(
    scan_id: str,
    custom_css: str | None = None,
    session: Session = Depends(get_session)
) -> FileResponse:
    """Generate and return a PDF report for a given scan (White-label support via custom_css)."""
    repo = ScanRepository(session)
    scan_result = repo.get_scan(scan_id)
    if not scan_result:
        raise HTTPException(status_code=404, detail="Scan not found")

    tmp_dir = Path(tempfile.mkdtemp())
    try:
        pdf_path = write_pdf_report(scan_result, tmp_dir, custom_css=custom_css)
        return FileResponse(pdf_path, media_type="application/pdf", filename=f"report_{scan_id}.pdf")
    except ImportError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {e}")
