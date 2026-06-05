"""Base rule class for PreemptCore's rule engine.

Rules are deterministic, regex-based scanners that produce Finding objects.
They operate on individual file content (text) line by line.
"""

from __future__ import annotations

import re
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

from preemptcore.core.models import Finding, FindingSeverity, QuantumRelevance


@dataclass
class RuleMatch:
    """A single regex match within a file."""

    rule_id: str
    file_path: Path
    line_number: int
    line_content: str
    evidence: str


class BaseRule(ABC):
    """Abstract base class for all PreemptCore scan rules."""

    #: Unique rule identifier (e.g. "py-rsa-keygen")
    rule_id: str

    #: Human-readable title
    title: str

    #: Detailed description (safe language — no "broken/vulnerable" for RSA/ECC)
    description: str

    #: Severity of the finding
    severity: FindingSeverity

    #: Quantum relevance classification
    quantum_relevance: QuantumRelevance

    #: Category tag (e.g. "classical_pki", "deprecated_crypto", "hardcoded_key")
    category: str

    #: Migration-aware recommendation
    recommendation: str

    #: NIST / CISA / RFC references
    references: list[str] = field(default_factory=list)

    @abstractmethod
    def match(self, content: str, file_path: Path) -> list[RuleMatch]:
        """Return all matches found in the given file content."""
        ...

    def to_finding(self, match: RuleMatch) -> Finding:
        """Convert a RuleMatch to a Finding."""
        return Finding(
            id=f"{self.rule_id}-{uuid.uuid4().hex[:8]}",
            title=self.title,
            description=self.description,
            severity=self.severity,
            quantum_relevance=self.quantum_relevance,
            file_path=str(match.file_path),
            line_number=match.line_number,
            evidence=match.evidence[:200],
            category=self.category,
            recommendation=self.recommendation,
            references=getattr(self, "references", []),
        )


class RegexRule(BaseRule):
    """A rule that matches a single regular expression pattern."""

    pattern: re.Pattern[str]

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)

    def match(self, content: str, file_path: Path) -> list[RuleMatch]:
        matches: list[RuleMatch] = []
        for lineno, line in enumerate(content.splitlines(), start=1):
            if self.pattern.search(line):
                matches.append(
                    RuleMatch(
                        rule_id=self.rule_id,
                        file_path=file_path,
                        line_number=lineno,
                        line_content=line,
                        evidence=line.strip()[:200],
                    )
                )
        return matches
