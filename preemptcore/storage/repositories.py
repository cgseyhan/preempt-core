"""Storage repositories for database operations."""

from sqlmodel import Session, select

from preemptcore.core.models import ScanResult
from preemptcore.storage.models_db import DBScanResult


class ScanRepository:
    """Repository for managing ScanResult records in the database."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save_scan(self, scan_result: ScanResult) -> None:
        """Save a new scan result to the database."""
        db_scan = DBScanResult.from_domain(scan_result)
        self.session.add(db_scan)
        self.session.commit()
        # Optionally refresh or just rely on commit

    def get_all_scans(self) -> list[ScanResult]:
        """Retrieve all scan results from the database."""
        statement = select(DBScanResult).order_by(DBScanResult.created_at.desc()) # type: ignore
        results = self.session.exec(statement).all()
        return [r.to_domain() for r in results]

    def get_scan(self, scan_id: str) -> ScanResult | None:
        """Retrieve a specific scan by ID."""
        db_scan = self.session.get(DBScanResult, scan_id)
        if not db_scan:
            return None
        return db_scan.to_domain()
