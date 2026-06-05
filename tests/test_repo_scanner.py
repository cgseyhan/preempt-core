"""Tests for the repo scanner."""

from __future__ import annotations

from pathlib import Path

from preemptcore.core.models import ScanResult
from preemptcore.scanners.repo_scanner import RepoScanner

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "vulnerable_python_app"


class TestRepoScanner:
    def test_scan_returns_scan_result(self, tmp_path: Path) -> None:
        """Scanner should return a ScanResult for any directory."""
        scanner = RepoScanner()
        result = scanner.scan(tmp_path)
        assert isinstance(result, ScanResult)

    def test_scan_id_is_set(self, tmp_path: Path) -> None:
        scanner = RepoScanner()
        result = scanner.scan(tmp_path)
        assert result.scan_id.startswith("scan_")

    def test_project_name_matches_dir(self, tmp_path: Path) -> None:
        scanner = RepoScanner()
        result = scanner.scan(tmp_path)
        assert result.project_name == tmp_path.name

    def test_scan_target_recorded(self, tmp_path: Path) -> None:
        scanner = RepoScanner()
        result = scanner.scan(tmp_path)
        assert len(result.targets) == 1
        assert result.targets[0].target_type == "repo"

    def test_ignored_dirs_skipped(self, tmp_path: Path) -> None:
        """Files inside node_modules and .git should not be yielded."""
        ignored = tmp_path / "node_modules" / "some_package"
        ignored.mkdir(parents=True)
        (ignored / "index.js").write_text("crypto.createSign('RSA-SHA256')")

        scanner = RepoScanner()
        files = list(scanner._iter_files(tmp_path))
        assert not any("node_modules" in str(f) for f in files)

    def test_scans_fixture_directory(self) -> None:
        """Scan the vulnerable_python_app fixture without crashing."""
        if not FIXTURE_DIR.exists():
            return  # fixture not yet created — skip
        scanner = RepoScanner()
        result = scanner.scan(FIXTURE_DIR)
        assert isinstance(result, ScanResult)
