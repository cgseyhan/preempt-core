# PreemptCore

**PreemptCore** is a developer-first cryptographic inventory and post-quantum readiness scanner.

It helps engineering and security teams discover quantum-relevant cryptographic usage across repositories and TLS endpoints, generate a **Cryptography Bill of Materials (CBOM)**, calculate a **Q-Score**, and prioritize migration work.

> PreemptCore does not claim that RSA or ECC usage is immediately broken today. Instead, it identifies cryptographic assets that should be included in a post-quantum migration roadmap.

---

## Quick Start

```bash
pip install -e ".[dev]"

# Scan a local repository
preemptcore scan repo ./examples/vulnerable_python_app

# Scan a TLS endpoint
preemptcore scan endpoint api.example.com

# Generate a PDF report from a CBOM
preemptcore report ./preemptcore-output/cbom.json --format pdf

# Start the Web Dashboard
preemptcore dashboard

# Schedule a daily scan for a specific client
preemptcore schedule run ./examples/vulnerable_python_app --client "Acme Corp"
```

## Features

- **Local Repository Scanner**: Analyze Python, JS/TS, Go, Java, and config files for cryptographic usage.
- **TLS Endpoint Scanner**: Detect deprecated legacy protocols or classical key exchange methods.
- **Web Dashboard**: Interactive UI with charts to track post-quantum readiness over time.
- **Consultant Mode**: Multi-client tracking (`--client`), scheduled scans (`preemptcore schedule run`), and white-label **PDF Export**.
- **CI/CD Ready**: Includes a composite GitHub Action to enforce Q-Score thresholds and comment on PRs.
- **Reporting**: Exports to JSON (CBOM), HTML, Markdown, PDF, and SARIF for GitHub Security Center integration.

## Output

```
PreemptCore Scan Complete

Project: vulnerable_python_app
Q-Score: 44/100
Readiness: Low

Findings:
- 3 high quantum-relevant findings
- 4 deprecated crypto findings
- 1 hardcoded key indicator

Reports written to:
  ./preemptcore-output/cbom.json
  ./preemptcore-output/report.html
  ./preemptcore-output/report.sarif
```

## GitHub Actions Integration

You can integrate PreemptCore directly into your CI/CD pipeline to block PRs that drop your Q-Score below a certain threshold:

```yaml
- uses: cgseyhan/preempt-core@master
  with:
    path: '.'
    min-q-score: 50
    format: 'all'
```


## Development

```bash
# Install with dev extras
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check .

# Type check
mypy preemptcore
```

## Docker

```bash
docker build -t preemptcore .
docker run --rm -v "$PWD:/workspace" preemptcore scan repo /workspace
```

## NIST PQC Standards

| Algorithm | Standard | Use Case                         |
|-----------|----------|----------------------------------|
| ML-KEM    | FIPS 203 | Key encapsulation / key exchange |
| ML-DSA    | FIPS 204 | Digital signatures               |
| SLH-DSA   | FIPS 205 | Digital signatures (stateless)   |
| FN-DSA    | FIPS 206 | Digital signatures (lattice)     |

## License

MIT
