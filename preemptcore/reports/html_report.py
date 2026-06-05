"""HTML report writer using Jinja2."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from preemptcore.core.models import ScanResult

_TEMPLATE_DIR = Path(__file__).parent / "templates"


def write_html_report(result: ScanResult, output_dir: Path) -> Path:
    """Render an HTML report from the scan result."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "report.html"

    env = Environment(loader=FileSystemLoader(str(_TEMPLATE_DIR)), autoescape=True)
    template = env.get_template("report.html.j2")

    high = sum(1 for f in result.findings if f.severity.value in ("high", "critical"))
    medium = sum(1 for f in result.findings if f.severity.value == "medium")
    low = sum(1 for f in result.findings if f.severity.value in ("low", "info"))
    quantum_relevant = sum(1 for f in result.findings if f.quantum_relevance.value != "none")

    html = template.render(
        result=result,
        high=high,
        medium=medium,
        low=low,
        quantum_relevant=quantum_relevant,
        readiness_color=_readiness_color(result.readiness_label),
    )

    out_path.write_text(html, encoding="utf-8")
    return out_path


def _readiness_color(label: str) -> str:
    return {
        "Strong": "#22c55e",
        "Good": "#86efac",
        "Moderate": "#fbbf24",
        "Low": "#f97316",
        "Critical": "#ef4444",
    }.get(label, "#94a3b8")
