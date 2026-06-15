# L24/C06/T02 — Re-Encryption to Backend

## Learning Objectives

- Use re-encryption
- End-to-end TLS

## Re-Encryption

Terminate TLS at edge; re-encrypt to backend:

```
Browser ←TLS→ Edge ←TLS→ Backend
```

Edge sees plaintext briefly.

## Why

- Compliance (e2e encryption)
- Untrusted internal network
- Zero trust
- Defense in depth

## Setup (Nginx)

```nginx
location / {
    proxy_pass https://backend:8443;
    proxy_ssl_verify on;
    proxy_ssl_trusted_certificate /etc/ssl/ca.crt;
}
```

## ALB

```bash
# Target group: HTTPS
aws elbv2 create-target-group --protocol HTTPS --port 8443
```

ALB re-encrypts.

## Service Mesh

Istio / Linkerd:
- mTLS between sidecars
- Internal traffic encrypted
- Auto

(See L14.)

## End-to-End

```
Browser ←TLS→ Edge ←TLS→ Backend (decrypts)
```

Or:
```
Browser ←TLS→ TCP pass-through → Backend (decrypts)
```

Pass-through: edge doesn't see plain.

## TCP Pass-Through

LB only:
- No L7 inspection
- No HTTP routing
- E2E encryption

For: max security, less features.

## SNI Pass-Through

LB sees SNI; routes; doesn't decrypt:
```
Browser → LB → backend by SNI host
   (LB doesn't decrypt)
```

For: multi-tenant; e2e.

## Performance

Re-encryption:
- CPU on both sides
- Minor latency
- < 5% impact typical

## Backend Cert

Internal CA:
- Private CA
- Cert per service

Or:
- Service mesh issues (Istio, SPIRE)

## Mutual TLS

Backend verifies edge cert too:
```nginx
proxy_ssl_certificate /etc/ssl/client.crt;
proxy_ssl_certificate_key /etc/ssl/client.key;
```

For: zero trust.

## Cert Rotation

Service mesh: auto.
Manual: hard. Automate.

## Cost

- More CPU
- More cert management
- More complexity

For: justify with compliance / security.

## When E2E

- Regulated (PCI-DSS, HIPAA)
- Untrusted multi-tenant
- High-value data

## When Edge Only

- Internal trusted network
- Performance critical
- Lower threat

## Best Practices

- Service mesh for internal mTLS
- Internal CA
- Short cert TTL
- Cipher modern

## Common Mistakes

- Cert verify off (MITM risk)
- Long cert TTL
- Mix encryption strategies (some plain, some not)

## Quick Refs

```nginx
proxy_pass https://backend;
proxy_ssl_verify on;
proxy_ssl_certificate ...
```

```bash
# Service mesh: auto mTLS
istioctl install
```

## Interview Prep

**Mid**: "Re-encryption."

**Senior**: "E2E TLS."

**Staff**: "TLS architecture."

## Next Topic

→ [T03 — SNI Routing](T03-SNI-Routing.md)
