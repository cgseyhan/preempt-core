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

# Generate an HTML report from a CBOM
preemptcore report ./preemptcore-output/cbom.json --format html
```

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
