import os
import shutil
from pathlib import Path

from typer.testing import CliRunner

from preemptcore.cli.main import app

runner = CliRunner()


def test_scan_repo_fails_below_threshold(tmp_path: Path) -> None:
    # This repo scan will return a score (e.g. 90 or 100 based on empty dir)
    # If we set min-q-score to 101, it must fail.
    empty_repo = tmp_path / "empty_repo"
    empty_repo.mkdir()
    
    result = runner.invoke(app, ["scan", "repo", str(empty_repo), "--min-q-score", "101"])
    assert result.exit_code == 1
    assert "Final Q-Score" in result.stdout
    assert "below the required threshold" in result.stdout

def test_scan_repo_passes_above_threshold(tmp_path: Path) -> None:
    empty_repo = tmp_path / "empty_repo"
    empty_repo.mkdir()
    
    result = runner.invoke(app, ["scan", "repo", str(empty_repo), "--min-q-score", "50"])
    assert result.exit_code == 0
    assert "PreemptCore Scan Complete" in result.stdout
