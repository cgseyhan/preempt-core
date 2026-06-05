"""Report command: `preemptcore report <cbom.json> --format html`."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

report_app = typer.Typer(help="Generate reports from a CBOM JSON file.", no_args_is_help=True)
console = Console()


@report_app.command()
def report(
    cbom: Path = typer.Argument(..., help="Path to a cbom.json file produced by a scan."),
    fmt: str = typer.Option("html", "--format", "-f", help="Output format: html | sarif | json"),
    output: Path = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory (defaults to the cbom.json directory).",
    ),
) -> None:
    """Generate a report from an existing CBOM JSON file."""
    if not cbom.exists():
        console.print(f"[bold red]Error:[/bold red] File not found: {cbom}")
        raise typer.Exit(code=1)

    import json
    from preemptcore.core.models import ScanResult

    data = json.loads(cbom.read_text(encoding="utf-8"))
    result = ScanResult.model_validate(data)

    out_dir = output or cbom.parent

    from preemptcore.reports.html_report import write_html_report
    from preemptcore.reports.sarif_report import write_sarif_report
    from preemptcore.reports.json_report import write_json_report

    if fmt == "html":
        p = write_html_report(result, out_dir)
    elif fmt == "sarif":
        p = write_sarif_report(result, out_dir)
    else:
        p = write_json_report(result, out_dir)

    console.print(f"[green][OK][/green] Report written: {p}")
