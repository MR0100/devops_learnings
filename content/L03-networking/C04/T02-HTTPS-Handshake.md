# L03/C04/T02 — HTTPS / TLS Handshake (Step by Step)

## Learning Objectives

- Walk through TLS 1.3 handshake
- Compare TLS 1.2 vs 1.3
- Understand 0-RTT resumption

## TLS 1.3 (1-RTT)

```
Client                                    Server
  │                                         │
  │ ClientHello                             │
  │ + key_share (ephemeral pubkey)          │
  │ + ciphers, sig_algs, supported_versions │
  │ ──────────────────────────────────→    │
  │                                         │
  │ ServerHello + key_share                 │
  │ {EncryptedExtensions, Certificate,      │
  │  CertificateVerify, Finished}           │
  │ ←──────────────────────────────────    │
  │                                         │
  │ {Finished}                              │
  │ ──────────────────────────────────→    │
  │                                         │
  │ {HTTP request}                          │
  │ ──────────────────────────────────→    │
```

After the handshake, both sides have a shared symmetric key. All app data is encrypted.

## Step-by-Step

### 1. Client → Server: ClientHello
- TLS versions supported (must include 1.3)
- Cipher suites offered
- Signature algorithms
- Supported groups (for ECDHE)
- **Key share**: client's ephemeral ECDHE public key
- SNI (server_name extension): "I want example.com"
- ALPN: "h2, http/1.1" (which L7 protocol)

### 2. Server → Client: ServerHello + Encrypted Extensions
- Selected version (1.3)
- Selected cipher suite
- Server's key share (ECDHE public key)
- **Now both sides can derive shared secret**
- Encrypted extensions (ALPN selection, etc.)
- Certificate (server's cert chain)
- CertificateVerify (signature proving server owns the private key)
- Finished (proves handshake integrity)

### 3. Client → Server: Finished
- Verifies server's cert chain
- Sends own Finished
- Connection established

### 4. Application Data
- All data symmetrically encrypted with derived key (AES-GCM, ChaCha20-Poly1305)

## TLS 1.2 (2-RTT)

```
Client                                    Server
  │ ClientHello                             │
  │ ───────────────→                       │
  │ ServerHello, Certificate,               │
  │ ServerKeyExchange, ServerHelloDone      │
  │ ←───────────────                       │
  │ ClientKeyExchange,                      │
  │ ChangeCipherSpec, Finished              │
  │ ───────────────→                       │
  │ ChangeCipherSpec, Finished              │
  │ ←───────────────                       │
  │ Application Data                        │
  │ ───────────────→                       │
```

Twice the round trips. TLS 1.3 was a major upgrade.

## TLS 1.3 Improvements

- 1-RTT handshake (vs 2-RTT)
- 0-RTT resumption (early data)
- Forward secrecy mandatory (ECDHE only)
- Removed broken primitives (RC4, 3DES, MD5, SHA-1, RSA key exchange)
- Encrypted handshake (more privacy)
- Fewer cipher suites (5 vs hundreds)
- ChaCha20 for mobile/low-power CPUs

## TLS 1.3 Cipher Suites (only 5)

```
TLS_AES_128_GCM_SHA256
TLS_AES_256_GCM_SHA384
TLS_CHACHA20_POLY1305_SHA256
TLS_AES_128_CCM_SHA256
TLS_AES_128_CCM_8_SHA256
```

Each: cipher + hash. No key exchange variants (always ECDHE).

## 0-RTT Resumption

Subsequent connections can send app data immediately:
```
ClientHello + early_data (app request, encrypted with resumption key)
   ────────────────────→
ServerHello + Finished + response
   ←────────────────────
```

Saves 1 RTT for repeat visitors. Used by HTTP/3, QUIC.

**Risk**: replay attacks. The same 0-RTT request could be replayed. Use ONLY for idempotent operations (GET).

## Certificate Verification

Server presents cert + chain. Client verifies:
1. Cert signed by trusted CA (chain leads to root in trust store)
2. Cert hostname matches SNI (CN or SAN)
3. Cert not expired
4. Cert not revoked (CRL or OCSP)

## SNI

ClientHello has unencrypted server_name. Allows one IP to host many certs.

Privacy concern: ISPs can see what site you're visiting. ESNI / ECH (Encrypted Client Hello) addresses this.

## Session Resumption (TLS 1.2)

- Session ID-based: server caches session state
- Session ticket-based (RFC 5077): server gives client encrypted state; stateless

TLS 1.3 uses Pre-Shared Keys (PSK) for resumption.

## Debugging

```bash
openssl s_client -connect example.com:443 -servername example.com -tls1_3 -showcerts
# Look for "Protocol:" "Cipher:" lines
```

```bash
curl -v https://example.com 2>&1 | grep -i "tls\|cipher\|protocol"
```

Wireshark with private key can decrypt; use SSLKEYLOGFILE env var with browsers.

## Performance

| | Cost |
|---|---|
| TLS 1.2 handshake | 2 RTT + crypto |
| TLS 1.3 handshake | 1 RTT + crypto |
| 0-RTT resumption | 0 RTT (request piggybacks ClientHello) |
| Bulk encryption (AES-GCM with AES-NI) | ~negligible |

For a 100ms RTT path, TLS 1.3 saves 100ms on first request.

## Common Mistakes

- **Using 0-RTT early data for non-idempotent requests**: 0-RTT is replayable. Restrict it to safe/idempotent operations (GET); a replayed POST can double-charge or duplicate a write.
- **Misdiagnosing SNI/hostname mismatches**: a cert valid for `example.com` served to a request for `api.example.com` fails name verification. Always pass `-servername` to `openssl s_client`, or it omits SNI and you debug the wrong cert.
- **Shipping an incomplete certificate chain**: leaving out an intermediate works in browsers that cache it but fails for fresh clients and many programmatic ones. Always serve leaf + intermediates (not the root).
- **Assuming TLS hides the destination**: SNI is sent in plaintext in the ClientHello, so the hostname is visible on the wire. Only ECH (Encrypted Client Hello) closes that gap.
- **Treating expiry/revocation as edge cases**: expired certs and missing OCSP/CRL handling are among the most common production TLS outages. Monitor and auto-renew.
- **Expecting TLS 1.3 to negotiate old key-exchange/cipher tricks**: 1.3 mandates ECDHE (forward secrecy) and removed RSA key exchange, RC4, 3DES, and SHA-1 — clients pinned to those fail to connect.

## Best Practices

- **Default to TLS 1.3** (fall back to 1.2 only for legacy clients); disable TLS 1.0/1.1 and weak ciphers entirely.
- **Require forward secrecy (ECDHE)** so a future private-key compromise can't decrypt past captured traffic.
- **Automate certificate lifecycle** (ACME/Let's Encrypt, ACM) with renewal well before expiry, and alert on approaching expiry independently.
- **Serve the full chain and enable OCSP stapling** to cut a revocation round-trip and avoid soft-fail gaps.
- **Set HSTS** (`Strict-Transport-Security`) to force HTTPS and prevent downgrade/stripping; consider ECH/ESNI where supported to protect the visited hostname.
- **Gate 0-RTT to idempotent requests** at the server, or disable it where replay risk is unacceptable.

## Quick Refs

Handshake RTTs: TLS 1.2 = 2 · TLS 1.3 = 1 · TLS 1.3 0-RTT = 0 (resumption, replay-risky). TLS 1.3 = mandatory ECDHE (forward secrecy), 5 cipher suites, encrypted handshake.

TLS 1.3 cipher suites: `TLS_AES_128_GCM_SHA256` · `TLS_AES_256_GCM_SHA384` · `TLS_CHACHA20_POLY1305_SHA256` (+ two CCM). Cert checks: chain to trusted root · hostname (SNI/SAN) · validity dates · revocation (OCSP/CRL).

```bash
# Inspect protocol, cipher, and cert chain
openssl s_client -connect example.com:443 -servername example.com -tls1_3 -showcerts </dev/null

# Check certificate expiry
echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null \
  | openssl x509 -noout -dates -subject -issuer

# Negotiated version/cipher via curl
curl -v https://example.com 2>&1 | grep -iE 'SSL connection|TLS|cipher|ALPN'

# Decrypt in Wireshark
SSLKEYLOGFILE=/tmp/keys.log chromium https://example.com
```

## Interview Prep

**Mid**: "Walk through TLS 1.3 handshake."

**Senior**: "What's 0-RTT and what's the risk?"

**Staff**: "How does TLS 1.3 achieve forward secrecy?"

## Next Topic

→ [T03 — HTTP/2 Multiplexing & Server Push](T03-HTTP2.md)
