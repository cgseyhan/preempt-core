"""Scan commands: `preemptcore scan repo` and `preemptcore scan endpoint`."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from preemptcore.core.models import ScanResult
from preemptcore.core.scoring import calculate_score
from preemptcore.storage.db import create_db_and_tables, get_session
from preemptcore.storage.repositories import ScanRepository

scan_app = typer.Typer(help="Scan a repository or TLS endpoint.", no_args_is_help=True)
console = Console()


@scan_app.command("repo")
def scan_repo(
    path: Path = typer.Argument(..., help="Path to the local repository to scan."),
    output: Path = typer.Option(
        Path("./preemptcore-output"),
        "--output",
        "-o",
        help="Directory to write report files.",
    ),
    fmt: str = typer.Option(
        "all",
        "--format",
        "-f",
        help="Output format: json | html | sarif | markdown | all",
    ),
    min_q_score: int = typer.Option(
        0,
        "--min-q-score",
        help="Fail the scan (exit code 1) if final Q-Score is below this threshold.",
    ),
) -> None:
    """Scan a local repository for quantum-relevant cryptographic usage."""
    if not path.exists():
        console.print(f"[bold red]Error:[/bold red] Path does not exist: {path}")
        raise typer.Exit(code=1)

    console.print(Panel(f"[bold cyan]Scanning repository:[/bold cyan] {path.resolve()}"))

    # Import here to keep CLI startup fast
    from preemptcore.scanners.repo_scanner import RepoScanner

    scanner = RepoScanner()
    result: ScanResult = scanner.scan(path)

    breakdown = calculate_score(result)
    result.q_score = breakdown.final_score
    result.readiness_label = breakdown.readiness_label

    _save_to_db(result)
    _print_summary(result)
    _write_reports(result, output, fmt)

    if result.q_score < min_q_score:
        console.print(f"\n[bold red]Error:[/bold red] Final Q-Score ({result.q_score}) is below the required threshold of {min_q_score}.")
        raise typer.Exit(code=1)


@scan_app.command("endpoint")
def scan_endpoint(
    host: str = typer.Argument(..., help="Domain or URL to scan (e.g. api.example.com)."),
    output: Path = typer.Option(
        Path("./preemptcore-output"),
        "--output",
        "-o",
        help="Directory to write report files.",
    ),
    min_q_score: int = typer.Option(
        0,
        "--min-q-score",
        help="Fail the scan (exit code 1) if final Q-Score is below this threshold.",
    ),
) -> None:
    """Scan a TLS endpoint for post-quantum migration relevance."""
    console.print(Panel(f"[bold cyan]Scanning endpoint:[/bold cyan] {host}"))

    from preemptcore.scanners.endpoint_scanner import EndpointScanner

    scanner = EndpointScanner()
    result: ScanResult = scanner.scan(host)

    breakdown = calculate_score(result)
    result.q_score = breakdown.final_score
    result.readiness_label = breakdown.readiness_label

    _save_to_db(result)
    _print_summary(result)
    _write_reports(result, output, "json")

    if result.q_score < min_q_score:
        console.print(f"\n[bold red]Error:[/bold red] Final Q-Score ({result.q_score}) is below the required threshold of {min_q_score}.")
        raise typer.Exit(code=1)

def _save_to_db(result: ScanResult) -> None:
    """Save the scan result to the local database."""
    try:
        create_db_and_tables()
        session_gen = get_session()
        session = next(session_gen)
        repo = ScanRepository(session)
        repo.save_scan(result)
    except Exception as e:
        console.print(f"[yellow]Warning: Could not save scan to history database: {e}[/yellow]")



def _print_summary(result: ScanResult) -> None:
    """Print a rich summary table to the terminal."""
    high = sum(1 for f in result.findings if f.severity.value in ("high", "critical"))
    medium = sum(1 for f in result.findings if f.severity.value == "medium")
    low = sum(1 for f in result.findings if f.severity.value in ("low", "info"))
    qr = sum(1 for f in result.findings if f.quantum_relevance.value != "none")

    label_color = {
        "Strong": "green",
        "Good": "green",
        "Moderate": "yellow",
        "Low": "yellow",
        "Critical": "red",
    }.get(result.readiness_label, "white")

    table = Table(title="PreemptCore Scan Complete", show_header=False, box=None)
    table.add_column("Key", style="bold")
    table.add_column("Value")
    table.add_row("Project", result.project_name)
    table.add_row("Scan ID", result.scan_id)
    table.add_row("Total findings", str(len(result.findings)))
    table.add_row("Quantum-relevant", str(qr))
    table.add_row("High / Critical", str(high))
    table.add_row("Medium", str(medium))
    table.add_row("Low / Info", str(low))
    table.add_row(
        "Q-Score",
        f"[bold {label_color}]{result.q_score}/100 — {result.readiness_label}[/bold {label_color}]",
    )
    console.print(table)


def _write_reports(result: ScanResult, output: Path, fmt: str) -> None:
    """Write report files in the requested format(s)."""
    output.mkdir(parents=True, exist_ok=True)

    from preemptcore.reports.html_report import write_html_report
    from preemptcore.reports.json_report import write_json_report
    from preemptcore.reports.markdown_report import write_markdown_report
    from preemptcore.reports.sarif_report import write_sarif_report

    written: list[Path] = []

    if fmt in ("json", "all"):
        p = write_json_report(result, output)
        written.append(p)

    if fmt in ("html", "all"):
        p = write_html_report(result, output)
        written.append(p)

    if fmt in ("sarif", "all"):
        p = write_sarif_report(result, output)
        written.append(p)

    if fmt in ("markdown", "all"):
        p = write_markdown_report(result, output)
        written.append(p)

    if written:
        console.print("\n[bold]Reports written:[/bold]")
        for p in written:
            console.print(f"  [green][OK][/green] {p}")
