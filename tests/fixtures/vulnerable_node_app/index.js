// Vulnerable Node.js fixture — for JS/TS rule tests

const crypto = require('crypto');

// RSA key generation (quantum-relevant)
const { privateKey, publicKey } = crypto.generateKeyPair('rsa', {
  modulusLength: 2048,
});

// RSA-SHA256 signing (quantum-relevant)
const sign = crypto.createSign('RSA-SHA256');
sign.update('data to sign');
const signature = sign.sign(privateKey, 'hex');

// MD5 usage (deprecated)
const md5Hash = crypto.createHash('md5').update('data').digest('hex');

// SHA-1 usage (deprecated)
const sha1Hash = crypto.createHash('sha1').update('data').digest('hex');

// jsonwebtoken RS256 (quantum-relevant)
const jwt = require('jsonwebtoken');
const token = jwt.sign({ sub: 'user123' }, privateKey, { algorithm: 'RS256' });
