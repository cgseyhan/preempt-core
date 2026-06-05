"""Shared constants for PreemptCore."""

# File extensions by language group
PYTHON_EXTENSIONS = {".py"}
JS_TS_EXTENSIONS = {".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs"}
GO_EXTENSIONS = {".go"}
JAVA_EXTENSIONS = {".java"}
CONFIG_EXTENSIONS = {".yaml", ".yml", ".json", ".env", ".toml", ".conf", ".cfg", ".ini"}
DOCKER_EXTENSIONS = {"Dockerfile", ".dockerfile"}

ALL_SUPPORTED_EXTENSIONS = (
    PYTHON_EXTENSIONS
    | JS_TS_EXTENSIONS
    | GO_EXTENSIONS
    | JAVA_EXTENSIONS
    | CONFIG_EXTENSIONS
    | DOCKER_EXTENSIONS
)

# Directories to ignore when scanning
IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    "target",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "site-packages",
    ".eggs",
}

# NIST PQC algorithm references for recommendations
NIST_PQC_REFS = {
    "ML-KEM": "https://csrc.nist.gov/pubs/fips/203/final",
    "ML-DSA": "https://csrc.nist.gov/pubs/fips/204/final",
    "SLH-DSA": "https://csrc.nist.gov/pubs/fips/205/final",
    "FN-DSA": "https://csrc.nist.gov/pubs/fips/206/ipd",
}
