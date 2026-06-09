"""Dashboard command: `preemptcore dashboard`."""

import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

dashboard_app = typer.Typer(help="Start the Web Dashboard.", no_args_is_help=True)
console = Console()

@dashboard_app.callback(invoke_without_command=True)
def run_dashboard() -> None:
    """Start the Web Dashboard server and open it in the browser."""
    # Check if dashboard/dist exists
    base_dir = Path(__file__).parent.parent.parent
    dashboard_dist = base_dir / "dashboard" / "dist"
    
    if not dashboard_dist.exists():
        console.print("[yellow]Building Dashboard UI for the first time... This might take a minute.[/yellow]")
        dashboard_dir = base_dir / "dashboard"
        try:
            subprocess.run(["npm", "run", "build"], cwd=dashboard_dir, check=True, shell=True)
        except subprocess.CalledProcessError:
            console.print("[bold red]Failed to build the dashboard. Make sure you have Node.js and npm installed.[/bold red]")
            raise typer.Exit(1)
            
    console.print(Panel("[bold green]Starting PreemptCore Dashboard...[/bold green]\nListening at: http://localhost:8000\nPress Ctrl+C to stop.", expand=False))
    
    # Open browser after a short delay
    def open_browser() -> None:
        time.sleep(1.5)
        webbrowser.open("http://localhost:8000")
        
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start Uvicorn
    import uvicorn
    uvicorn.run("preemptcore.api.main:app", host="127.0.0.1", port=8000, log_level="warning")
