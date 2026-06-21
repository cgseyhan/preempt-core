"""Core Pydantic data models for PreemptCore."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class FindingSeverity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class QuantumRelevance(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Finding(BaseModel):
    """A single cryptographic finding discovered during a scan."""

    id: str
    title: str
    description: str
    severity: FindingSeverity
    quantum_relevance: QuantumRelevance
    file_path: str | None = None
    line_number: int | None = None
    evidence: str | None = None
    algorithm: str | None = None
    category: str
    recommendation: str
    references: list[str] = Field(default_factory=list)


class ScanTarget(BaseModel):
    """A target to be scanned (repository path or TLS endpoint)."""

    target_type: Literal["repo", "endpoint"]
    value: str


class ScanResult(BaseModel):
    """The complete result of one or more scan targets."""

    scan_id: str
    project_name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    targets: list[ScanTarget] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    q_score: int = 100
    readiness_label: str = "Strong"
    client_name: str | None = None


class ScoreBreakdown(BaseModel):
    """Explains how the Q-Score was computed."""

    base_score: int = 100
    deductions: list[tuple[str, int]] = Field(default_factory=list)
    bonuses: list[tuple[str, int]] = Field(default_factory=list)
    final_score: int = 100
    readiness_label: str = "Strong"


class ReportSummary(BaseModel):
    """High-level summary included in generated reports."""

    total_findings: int = 0
    quantum_relevant_findings: int = 0
    high_priority: int = 0
    medium_priority: int = 0
    low_priority: int = 0
    info_count: int = 0


class ScheduleConfig(BaseModel):
    """Configuration for a scheduled recurring scan."""

    schedule_id: str
    target_type: Literal["repo", "endpoint"]
    target_value: str
    cron_expression: str
    client_name: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = True
