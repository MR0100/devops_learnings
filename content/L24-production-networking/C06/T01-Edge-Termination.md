# L24/C06/T01 — Edge TLS Termination

## Learning Objectives

- Terminate TLS at edge
- Trade-offs

## Edge Termination

TLS terminates at:
- CDN / LB / proxy
- Backend: plain HTTP

```
Browser ←TLS→ Edge ←HTTP→ Backend
```

## Pros

- Simple backend (no certs)
- CPU offload
- Centralized cert mgmt
- L7 features (cache, route)

## Cons

- Plain text internal
- Trust internal network
- Single point for compromise

## When OK

- VPC private
- AWS internal (somewhat trusted)
- Not regulated

## When Not

- Zero trust
- Compliance (PCI, HIPAA)
- Untrusted network

## Setup (Nginx)

```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/ssl/site.crt;
    ssl_certificate_key /etc/ssl/site.key;
    
    location / {
        proxy_pass http://backend:8080;
    }
}
```

## Setup (ALB)

```bash
aws elbv2 create-load-balancer ...
# HTTPS listener with cert
aws elbv2 create-listener --protocol HTTPS \
  --certificates CertificateArn=arn:...
# Target group: HTTP
```

## Cert Sources

- Let's Encrypt (free, auto-rotate)
- Cloud cert manager (ACM, etc.)
- Self-signed (dev)
- CA-signed (enterprise)

## ACME Auto

```yaml
# cert-manager in K8s
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt
spec:
  acme:
    email: me@example.com
    server: https://acme-v02.api.letsencrypt.org/directory
```

Auto-renew.

## TLS Version

```
ssl_protocols TLSv1.2 TLSv1.3;
```

Disable old (1.0, 1.1).

## Ciphers

```nginx
ssl_ciphers HIGH:!aNULL:!MD5;
```

Modern only.

## HSTS

```
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
```

Force HTTPS.

## OCSP Stapling

```
ssl_stapling on;
ssl_stapling_verify on;
```

For: cert revocation check.

## SSL Session

```nginx
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
```

Reuse sessions; faster.

## Best Practices

- TLS 1.2+
- Modern ciphers
- HSTS
- Auto-renew certs
- OCSP stapling
- Session reuse

## Common Mistakes

- TLS 1.0 (insecure)
- Weak ciphers
- Manual rotation (expires)
- No HSTS

## Quick Refs

```nginx
listen 443 ssl http2;
ssl_certificate ...
ssl_certificate_key ...
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
```

## Interview Prep

**Mid**: "TLS termination."

**Senior**: "Where terminate."

**Staff**: "Zero-trust TLS."

## Next Topic

→ [T02 — Re-Encryption to Backend](T02-Re-Encryption.md)
