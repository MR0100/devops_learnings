# L24/C06 — TLS Termination Patterns

## Topics

- **T01 Edge Termination** — Terminate at LB
- **T02 Re-Encryption to Backend** — Terminate, re-encrypt
- **T03 SNI Routing** — Multiple certs per IP

## TLS Termination Options

### Option 1: Edge Termination (most common)
```
Client ─ TLS ─ LB ─ HTTP ─ Backend
```
- LB decrypts; backend gets plain HTTP
- Saves backend CPU
- Internal network must be trusted (or use private subnet)

### Option 2: TLS Passthrough
```
Client ─ TLS ─ LB ─ TLS ─ Backend
```
- LB doesn't decrypt; just forwards encrypted bytes
- Use for: backend needs to see client cert (mTLS); or LB can't decrypt for compliance
- LB can't make L7 decisions (URL-based routing impossible)

### Option 3: Re-encryption (Bridging)
```
Client ─ TLS ─ LB ─ TLS ─ Backend
```
- LB decrypts; inspects; re-encrypts to backend
- Best of both: L7 routing + encrypted transit
- Used for: PCI, compliance, defense in depth, K8s mTLS to backends

### Option 4: Cleartext Internal (Plain HTTP)
```
Client ─ TLS ─ LB ─ HTTP ─ Backend
```
- Same as Option 1; the most common
- Acceptable if internal network is private + audited

## When Each

| Need | Pick |
|---|---|
| Simple, fast, internal trust | Edge termination + HTTP backend |
| Compliance / Zero Trust | Re-encryption (bridging) |
| Backend needs client cert | Passthrough OR pass header |
| Backend is TCP (not HTTP) | Passthrough |
| Maximum performance + L7 routing | Re-encryption with TLS 1.3 |

## SNI (Server Name Indication)

Multiple TLS certs on one IP. Client tells server which cert to use via SNI extension in ClientHello.

```
Client: ClientHello, SNI = "api.example.com"
Server: presents cert for api.example.com

Same IP can serve:
- api.example.com
- portal.example.com
- admin.example.com
each with separate cert.
```

Now standard; pre-SNI required one IP per cert (IPv4 scarcity problem).

### SNI Routing
LB can route to different backends based on SNI:
```yaml
# Envoy SNI routing
filter_chains:
  - filter_chain_match:
      server_names: ["api.example.com"]
    filters: ...  # route to api backend
  - filter_chain_match:
      server_names: ["portal.example.com"]
    filters: ...  # route to portal backend
```

### Encrypted Client Hello (ECH)
Future: encrypt SNI so on-path observers can't see which site you're visiting. Slowly being adopted.

## ALPN (Application-Layer Protocol Negotiation)

Negotiate L7 protocol during TLS handshake.
```
Client: ClientHello, ALPN = [h2, http/1.1]
Server: ServerHello, ALPN = h2     # we'll use HTTP/2
```

Used to negotiate HTTP/2 over TLS without an upgrade dance.

`h3` for HTTP/3 over QUIC.

## TLS Mutual Auth (mTLS)

Server verifies client's cert too. Either side can be the "client" or "server" depending on context.

Used in:
- Service-to-service auth in service mesh (Istio, Linkerd)
- API access where every caller has a cert
- Zero Trust networks (BeyondCorp model)
- K8s API server ↔ kubelet

### Cert Distribution
- cert-manager (K8s) with CA issuer
- SPIFFE / SPIRE
- Vault PKI engine

## Certificate Rotation

Short-lived certs (24h, 7d, 90d) require automation:
- Let's Encrypt via cert-manager (90-day default)
- Istio rotates per-pod certs every 24h
- Vault PKI: minutes to hours

### Hot Reload
LBs need to load new certs without restart:
- Nginx: `nginx -s reload`
- HAProxy: socket commands or runtime
- Envoy: xDS update (no restart)

## Cipher Suites

TLS 1.3 simplified greatly (5 suites). TLS 1.2 had hundreds.

Modern policy:
- TLS 1.2 minimum (or 1.3 only for new)
- AEAD ciphers only (AES-GCM, ChaCha20-Poly1305)
- Forward secrecy (ECDHE)
- No RSA key exchange (no forward secrecy)
- No CBC mode (vulnerable to padding attacks)

### Check Your Site
```bash
testssl.sh example.com
sslyze --regular example.com
nmap --script ssl-enum-ciphers -p 443 example.com
```

## Common Mistakes

- TLS 1.0 / 1.1 still enabled (vulnerable to BEAST etc.)
- Self-signed certs in prod (clients see warnings)
- Cert expired (mass outage)
- Cert name mismatch (CN/SAN missing host)
- Intermediate CA not served (clients can't validate chain)
- Wildcard cert for too many subdomains (compromise blast radius)
- No HSTS header (clients can be downgraded)

## HSTS

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

Tells browsers: ONLY ever talk HTTPS to this domain for the next year.

## Certificate Transparency

All public CAs log certs to CT logs. Misissuance detectable.
- crt.sh — search CT logs

## Interview Themes

- "TLS termination patterns"
- "SNI — what does it solve?"
- "When passthrough vs re-encryption?"
- "Modern cipher suite policy"
- "Cert rotation at scale"
