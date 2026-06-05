"""Severity mapping helpers."""

from preemptcore.core.models import FindingSeverity, QuantumRelevance


def severity_from_quantum_relevance(qr: QuantumRelevance) -> FindingSeverity:
    """Map quantum relevance to a default finding severity."""
    mapping = {
        QuantumRelevance.HIGH: FindingSeverity.HIGH,
        QuantumRelevance.MEDIUM: FindingSeverity.MEDIUM,
        QuantumRelevance.LOW: FindingSeverity.LOW,
        QuantumRelevance.NONE: FindingSeverity.INFO,
    }
    return mapping[qr]
