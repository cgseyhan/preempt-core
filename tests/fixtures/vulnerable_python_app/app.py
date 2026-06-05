"""Vulnerable Python app fixture — used by test_repo_scanner.py and future rule tests."""

# RSA key generation (quantum-relevant)
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend(),
)

# Weak hash (deprecated)
import hashlib
digest = hashlib.md5(b"sensitive_data").hexdigest()

# SHA-1 (deprecated)
sha1_digest = hashlib.sha1(b"other_data").hexdigest()

# JWT RS256 (quantum-relevant)
import jwt
token = jwt.encode({"sub": "user123"}, "secret", algorithm="RS256")

# Hardcoded key indicator
RSA_PRIVATE_KEY = "-----BEGIN RSA PRIVATE KEY-----\nMIIEo..."

# Legacy TLS
import ssl
ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
