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

## Interview Prep

**Mid**: "Walk through cert chain validation."

**Senior**: "Why are intermediates used?"

**Staff**: "Cert revocation — why is it broken?"

## Next Topic

→ [T03 — mTLS (Mutual TLS)](T03-mTLS.md)
