"""TLS endpoint scanner — checks certificate and protocol details."""

from __future__ import annotations

import socket
import ssl
import uuid

from preemptcore.core.models import (
    Finding,
    FindingSeverity,
    QuantumRelevance,
    ScanResult,
    ScanTarget,
)


class EndpointScanner:
    """Scans a TLS endpoint and extracts cryptographic metadata."""

    def scan(self, host: str) -> ScanResult:
        """Connect to host and return a ScanResult with TLS findings."""
        # Normalize input: strip scheme if present
        host = host.removeprefix("https://").removeprefix("http://").rstrip("/")

        scan_id = f"scan_{uuid.uuid4().hex[:12]}"
        result = ScanResult(
            scan_id=scan_id,
            project_name=host,
            targets=[ScanTarget(target_type="endpoint", value=host)],
        )

        try:
            cert_info = self._get_cert_info(host)
        except Exception as exc:  # noqa: BLE001
            result.findings.append(
                Finding(
                    id=f"ep-err-{uuid.uuid4().hex[:8]}",
                    title="TLS connection failed",
                    description=f"Could not connect to {host}: {exc}",
                    severity=FindingSeverity.INFO,
                    quantum_relevance=QuantumRelevance.NONE,
                    category="tls_error",
                    recommendation="Verify the host is reachable and supports TLS.",
                )
            )
            return result

        result.findings.extend(self._analyze_cert(host, cert_info))
        return result

    def _get_cert_info(self, host: str, port: int = 443) -> dict:  # type: ignore[type-arg]
        """Retrieve TLS certificate metadata via a raw SSL socket."""
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                protocol = ssock.version()
                cipher = ssock.cipher()
        return {"cert": cert, "protocol": protocol, "cipher": cipher}

    def _analyze_cert(self, host: str, info: dict) -> list[Finding]:  # type: ignore[type-arg]
        """Produce findings from certificate metadata."""
        findings: list[Finding] = []
        cert = info.get("cert", {})
        protocol = info.get("protocol", "")

        # Check for legacy TLS versions
        if protocol in ("TLSv1", "TLSv1.1"):
            findings.append(
                Finding(
                    id=f"ep-tls-{uuid.uuid4().hex[:8]}",
                    title=f"Legacy TLS version in use: {protocol}",
                    description=(
                        f"The endpoint {host} negotiated {protocol}, which is deprecated and "
                        "should be disabled."
                    ),
                    severity=FindingSeverity.HIGH,
                    quantum_relevance=QuantumRelevance.LOW,
                    category="tls_legacy",
                    recommendation=(
                        "Upgrade to TLS 1.3. Legacy TLS versions offer weaker forward secrecy "
                        "and are deprecated by RFC 8996."
                    ),
                    references=["https://datatracker.ietf.org/doc/html/rfc8996"],
                )
            )

        # Classical public-key cryptography notice
        subject = dict(x[0] for x in cert.get("subject", []))
        issuer = dict(x[0] for x in cert.get("issuer", []))
        findings.append(
            Finding(
                id=f"ep-pki-{uuid.uuid4().hex[:8]}",
                title="Classical public-key cryptography in use",
                description=(
                    f"The TLS certificate for {host} uses classical public-key cryptography "
                    f"(subject: {subject.get('commonName', host)}). "
                    "This should be included in your post-quantum migration inventory."
                ),
                severity=FindingSeverity.MEDIUM,
                quantum_relevance=QuantumRelevance.HIGH,
                category="classical_pki",
                recommendation=(
                    "This does not necessarily indicate an immediately exploitable vulnerability "
                    "today. Evaluate migration to post-quantum certificates when your CA and "
                    "clients support ML-KEM or hybrid key establishment."
                ),
                references=[
                    "https://csrc.nist.gov/pubs/fips/203/final",
                    "https://www.cisa.gov/resources-tools/resources/"
                    "quantum-readiness-migration-post-quantum-cryptography",
                ],
                evidence=f"Protocol: {protocol} | Issuer: {issuer.get('organizationName', 'unknown')}",
            )
        )

        return findings
