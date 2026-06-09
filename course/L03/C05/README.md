# L03/C05 — TLS / SSL Deep Dive

## Chapter Overview

TLS underpins every secure connection. Understanding its mechanics — and its failure modes — is essential for ops, debugging, and security architecture.

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Crypto-Basics.md) | Symmetric vs Asymmetric Cryptography | 1 hr |
| [T02](T02-Certificates.md) | Certificates, CAs, Chains of Trust | 1 hr |
| [T03](T03-mTLS.md) | mTLS (Mutual TLS) | 0.5 hr |
| [T04](T04-Cipher-Suites.md) | Cipher Suites, Forward Secrecy | 1 hr |
| [T05](T05-ACME-Cert-Rotation.md) | Certificate Rotation & ACME (Let's Encrypt) | 0.5 hr |

## Crypto Building Blocks

### Symmetric
- Same key for encrypt and decrypt (AES, ChaCha20)
- Fast (CPU has dedicated instructions)
- Problem: how do you share the key?

### Asymmetric
- Public key encrypts, private decrypts (RSA, ECDH)
- Slow (~1000× symmetric)
- Solves key exchange but not bulk encryption

### TLS Combines Both
1. Asymmetric: handshake to establish a shared symmetric key
2. Symmetric: bulk encryption of application data

## Certificates and Chains

A certificate binds a public key to an identity (CN or SAN), signed by a CA.

```
Root CA Cert (self-signed, in OS/browser trust store)
   ↓ signs
Intermediate CA Cert
   ↓ signs
End-Entity (Leaf) Cert
   ↓
Server presents Leaf + Intermediate(s) (NOT root)
```

Browser/client validates: leaf → intermediate → root in trust store.

### Certificate Contents

- Subject: CN (Common Name, deprecated) + SAN (Subject Alternative Name, modern)
- Issuer: who signed
- Validity: notBefore, notAfter
- Public key
- Signature
- Extensions: KeyUsage, ExtendedKeyUsage (TLS Web Server, Client Auth), SAN

### SAN > CN
Modern browsers IGNORE CN and require SAN. Multiple SANs allow one cert for multiple names.

## Cipher Suites

A cipher suite encodes algorithm choices:

```
TLS_AES_256_GCM_SHA384            (TLS 1.3 — only 5 suites total)
TLS_CHACHA20_POLY1305_SHA256      (TLS 1.3)
TLS_AES_128_GCM_SHA256            (TLS 1.3)

TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384   (TLS 1.2 — many combinations)
└────┬───┘ └─┬─┘ └──────┬──────┘ └──┬──┘
     │      │           │           │
   KX      Auth        Cipher       MAC
```

TLS 1.3 simplifies: only AEAD (Authenticated Encryption with Associated Data) ciphers; key exchange is implicit (always ECDHE).

## Forward Secrecy

If the server's long-term private key is compromised tomorrow, can past traffic be decrypted?
- **Without FS**: yes (RSA key exchange)
- **With FS**: no (ECDHE generates ephemeral session keys)

TLS 1.3 mandates FS. TLS 1.2 needs ECDHE cipher suite.

## mTLS (Mutual TLS)

Both client AND server present certs. Server validates client's cert too.

Used for:
- Service-to-service auth in service mesh (Istio, Linkerd)
- Zero trust networks (BeyondCorp)
- API gateway → backend auth
- Kubernetes API server ↔ kubelet

Operationally hard at scale (cert lifecycle for many services) — service meshes solve this.

## SNI (Server Name Indication)

Without SNI, a server could only host one TLS cert per IP. SNI puts the hostname in the (unencrypted) ClientHello.

ESNI / ECH (Encrypted Client Hello) — encrypts SNI to hide which site you're visiting (privacy).

## ALPN (Application-Layer Protocol Negotiation)

Client and server negotiate the L7 protocol during TLS handshake:
- `h2` for HTTP/2
- `h3` for HTTP/3
- `http/1.1` for HTTP/1.1

Used by Envoy, browsers, gRPC.

## Certificate Lifecycle

1. **Generate** private key + Certificate Signing Request (CSR)
2. **Submit** CSR to CA (proves domain ownership via HTTP-01, DNS-01, or TLS-ALPN-01)
3. **Receive** signed cert
4. **Install** on server
5. **Renew** before expiry
6. **Revoke** if compromised (via CRL or OCSP — both unreliable)

### ACME (Let's Encrypt)
Automates the entire flow. Tools: `certbot`, `lego`, cert-manager (K8s).

- 90-day cert lifetime forces automation
- Free
- Rate limits per domain
- Production must use staging environment for testing

### cert-manager (K8s)

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: example-com-tls
  namespace: default
spec:
  secretName: example-com-tls
  dnsNames:
  - example.com
  - www.example.com
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
```

cert-manager auto-renews before expiry, rotates the K8s Secret, and the ingress controller picks up the new cert.

## Common TLS Issues

| Symptom | Likely Cause |
|---|---|
| "Cert expired" | Missed renewal |
| "Cert name mismatch" | SAN doesn't include the hostname accessed |
| "Untrusted CA" | Intermediate not served, or self-signed in untrusted store |
| "Protocol mismatch" | Old TLS 1.0/1.1 disabled |
| "Handshake failure" | Cipher mismatch, no overlap |
| Very slow handshake | TLS 1.0/1.2 with no session resumption |
| Random connection resets | Middlebox interference (rare) |

## Debugging Tools

```bash
openssl s_client -connect example.com:443 -servername example.com -showcerts
openssl x509 -in cert.pem -noout -text
openssl x509 -in cert.pem -noout -dates       # expiry
openssl x509 -in cert.pem -noout -fingerprint -sha256

nmap --script ssl-enum-ciphers -p 443 example.com   # what's supported
testssl.sh example.com                                # comprehensive
sslyze example.com:443
curl -v https://example.com 2>&1 | grep -i tls
```

## Interview Themes

- "Walk me through the TLS 1.3 handshake"
- "What is forward secrecy?"
- "Compare TLS 1.2 and TLS 1.3"
- "How does cert-manager work?"
- "Explain mTLS and where it's used"
- "Why was SNI added?"
- "Design cert rotation for 10K microservices"
