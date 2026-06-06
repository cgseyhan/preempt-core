from pathlib import Path

import pytest

from preemptcore.core.models import ScanResult, ScanTarget
from preemptcore.reports.markdown_report import write_markdown_report


@pytest.fixture
def sample_result() -> ScanResult:
    from datetime import datetime
    return ScanResult(
        scan_id="test-123",
        project_name="Test Project",
        created_at=datetime.now(),
        targets=[ScanTarget(target_type="repo", value=".")],
        findings=[],
        q_score=85,
        readiness_label="Good"
    )

def test_markdown_report_no_findings(tmp_path: Path, sample_result: ScanResult) -> None:
    out_path = write_markdown_report(sample_result, tmp_path)
    content = out_path.read_text(encoding="utf-8")
    
    assert "## PreemptCore Scan Report: Test Project" in content
    assert "**85/100**" in content
    assert "No findings detected. Excellent job! \U0001f680" in content

def test_markdown_report_with_findings(tmp_path: Path, sample_result: ScanResult) -> None:
    from preemptcore.core.models import Finding, FindingSeverity, QuantumRelevance
    sample_result.findings.append(
        Finding(
            id="test-rule",
            title="A Test Finding | With Pipes",
            description="Test desc",
            severity=FindingSeverity.HIGH,
            quantum_relevance=QuantumRelevance.HIGH,
            file_path="src/main.py",
            line_number=42,
            category="Crypto",
            recommendation="Fix it"
        )
    )
    
    out_path = write_markdown_report(sample_result, tmp_path)
    content = out_path.read_text(encoding="utf-8")
    
    assert "| **HIGH** | `src/main.py` | 42 | A Test Finding - With Pipes | Crypto |" in content
    assert "No findings detected." not in content
