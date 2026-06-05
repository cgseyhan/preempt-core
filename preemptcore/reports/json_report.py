"""JSON CBOM report writer."""

from __future__ import annotations

import json
from pathlib import Path

from preemptcore.core.models import ScanResult


def write_json_report(result: ScanResult, output_dir: Path) -> Path:
    """Write the scan result as a CBOM JSON file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "cbom.json"

    data = result.model_dump(mode="json")
    out_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    return out_path
