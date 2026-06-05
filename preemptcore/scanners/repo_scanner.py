"""Repo scanner — recursively scans a local repository for crypto findings."""

from __future__ import annotations

import uuid
from pathlib import Path

from preemptcore.core.constants import IGNORED_DIRS
from preemptcore.core.models import ScanResult, ScanTarget


class RepoScanner:
    """Scans a local repository directory for cryptographic findings."""

    def scan(self, path: Path) -> ScanResult:
        """Run the scan and return a ScanResult.

        Rules are applied per-file based on file extension. This method is a
        stub — rule sets will be wired up in Task 4 and Task 5.
        """
        project_name = path.resolve().name
        scan_id = f"scan_{uuid.uuid4().hex[:12]}"

        result = ScanResult(
            scan_id=scan_id,
            project_name=project_name,
            targets=[ScanTarget(target_type="repo", value=str(path.resolve()))],
        )

        for file_path in self._iter_files(path):
            # Rule application will be added in subsequent tasks
            pass

        return result

    def _iter_files(self, root: Path):  # type: ignore[return]
        """Yield all non-ignored files under root."""
        for item in root.rglob("*"):
            if item.is_file() and not self._is_ignored(item):
                yield item

    def _is_ignored(self, path: Path) -> bool:
        """Return True if any part of the path is an ignored directory."""
        return any(part in IGNORED_DIRS for part in path.parts)
