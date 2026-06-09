# L03/C05/T01 — Symmetric vs Asymmetric Cryptography

## Learning Objectives

- Distinguish symmetric and asymmetric crypto
- Understand why TLS combines both
- Recognize common algorithms

## Symmetric

Same key encrypts and decrypts.

- **Fast** (CPU has dedicated instructions like AES-NI)
- **Examples**: AES (128/192/256-bit), ChaCha20, 3DES (legacy)
- **Problem**: how do you share the key?

## Asymmetric (Public Key)

Two keys: public + private.
- What public encrypts, only private can decrypt
- What private signs, public can verify

- **Slow** (~1000× slower than symmetric)
- **Examples**: RSA (2048/4096-bit), ECDSA, Ed25519, ECDH

## Why Combine Both

TLS uses:
1. Asymmetric for **handshake** (key exchange + auth)
2. Symmetric for **bulk encryption** of app data

Best of both: fast bulk transfer + safe key exchange.

## AES (Advanced Encryption Standard)

The standard symmetric cipher since 2001.
- Block cipher, 128-bit blocks
- 128-bit, 192-bit, or 256-bit key
- Modes: ECB (bad), CBC, GCM, CCM
- **AES-GCM**: authenticated encryption; preferred mode

Hardware acceleration (AES-NI) makes it extremely fast on modern CPUs.

## ChaCha20-Poly1305

Modern stream cipher + MAC. Used when AES-NI not available (mobile, embedded).
- Constant-time (resistant to timing attacks)
- Faster than AES on low-end hardware

## RSA

Public key cryptosystem since 1977.
- Security based on integer factorization
- 2048-bit minimum modern
- Used for: signatures, key transport (legacy TLS)
- Slow; large keys

## Elliptic Curve

Modern public key.
- Smaller keys (256-bit ECC ≈ 3072-bit RSA security)
- Faster
- Curves: P-256, P-384, P-521, Curve25519, Curve448
- **Algorithms**: ECDSA (signing), ECDH (key exchange), Ed25519 (signing)

TLS 1.3 mandates ECDHE for key exchange (Ephemeral ECDH).

## Hashing

One-way functions. Input → fixed-size output.
- **SHA-256, SHA-384**: modern, secure
- **SHA-1, MD5**: broken; don't use
- **BLAKE2, BLAKE3**: faster alternatives

Used in: integrity checks, signatures, password hashing (with salt).

## MAC (Message Authentication Code)

Symmetric integrity check: HMAC-SHA256.
- Sender + receiver share key
- Sender computes MAC; sends along message
- Receiver computes MAC; compares

## AEAD (Authenticated Encryption with Associated Data)

Combines encryption + authentication in one operation.
- **AES-GCM**, **ChaCha20-Poly1305**
- Detects tampering
- Modern TLS uses only AEAD ciphers

## Key Derivation

From a shared secret (e.g., from ECDH), derive multiple keys (one for each direction, one for IVs, etc.). Function: HKDF (HMAC-based).

## Random Numbers

Cryptography requires high-quality randomness.
- Kernel CSPRNG: `/dev/urandom`, `getrandom()`
- Insufficient entropy → vulnerable keys
- Don't roll your own random

## Forward Secrecy

If long-term key compromised, past sessions still safe.
- Achieved via ephemeral keys (DH or ECDH per session)
- TLS 1.3: mandatory
- TLS 1.2: ECDHE cipher suites only

## Common Mistakes

- **Hardcoded keys** in source
- **Reusing nonces** (catastrophic for AES-GCM, ChaCha20)
- **MD5/SHA-1** for security purposes
- **ECB mode** (patterns visible)
- **Custom crypto** (always wrong)

## Interview Prep

**Junior**: "Symmetric vs asymmetric."

**Mid**: "Why does TLS use both?"

**Senior**: "What's AEAD?"

**Staff**: "What is forward secrecy?"

## Next Topic

→ [T02 — Certificates, CAs, Chains of Trust](T02-Certificates.md)
