# L03/C05/T02 — Certificates, CAs, Chains of Trust

## Learning Objectives

- Understand X.509 certificates
- Trace chain of trust to root CAs
- Read cert contents

## What's in a Certificate

X.509 certificate contains:
- **Subject**: CN (Common Name, deprecated) + SAN (Subject Alternative Names)
- **Issuer**: who signed
- **Validity**: notBefore, notAfter
- **Public Key**: subject's pubkey
- **Signature**: by issuer
- **Extensions**: KeyUsage, ExtendedKeyUsage, SAN, CRL/OCSP URLs

```bash
openssl x509 -in cert.pem -text -noout
```

## Chain of Trust

```
Root CA (self-signed, in OS/browser trust store)
  ↓ signs
Intermediate CA Cert
  ↓ signs
End-Entity (Leaf) Cert
  ↓
Server presents Leaf + Intermediates (NOT root)

Client validates: Leaf → Intermediate → Root (in trust store) ✓
```

Why intermediates: protects root key (root signs intermediates rarely; intermediates sign many leafs).

## SAN vs CN

Modern browsers IGNORE CN and check only SAN.

```
Subject: CN=example.com   ← ignored
X509v3 Subject Alternative Name:
  DNS:example.com, DNS:*.example.com, DNS:www.example.com
```

Multiple SANs = one cert covers multiple names.

## Wildcards

`*.example.com` matches `www.example.com`, `api.example.com`, but NOT:
- `example.com` itself (need separate SAN)
- `foo.bar.example.com` (only one level)

## EV / OV / DV

- **DV** (Domain Validated): just prove you control the domain (Let's Encrypt). Most common.
- **OV** (Organization Validated): verify org info. Costs more.
- **EV** (Extended Validation): strict org checks. Showed green address bar; mostly removed by browsers now.

For most: DV is sufficient.

## Certificate Generation

```bash
# Generate private key
openssl ecparam -name prime256v1 -genkey -noout -out key.pem

# Generate CSR (Certificate Signing Request)
openssl req -new -key key.pem -out csr.pem -subj "/CN=example.com"

# CA signs (creates cert)
# Sent CSR to CA; receive signed cert.pem
```

## Self-Signed Certs

For internal use (no CA needed):
```bash
openssl req -x509 -newkey ec -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=internal" \
  -addext "subjectAltName=DNS:internal.example.com"
```

Browsers will warn unless cert added to trust store.

## Reading Cert Details

```bash
# From file
openssl x509 -in cert.pem -text -noout

# From server
openssl s_client -connect example.com:443 -servername example.com -showcerts < /dev/null

# Just expiry
openssl x509 -in cert.pem -noout -dates

# Just fingerprint
openssl x509 -in cert.pem -noout -fingerprint -sha256

# Validate chain
openssl verify -CAfile chain.pem cert.pem
```

## Common Issues

### Missing Intermediate
Server presents leaf only. Browser doesn't find chain to trusted root. Error: "Unable to verify."

Fix: server config must include full chain (leaf + intermediates).

### Expired
Replace before notAfter date. Set up monitoring (alerts at 30/14/7 days before expiry).

### Hostname Mismatch
Cert SAN doesn't include the hostname client accessed. Add SAN or reissue.

### Self-Signed in Prod
Browsers/OS warn. Use real CA (Let's Encrypt is free).

## Certificate Stores

OS / browser maintain trust stores:
- **Mozilla NSS** (Firefox)
- **System** (Windows certmgr, macOS Keychain)
- **OpenSSL** (Linux: `/etc/ssl/certs/`)
- **Java** (cacerts in JRE)
- **Custom** (containers may not include system store)

## Adding CA to System Trust

Linux (Ubuntu):
```bash
sudo cp my-ca.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
```

## OCSP and CRL

Revocation checking:
- **CRL** (Certificate Revocation List): downloaded periodically; large
- **OCSP** (Online Cert Status Protocol): query CA per cert; privacy leak
- **OCSP Stapling**: server includes OCSP response (avoids client→CA query)

Reality: revocation checking often fails open (browsers accept if can't reach CA). Better: short-lived certs (cert-manager rotates often).

## Modern Cert Lifecycle

- Cert valid 90 days (Let's Encrypt standard)
- Renewed automatically by cert-manager / ACME client
- Forces automation (no human in the loop)

## Common Mistakes

- **Shipping the leaf only** — server omits intermediates, so clients on a fresh trust store can't build a chain. Always serve `fullchain.pem` (leaf + intermediates, root excluded).
- **Relying on CN** — modern clients ignore Common Name entirely and match only SAN. A cert with no SAN fails even if CN is correct.
- **Wrong chain order** — leaf must come first in the bundle, then intermediates leaf-to-root. Reversed order breaks some clients.
- **Wildcard over-reach** — `*.example.com` does *not* match the apex `example.com` or nested `a.b.example.com`; people forget and get hostname-mismatch errors.
- **Treating revocation as reliable** — CRL/OCSP usually fail *open*; a revoked cert may still be accepted. Lean on short-lived certs instead.
- **Leaking the private key into Git/images** — the key must never be committed; rotate immediately if it is.

## Best Practices

- Serve the **full chain** and verify it with `openssl verify -untrusted intermediates.pem leaf.pem`.
- Use **SAN with every hostname** the cert must cover; keep CN matching the primary SAN only for cosmetics.
- Adopt **short-lived certs (≤90 days) with automated renewal** (cert-manager/ACME) so revocation matters less and rotation is proven.
- **Monitor expiry** with alerts at 30/14/7 days and a probe (`blackbox_exporter` TLS probe) — expiry is the #1 preventable outage.
- Enable **OCSP stapling** so clients don't have to reach the CA, and keep an eye on the staple being fresh.
- Keep private keys at `0600`, owned by the service user, ideally non-exportable (KMS/HSM/TPM) where supported.

## Quick Refs

```bash
# Inspect a cert (subject, SANs, validity, issuer)
openssl x509 -in cert.pem -noout -text

# Just the SANs
openssl x509 -in cert.pem -noout -ext subjectAltName

# Pull the served chain from a live host
openssl s_client -connect example.com:443 -servername example.com -showcerts </dev/null

# Verify a leaf against its chain
openssl verify -CAfile root.pem -untrusted intermediates.pem leaf.pem

# Check key/cert/CSR match (modulus must be identical)
openssl x509 -noout -modulus -in cert.pem | openssl md5
openssl rsa  -noout -modulus -in key.pem  | openssl md5

# Days remaining
openssl x509 -in cert.pem -noout -enddate
```

Chain reminder: **server presents Leaf + Intermediates; client already has the Root.** Never include the root in what you serve.

## Interview Prep

**Mid**: "Walk through cert chain validation."

**Senior**: "Why are intermediates used?"

**Staff**: "Cert revocation — why is it broken?"

## Next Topic

→ [T03 — mTLS (Mutual TLS)](T03-mTLS.md)
