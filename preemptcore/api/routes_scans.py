"""Scan API routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from preemptcore.core.models import ScanResult
from preemptcore.core.scoring import calculate_score
from preemptcore.storage.db import get_session
from preemptcore.storage.repositories import ScanRepository

router = APIRouter()


class RepoScanRequest(BaseModel):
    path: str
    client_name: str | None = None


class EndpointScanRequest(BaseModel):
    host: str
    client_name: str | None = None


@router.post("/repo", response_model=ScanResult)
async def scan_repo(
    req: RepoScanRequest,
    session: Session = Depends(get_session)
) -> ScanResult:
    """Scan a local repository path and save results."""
    from preemptcore.scanners.repo_scanner import RepoScanner

    p = Path(req.path)
    if not p.exists():
        raise HTTPException(status_code=404, detail=f"Path not found: {req.path}")

    scanner = RepoScanner()
    result = scanner.scan(p)
    breakdown = calculate_score(result)
    result.q_score = breakdown.final_score
    result.readiness_label = breakdown.readiness_label
    result.client_name = req.client_name

    repo = ScanRepository(session)
    repo.save_scan(result)
    return result


@router.post("/endpoint", response_model=ScanResult)
async def scan_endpoint(
    req: EndpointScanRequest,
    session: Session = Depends(get_session)
) -> ScanResult:
    """Scan a TLS endpoint and save results."""
    from preemptcore.scanners.endpoint_scanner import EndpointScanner

    scanner = EndpointScanner()
    result = scanner.scan(req.host)
    breakdown = calculate_score(result)
    result.q_score = breakdown.final_score
    result.readiness_label = breakdown.readiness_label
    result.client_name = req.client_name

    repo = ScanRepository(session)
    repo.save_scan(result)
    return result


@router.get("", response_model=list[ScanResult])
async def list_scans(
    client_name: str | None = None,
    session: Session = Depends(get_session)
) -> list[ScanResult]:
    """Retrieve history of all scans, optionally filtered by client."""
    from sqlmodel import select

    from preemptcore.storage.models_db import DBScanResult
    
    statement = select(DBScanResult).order_by(DBScanResult.created_at.desc()) # type: ignore
    if client_name:
        statement = statement.where(DBScanResult.client_name == client_name)
        
    results = session.exec(statement).all()
    return [r.to_domain() for r in results]


@router.get("/{scan_id}", response_model=ScanResult)
async def get_scan(scan_id: str, session: Session = Depends(get_session)) -> ScanResult:
    """Retrieve a specific scan by ID."""
    repo = ScanRepository(session)
    result = repo.get_scan(scan_id)
    if not result:
        raise HTTPException(status_code=404, detail="Scan not found")
    return result
