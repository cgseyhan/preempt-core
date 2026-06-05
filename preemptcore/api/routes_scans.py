"""Scan API routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from preemptcore.core.models import ScanResult
from preemptcore.core.scoring import calculate_score

router = APIRouter()


class RepoScanRequest(BaseModel):
    path: str


class EndpointScanRequest(BaseModel):
    host: str


@router.post("/repo", response_model=ScanResult)
async def scan_repo(req: RepoScanRequest) -> ScanResult:
    """Scan a local repository path."""
    from preemptcore.scanners.repo_scanner import RepoScanner

    p = Path(req.path)
    if not p.exists():
        raise HTTPException(status_code=404, detail=f"Path not found: {req.path}")

    scanner = RepoScanner()
    result = scanner.scan(p)
    breakdown = calculate_score(result)
    result.q_score = breakdown.final_score
    result.readiness_label = breakdown.readiness_label
    return result


@router.post("/endpoint", response_model=ScanResult)
async def scan_endpoint(req: EndpointScanRequest) -> ScanResult:
    """Scan a TLS endpoint."""
    from preemptcore.scanners.endpoint_scanner import EndpointScanner

    scanner = EndpointScanner()
    result = scanner.scan(req.host)
    breakdown = calculate_score(result)
    result.q_score = breakdown.final_score
    result.readiness_label = breakdown.readiness_label
    return result
