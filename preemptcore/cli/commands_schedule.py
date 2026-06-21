"""Schedule command: `preemptcore schedule`."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

schedule_app = typer.Typer(help="Manage and run scheduled scans.", no_args_is_help=True)
console = Console()


@schedule_app.command("run")
def run_scheduler(
    target: str = typer.Argument(..., help="Path to repo or endpoint host to scan."),
    target_type: str = typer.Option("repo", "--type", "-t", help="Target type: repo | endpoint"),
    cron: str = typer.Option("0 0 * * *", "--cron", help="Cron expression for the schedule (default: daily at midnight)."),
    client: str | None = typer.Option(None, "--client", "-c", help="Client name to associate with the scheduled scan."),
) -> None:
    """Run a blocking scheduler to periodically execute a scan."""
    try:
        from apscheduler.schedulers.blocking import BlockingScheduler
        from apscheduler.triggers.cron import CronTrigger
    except ImportError:
        console.print("[bold red]Error:[/bold red] APScheduler not installed. Please install with `pip install apscheduler`.")
        raise typer.Exit(code=1)

    console.print(Panel(f"[bold cyan]Starting Scheduler[/bold cyan]\nTarget: {target}\nType: {target_type}\nCron: {cron}\nClient: {client or 'None'}"))

    def scheduled_scan_job() -> None:
        console.print(f"\n[bold green]Executing scheduled scan on {target}...[/bold green]")
        if target_type == "repo":
            from preemptcore.cli.commands_scan import _print_summary, _save_to_db
            from preemptcore.core.scoring import calculate_score
            from preemptcore.scanners.repo_scanner import RepoScanner
            
            scanner_repo = RepoScanner()
            p = Path(target)
            if not p.exists():
                console.print(f"[bold red]Error:[/bold red] Path not found: {p}")
                return
                
            result = scanner_repo.scan(p)
        else:
            from preemptcore.cli.commands_scan import _print_summary, _save_to_db
            from preemptcore.core.scoring import calculate_score
            from preemptcore.scanners.endpoint_scanner import EndpointScanner
            
            scanner_ep = EndpointScanner()
            result = scanner_ep.scan(target)
            
        breakdown = calculate_score(result)
        result.q_score = breakdown.final_score
        result.readiness_label = breakdown.readiness_label
        result.client_name = client
        
        _save_to_db(result)
        _print_summary(result)

    scheduler = BlockingScheduler()
    scheduler.add_job(scheduled_scan_job, CronTrigger.from_crontab(cron))
    
    try:
        console.print("[green]Scheduler is running. Press Ctrl+C to exit.[/green]")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        console.print("\n[yellow]Scheduler stopped.[/yellow]")
