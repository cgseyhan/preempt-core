"""SQLModel database models for PreemptCore storage."""

import json
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from preemptcore.core.models import (
    Finding,
    FindingSeverity,
    QuantumRelevance,
    ScanResult,
    ScanTarget,
)


class DBScanTarget(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    scan_id: str = Field(foreign_key="dbscanresult.scan_id")
    target_type: str
    value: str

    scan: Optional["DBScanResult"] = Relationship(back_populates="targets")


class DBFinding(SQLModel, table=True):
    db_id: int | None = Field(default=None, primary_key=True)
    finding_id: str
    scan_id: str = Field(foreign_key="dbscanresult.scan_id")
    
    title: str
    description: str
    severity: str
    quantum_relevance: str
    file_path: str | None = None
    line_number: int | None = None
    evidence: str | None = None
    algorithm: str | None = None
    category: str
    recommendation: str
    references_json: str = "[]"

    scan: Optional["DBScanResult"] = Relationship(back_populates="findings")


class DBScanResult(SQLModel, table=True):
    scan_id: str = Field(primary_key=True)
    project_name: str
    created_at: datetime
    q_score: int
    readiness_label: str
    client_name: str | None = Field(default=None)

    targets: list[DBScanTarget] = Relationship(back_populates="scan", cascade_delete=True)
    findings: list[DBFinding] = Relationship(back_populates="scan", cascade_delete=True)

    @classmethod
    def from_domain(cls, result: ScanResult) -> "DBScanResult":
        db_scan = cls(
            scan_id=result.scan_id,
            project_name=result.project_name,
            created_at=result.created_at,
            q_score=result.q_score,
            readiness_label=result.readiness_label,
            client_name=result.client_name,
        )
        for t in result.targets:
            db_scan.targets.append(DBScanTarget(target_type=t.target_type, value=t.value))
        
        for f in result.findings:
            db_scan.findings.append(DBFinding(
                finding_id=f.id,
                title=f.title,
                description=f.description,
                severity=f.severity.value,
                quantum_relevance=f.quantum_relevance.value,
                file_path=f.file_path,
                line_number=f.line_number,
                evidence=f.evidence,
                algorithm=f.algorithm,
                category=f.category,
                recommendation=f.recommendation,
                references_json=json.dumps(f.references)
            ))
        return db_scan

    def to_domain(self) -> ScanResult:
        domain_targets = [
            ScanTarget(target_type=t.target_type, value=t.value)
            for t in self.targets
        ]
        domain_findings = []
        for f in self.findings:
            refs = json.loads(f.references_json)
            domain_findings.append(Finding(
                id=f.finding_id,
                title=f.title,
                description=f.description,
                severity=FindingSeverity(f.severity),
                quantum_relevance=QuantumRelevance(f.quantum_relevance),
                file_path=f.file_path,
                line_number=f.line_number,
                evidence=f.evidence,
                algorithm=f.algorithm,
                category=f.category,
                recommendation=f.recommendation,
                references=refs
            ))
        
        return ScanResult(
            scan_id=self.scan_id,
            project_name=self.project_name,
            created_at=self.created_at,
            targets=domain_targets,
            findings=domain_findings,
            q_score=self.q_score,
            readiness_label=self.readiness_label,
            client_name=self.client_name,
        )


class DBSchedule(SQLModel, table=True):
    schedule_id: str = Field(primary_key=True)
    target_type: str
    target_value: str
    cron_expression: str
    client_name: str | None = None
    created_at: datetime
    is_active: bool = True
