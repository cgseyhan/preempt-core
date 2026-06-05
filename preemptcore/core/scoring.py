"""Deterministic Q-Score calculator.

Scoring rules (no AI/LLM involvement):

Base score: 100

Deductions:
  - High quantum relevance finding:    -8 each
  - Medium quantum relevance finding:  -4 each
  - Low quantum relevance finding:     -1 each
  - Deprecated crypto finding:         -7 each
  - Hardcoded key/secret indicator:    -12 each
  - TLS 1.0 / 1.1 exposure:           -10 (once)
  - No migration signals found:        -10 (once)

Bonuses:
  + KMS / Vault / HSM reference found: +5
  + Crypto inventory file present:     +5
"""

from __future__ import annotations

from preemptcore.core.models import Finding, QuantumRelevance, ScoreBreakdown, ScanResult

# Category constants used by rules
CATEGORY_DEPRECATED_CRYPTO = "deprecated_crypto"
CATEGORY_HARDCODED_KEY = "hardcoded_key"
CATEGORY_TLS_LEGACY = "tls_legacy"
CATEGORY_MIGRATION_SIGNAL = "migration_signal"

_READINESS_LABELS = [
    (86, "Strong"),
    (71, "Good"),
    (51, "Moderate"),
    (31, "Low"),
    (0, "Critical"),
]


def _readiness_label(score: int) -> str:
    for threshold, label in _READINESS_LABELS:
        if score >= threshold:
            return label
    return "Critical"


def calculate_score(result: ScanResult) -> ScoreBreakdown:
    """Compute Q-Score from a ScanResult deterministically."""
    base = 100
    deductions: list[tuple[str, int]] = []
    bonuses: list[tuple[str, int]] = []

    has_tls_legacy = False
    has_migration_signal = False
    has_kms_vault_hsm = False
    has_crypto_inventory_file = False

    for finding in result.findings:
        _apply_quantum_relevance(finding, deductions)
        _apply_category_flags(
            finding,
            deductions,
            has_tls_legacy_ref=None,  # handled below
        )

        if finding.category == CATEGORY_DEPRECATED_CRYPTO:
            deductions.append(("Deprecated crypto usage", -7))
        elif finding.category == CATEGORY_HARDCODED_KEY:
            deductions.append(("Hardcoded key/secret indicator", -12))
        elif finding.category == CATEGORY_TLS_LEGACY:
            has_tls_legacy = True
        elif finding.category == CATEGORY_MIGRATION_SIGNAL:
            has_migration_signal = True

        title_lower = finding.title.lower()
        if any(k in title_lower for k in ("kms", "vault", "hsm")):
            has_kms_vault_hsm = True
        if "crypto inventory" in title_lower:
            has_crypto_inventory_file = True

    if has_tls_legacy:
        deductions.append(("TLS 1.0/1.1 exposure", -10))

    if not has_migration_signal:
        deductions.append(("No migration signals found", -10))

    if has_kms_vault_hsm:
        bonuses.append(("KMS/Vault/HSM reference found", +5))

    if has_crypto_inventory_file:
        bonuses.append(("Crypto inventory file present", +5))

    total_deduction = sum(v for _, v in deductions)
    total_bonus = sum(v for _, v in bonuses)
    final = max(0, min(100, base + total_deduction + total_bonus))

    return ScoreBreakdown(
        base_score=base,
        deductions=deductions,
        bonuses=bonuses,
        final_score=final,
        readiness_label=_readiness_label(final),
    )


def _apply_quantum_relevance(finding: Finding, deductions: list[tuple[str, int]]) -> None:
    """Add per-finding quantum relevance deduction."""
    if finding.quantum_relevance == QuantumRelevance.HIGH:
        deductions.append((f"High quantum relevance: {finding.title}", -8))
    elif finding.quantum_relevance == QuantumRelevance.MEDIUM:
        deductions.append((f"Medium quantum relevance: {finding.title}", -4))
    elif finding.quantum_relevance == QuantumRelevance.LOW:
        deductions.append((f"Low quantum relevance: {finding.title}", -1))


def _apply_category_flags(
    finding: Finding,
    deductions: list[tuple[str, int]],
    has_tls_legacy_ref: None,
) -> None:
    """Placeholder for future per-category logic extensions."""
    pass
