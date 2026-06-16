# L03/C05/T04 — Cipher Suites, Forward Secrecy

## Learning Objectives

- Read cipher suite names
- Choose modern cipher suites
- Configure servers safely

## Cipher Suite Naming

### TLS 1.2
```
TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
│   │     │   │    │     │   │
│   │     │   │    │     │   └─ MAC / PRF
│   │     │   │    │     └─── cipher mode (GCM)
│   │     │   │    └─────── symmetric cipher
│   │     │   └─────── (filler)
│   │     └───── auth algorithm (server's cert type)
│   └───── key exchange
└── TLS protocol
```

### TLS 1.3 (only 5 suites)
```
TLS_AES_256_GCM_SHA384
TLS_AES_128_GCM_SHA256
TLS_CHACHA20_POLY1305_SHA256
TLS_AES_128_CCM_SHA256
TLS_AES_128_CCM_8_SHA256
```

Simplified: cipher + hash. Key exchange always ECDHE. Auth via signature_algorithms extension.

## Modern Recommended

For 2025+:

### TLS 1.3 (preferred)
- TLS_AES_256_GCM_SHA384
- TLS_AES_128_GCM_SHA256
- TLS_CHACHA20_POLY1305_SHA256

### TLS 1.2 (fallback for legacy clients)
- ECDHE-ECDSA-AES256-GCM-SHA384
- ECDHE-ECDSA-CHACHA20-POLY1305
- ECDHE-RSA-AES256-GCM-SHA384
- ECDHE-RSA-CHACHA20-POLY1305

## Forward Secrecy

If server's long-term private key is stolen tomorrow, can past traffic be decrypted?
- **Without FS**: yes (RSA key exchange → recorded sessions decrypted with stolen key)
- **With FS**: no (ECDHE generates per-session ephemeral key)

TLS 1.3: FS is mandatory (only ECDHE/PSK key exchange).
TLS 1.2: only ECDHE/DHE suites have FS. Avoid plain RSA suites.

## What to Disable

- TLS 1.0 (POODLE)
- TLS 1.1 (weaker)
- SSLv2, SSLv3 (broken)
- RC4 (broken)
- 3DES (weak)
- CBC mode (padding oracle attacks; remove from preferences)
- RSA key exchange (no FS)
- MD5 (broken)
- SHA-1 in cert sigs (weak)
- Anonymous DH (no auth)

## Mozilla Configurations

Mozilla publishes server configs:
- **Modern**: TLS 1.3 only; modern browsers
- **Intermediate**: TLS 1.2+; broad compatibility (recommended default)
- **Old**: includes TLS 1.0 (legacy clients; high security cost)

https://ssl-config.mozilla.org/

## Sample Nginx Config (Intermediate)

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 1d;
ssl_session_tickets off;
```

## Testing

```bash
# Comprehensive
testssl.sh example.com

# Quick
nmap --script ssl-enum-ciphers -p 443 example.com

# SSL Labs (online)
# https://www.ssllabs.com/ssltest/

# Just protocol versions
nmap --script ssl-enum-ciphers -p 443 -Pn example.com | grep TLSv
```

Aim for SSL Labs A+ for public sites.

## Cipher Order

Server can prefer certain ciphers:
- `ssl_prefer_server_ciphers off` in TLS 1.3 (rare to override)
- For TLS 1.2: put ChaCha20 first for mobile-friendly default

## Performance Impact

- AES-NI: hardware acceleration; AES-GCM very fast
- ChaCha20 software: fast on mobile / no AES-NI
- Modern CPUs: TLS overhead < 1% throughput

## Common Mistakes

- Old protocols enabled "for compatibility" with one ancient client
- Cipher list copy-pasted from 2014
- Self-signed certs in production
- HSTS without testing first (browsers cache the policy)
- Mixed content (HTTP resources on HTTPS page)

## HSTS

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

Browser: only ever HTTPS for this domain for 1 year.

Use carefully: once set with long max-age, can't easily revert.

## Best Practices

- Start from **Mozilla "Intermediate"** (TLS 1.2 + 1.3) for public sites; move to "Modern" (TLS 1.3 only) once you know no legacy clients remain.
- Offer only **AEAD suites with ECDHE** (forward secrecy); disable static-RSA key exchange, CBC suites, RC4, 3DES, and TLS ≤1.1.
- For TLS 1.2, **let the client choose** (`ssl_prefer_server_ciphers off`) so mobile clients can pick ChaCha20 — it's faster without AES-NI.
- Enable **session resumption** (tickets or IDs) carefully: rotate ticket keys, or disable tickets if you can't rotate them, to preserve forward secrecy.
- Re-test after every config change with `testssl.sh`/SSL Labs and **keep the cipher list in config management**, not copy-pasted from a blog.
- Roll out **HSTS incrementally** (short max-age → long → `preload`) so you can back out before committing to the preload list.

## Quick Refs

TLS 1.3 has only 5 suites; key exchange is always ECDHE and auth is negotiated separately:

```
TLS_AES_256_GCM_SHA384          ← strong default
TLS_AES_128_GCM_SHA256          ← fast, widely used
TLS_CHACHA20_POLY1305_SHA256    ← best on no-AES-NI / mobile
TLS_AES_128_CCM_SHA256          ← constrained / IoT
TLS_AES_128_CCM_8_SHA256        ← IoT (short tag)
```

```bash
# Full audit (protocols, ciphers, cert, vulns)
testssl.sh example.com

# Which protocols/ciphers does the server accept?
nmap --script ssl-enum-ciphers -p 443 example.com

# Negotiate a specific version to confirm what's enabled
openssl s_client -connect example.com:443 -tls1_2 </dev/null
openssl s_client -connect example.com:443 -tls1_3 </dev/null

# What did this connection actually negotiate?
curl -v https://example.com 2>&1 | grep -iE "SSL connection|ALPN|TLSv"
```

Disable list (memorize): **SSLv2/v3, TLS 1.0/1.1, RC4, 3DES, CBC suites, static-RSA kex, MD5, SHA-1 sigs, anonymous DH.**

## Interview Prep

**Mid**: "What's forward secrecy?"

**Senior**: "Modern cipher policy — what to enable?"

**Staff**: "Test if a server is secure — process."

## Next Topic

→ [T05 — Certificate Rotation & ACME](T05-ACME-Cert-Rotation.md)
