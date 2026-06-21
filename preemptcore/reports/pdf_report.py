"""PDF report writer using WeasyPrint."""

from __future__ import annotations

from pathlib import Path

from preemptcore.core.models import ScanResult
from preemptcore.reports.html_report import write_html_report


def write_pdf_report(result: ScanResult, output_dir: Path, custom_css: str | None = None) -> Path:
    """Render a PDF report from the scan result."""
    try:
        from weasyprint import CSS, HTML
    except ImportError as e:
        raise ImportError("weasyprint is not installed. Please install with `pip install weasyprint` to generate PDF reports.") from e

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "report.pdf"

    # We reuse the HTML generation
    html_path = write_html_report(result, output_dir)
    
    # Render PDF
    html_doc = HTML(filename=str(html_path))
    
    stylesheets = []
    if custom_css:
        stylesheets.append(CSS(string=custom_css))
        
    html_doc.write_pdf(str(out_path), stylesheets=stylesheets if stylesheets else None)
    
    return out_path
