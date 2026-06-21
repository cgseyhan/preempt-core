"""PreemptCore CLI entry point."""

import typer

from preemptcore.cli.commands_dashboard import dashboard_app
from preemptcore.cli.commands_report import report_app
from preemptcore.cli.commands_scan import scan_app
from preemptcore.cli.commands_schedule import schedule_app

app = typer.Typer(
    name="preemptcore",
    help=(
        "PreemptCore — cryptographic inventory and post-quantum readiness scanner.\n\n"
        "Scan repositories and TLS endpoints for quantum-relevant cryptographic usage, "
        "generate a Q-Score, and export CBOM/HTML/SARIF reports."
    ),
    no_args_is_help=True,
    rich_markup_mode="rich",
)

app.add_typer(scan_app, name="scan")
app.add_typer(report_app, name="report")
app.add_typer(dashboard_app, name="dashboard")
app.add_typer(schedule_app, name="schedule")

@app.command()
def version() -> None:
    """Show PreemptCore version."""
    from preemptcore import __version__

    typer.echo(f"PreemptCore v{__version__}")


if __name__ == "__main__":
    app()
