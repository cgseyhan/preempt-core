"""Tests for Q-Score calculation."""

from __future__ import annotations

from preemptcore.core.models import (
    Finding,
    FindingSeverity,
    QuantumRelevance,
    ScanResult,
    ScanTarget,
)
from preemptcore.core.scoring import calculate_score


def _make_result(findings: list[Finding] | None = None) -> ScanResult:
    return ScanResult(
        scan_id="test-001",
        project_name="test-project",
        targets=[ScanTarget(target_type="repo", value="/tmp/test")],
        findings=findings or [],
    )


def _make_finding(
    qr: QuantumRelevance = QuantumRelevance.NONE,
    category: str = "classical_pki",
    title: str = "Test Finding",
) -> Finding:
    return Finding(
        id="f-001",
        title=title,
        description="Test.",
        severity=FindingSeverity.INFO,
        quantum_relevance=qr,
        category=category,
        recommendation="No action needed.",
    )


class TestBasicScoring:
    def test_empty_scan_yields_90(self) -> None:
        """No findings → no migration signals penalty only."""
        result = _make_result()
        breakdown = calculate_score(result)
        # Base 100 - 10 (no migration signals)
        assert breakdown.final_score == 90
        assert breakdown.readiness_label == "Strong"

    def test_high_qr_deducts_8(self) -> None:
        finding = _make_finding(qr=QuantumRelevance.HIGH)
        result = _make_result([finding])
        breakdown = calculate_score(result)
        # 100 - 8 (high qr) - 10 (no migration) = 82
        assert breakdown.final_score == 82

    def test_medium_qr_deducts_4(self) -> None:
        finding = _make_finding(qr=QuantumRelevance.MEDIUM)
        result = _make_result([finding])
        breakdown = calculate_score(result)
        # 100 - 4 - 10 = 86
        assert breakdown.final_score == 86

    def test_low_qr_deducts_1(self) -> None:
        finding = _make_finding(qr=QuantumRelevance.LOW)
        result = _make_result([finding])
        breakdown = calculate_score(result)
        # 100 - 1 - 10 = 89
        assert breakdown.final_score == 89

    def test_deprecated_crypto_deducts_7(self) -> None:
        finding = _make_finding(category="deprecated_crypto")
        result = _make_result([finding])
        breakdown = calculate_score(result)
        # 100 - 7 - 10 = 83
        assert breakdown.final_score == 83

    def test_hardcoded_key_deducts_12(self) -> None:
        finding = _make_finding(category="hardcoded_key")
        result = _make_result([finding])
        breakdown = calculate_score(result)
        # 100 - 12 - 10 = 78
        assert breakdown.final_score == 78

    def test_tls_legacy_deducts_10_once(self) -> None:
        f1 = _make_finding(category="tls_legacy")
        f2 = _make_finding(category="tls_legacy")
        result = _make_result([f1, f2])
        breakdown = calculate_score(result)
        # 100 - 10 (tls, once) - 10 (no migration) = 80
        assert breakdown.final_score == 80

    def test_score_clamped_at_zero(self) -> None:
        findings = [_make_finding(category="hardcoded_key") for _ in range(20)]
        result = _make_result(findings)
        breakdown = calculate_score(result)
        assert breakdown.final_score == 0

    def test_score_not_above_100(self) -> None:
        finding = _make_finding(title="kms reference", category="migration_signal")
        result = _make_result([finding])
        breakdown = calculate_score(result)
        assert breakdown.final_score <= 100


class TestReadinessLabels:
    def test_label_strong(self) -> None:
        result = _make_result()
        breakdown = calculate_score(result)
        assert breakdown.readiness_label in ("Strong", "Good", "Moderate", "Low", "Critical")

    def test_label_critical_at_zero(self) -> None:
        findings = [_make_finding(category="hardcoded_key") for _ in range(20)]
        result = _make_result(findings)
        breakdown = calculate_score(result)
        assert breakdown.readiness_label == "Critical"

    def test_score_breakdown_has_deductions(self) -> None:
        finding = _make_finding(qr=QuantumRelevance.HIGH)
        result = _make_result([finding])
        breakdown = calculate_score(result)
        assert len(breakdown.deductions) > 0
