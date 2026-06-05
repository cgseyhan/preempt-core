"""SARIF 2.1 report writer for GitHub Security tab integration."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from preemptcore.core.models import ScanResult

SARIF_VERSION = "2.1.0"
SARIF_SCHEMA = "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json"


def write_sarif_report(result: ScanResult, output_dir: Path) -> Path:
    """Write SARIF 2.1 report from scan results."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "report.sarif"

    rules = []
    results = []

    seen_rules: set[str] = set()

    for finding in result.findings:
        rule_id = finding.id

        if rule_id not in seen_rules:
            seen_rules.add(rule_id)
            rules.append(
                {
                    "id": rule_id,
                    "name": finding.title.replace(" ", ""),
                    "shortDescription": {"text": finding.title},
                    "fullDescription": {"text": finding.description},
                    "helpUri": finding.references[0] if finding.references else "",
                    "properties": {
                        "quantum_relevance": finding.quantum_relevance.value,
                        "category": finding.category,
                    },
                }
            )

        location: dict = {}  # type: ignore[type-arg]
        if finding.file_path:
            location = {
                "physicalLocation": {
                    "artifactLocation": {"uri": finding.file_path},
                    "region": {"startLine": finding.line_number or 1},
                }
            }

        results.append(
            {
                "ruleId": rule_id,
                "level": _sarif_level(finding.severity.value),
                "message": {
                    "text": f"{finding.description}\n\nRecommendation: {finding.recommendation}"
                },
                "locations": [location] if location else [],
            }
        )

    sarif = {
        "version": SARIF_VERSION,
        "$schema": SARIF_SCHEMA,
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "PreemptCore",
                        "version": "0.1.0",
                        "informationUri": "https://github.com/preemptcore/preemptcore",
                        "rules": rules,
                    }
                },
                "results": results,
            }
        ],
    }

    out_path.write_text(json.dumps(sarif, indent=2), encoding="utf-8")
    return out_path


def _sarif_level(severity: str) -> str:
    return {
        "critical": "error",
        "high": "error",
        "medium": "warning",
        "low": "note",
        "info": "note",
    }.get(severity, "note")
