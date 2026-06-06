"""Tests for the TLS endpoint scanner using mocked certificate data."""

from __future__ import annotations

from unittest.mock import patch

from preemptcore.core.models import ScanResult
from preemptcore.scanners.endpoint_scanner import EndpointScanner

MOCK_CERT = {
    "subject": [[("commonName", "example.com")]],
    "issuer": [[("organizationName", "Test CA")]],
    "notAfter": "Dec 31 23:59:59 2026 GMT",
}


class TestEndpointScanner:
    def test_scan_returns_scan_result(self) -> None:
        scanner = EndpointScanner()
        with patch.object(scanner, "_get_cert_info") as mock_get:
            mock_get.return_value = {
                "cert": MOCK_CERT,
                "protocol": "TLSv1.3",
                "cipher": ("TLS_AES_256_GCM_SHA384", "TLSv1.3", 256),
            }
            result = scanner.scan("example.com")

        assert isinstance(result, ScanResult)

    def test_scan_produces_pki_finding(self) -> None:
        scanner = EndpointScanner()
        with patch.object(scanner, "_get_cert_info") as mock_get:
            mock_get.return_value = {
                "cert": MOCK_CERT,
                "protocol": "TLSv1.3",
                "cipher": ("TLS_AES_256_GCM_SHA384", "TLSv1.3", 256),
            }
            result = scanner.scan("example.com")

        pki_findings = [f for f in result.findings if f.category == "classical_pki"]
        assert len(pki_findings) >= 1

    def test_legacy_tls_produces_finding(self) -> None:
        scanner = EndpointScanner()
        with patch.object(scanner, "_get_cert_info") as mock_get:
            mock_get.return_value = {
                "cert": MOCK_CERT,
                "protocol": "TLSv1",
                "cipher": ("AES128-SHA", "TLSv1", 128),
            }
            result = scanner.scan("example.com")

        tls_findings = [f for f in result.findings if f.category == "tls_legacy"]
        assert len(tls_findings) >= 1

    def test_connection_failure_produces_error_finding(self) -> None:
        scanner = EndpointScanner()
        with patch.object(scanner, "_get_cert_info", side_effect=ConnectionRefusedError("refused")):
            result = scanner.scan("unreachable.example.com")

        error_findings = [f for f in result.findings if f.category == "tls_error"]
        assert len(error_findings) == 1

    def test_strips_https_prefix(self) -> None:
        scanner = EndpointScanner()
        with patch.object(scanner, "_get_cert_info") as mock_get:
            mock_get.return_value = {
                "cert": MOCK_CERT,
                "protocol": "TLSv1.3",
                "cipher": ("TLS_AES_256_GCM_SHA384", "TLSv1.3", 256),
            }
            result = scanner.scan("https://example.com")

        assert result.project_name == "example.com"

    def test_finding_uses_safe_language(self) -> None:
        """Findings must not use 'broken' or 'vulnerable' for PKI findings."""
        scanner = EndpointScanner()
        with patch.object(scanner, "_get_cert_info") as mock_get:
            mock_get.return_value = {
                "cert": MOCK_CERT,
                "protocol": "TLSv1.3",
                "cipher": ("TLS_AES_256_GCM_SHA384", "TLSv1.3", 256),
            }
            result = scanner.scan("example.com")

        for finding in result.findings:
            assert "broken" not in finding.description.lower()
            assert "vulnerable" not in finding.description.lower()
