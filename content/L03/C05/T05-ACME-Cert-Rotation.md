# L03/C05/T05 — Certificate Rotation & ACME (Let's Encrypt)

## Learning Objectives

- Use ACME protocol via Let's Encrypt
- Automate cert rotation at scale
- Choose validation challenge types

## ACME Protocol

Automated Certificate Management Environment (RFC 8555).
- Standardized issuance flow
- Used by Let's Encrypt, ZeroSSL, BuyPass, more
- Free public CAs

## Validation Challenges

CA must verify you control the domain. Three methods:

### HTTP-01
CA tells you to put a file at `http://domain/.well-known/acme-challenge/TOKEN`. CA fetches.
- Easy
- Requires HTTP server running
- Works for individual domains; not wildcards

### DNS-01
CA tells you to add a TXT record `_acme-challenge.domain`. CA queries DNS.
- Works for wildcards
- Requires DNS API access (Route 53, Cloudflare API)
- Slower (DNS propagation)

### TLS-ALPN-01
TLS-based, using ALPN. Less common.

## Let's Encrypt Limits

- 90-day cert validity (forces automation)
- 50 certs per registered domain per week
- 5 duplicate certs per week
- Free; supported by donations

## Tools

### Certbot
Reference client. Easy on Linux servers:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d example.com -d www.example.com
```

Auto-modifies nginx; sets up renewal cron.

### cert-manager (K8s)
Most common in K8s:
```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: example-com-tls
spec:
  secretName: example-com-tls
  dnsNames:
    - example.com
    - www.example.com
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer

---
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    email: admin@example.com
    server: https://acme-v02.api.letsencrypt.org/directory
    privateKeySecretRef:
      name: letsencrypt-prod-account-key
    solvers:
      - http01:
          ingress:
            class: nginx
```

### lego (Go)
Library + CLI; supports many providers.

### Caddy
Web server with built-in ACME. Zero-config:
```caddy
example.com {
    reverse_proxy backend:8080
}
```

Caddy gets a Let's Encrypt cert and auto-renews.

## Internal CA + ACME

For internal services, you can run private ACME:
- **Smallstep step-ca**: internal ACME server
- **Boulder**: Let's Encrypt's server (OSS)

Pair with cert-manager for K8s-style automation.

## Cert Rotation Automation

```
30 days before expiry → renew
20 days before → second attempt if first failed
Daily checks → alert if cert < 14 days from expiry
```

cert-manager handles automatically. Self-managed: cron + certbot.

## Hot Reload on Renewal

After renewing cert:
- Nginx: `nginx -s reload` (SIGHUP)
- Apache: `apachectl graceful`
- HAProxy: `systemctl reload haproxy`
- Custom apps: SIGHUP + re-read cert file

K8s with cert-manager: Secret updated → ingress controller auto-reloads.

## Wildcard Certs

Cover all subdomains: `*.example.com` matches `www`, `api`, `app`, but not the apex or nested.

Use DNS-01 challenge (HTTP-01 doesn't work for wildcards).

## Best Practices

- **Monitor expiry**: alert at 30/14/7 days remaining
- **Automate everything**: no manual cert ops
- **Test rotation**: actually renew, don't just check the system "should"
- **Backup CA-issued certs**: in case of CA outage
- **Multiple CAs**: subscribe to backup (ZeroSSL, BuyPass) for redundancy
- **OCSP Stapling**: server includes OCSP response

## Common Issues

- **Rate limit hit**: scripted retries during testing → blocked from issuance
- **DNS-01 propagation**: cert-manager retries; can take time
- **Webroot mismatch**: HTTP-01 challenge file not served at right URL
- **CAA records block CA**: domain's CAA only allows X; you're trying Y
- **Account key lost**: have to register new account

## Monitoring

```bash
# Days until expiry
echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null | \
  openssl x509 -noout -enddate | cut -d= -f2

# All certs in K8s
kubectl get certs -A | awk 'NR>1 {print $1, $2, $3}'
```

Prometheus exporter: `prometheus-cert-exporter` or `blackbox_exporter` with TLS probe.

## Migration Path

If you have manually-managed certs:
1. Install cert-manager / certbot
2. Test on staging
3. Migrate one service at a time
4. Remove old cert files
5. Verify monitoring

Eventually: no human ever touches certs again.

## Common Mistakes

- **Testing against the production ACME endpoint** — burns rate limits (50 certs/registered-domain/week). Use the **staging** directory until the flow works.
- **Using HTTP-01 for a wildcard** — it can't validate `*.example.com`; wildcards require **DNS-01**.
- **CAA record blocks the CA** — a `CAA` record permitting only one issuer silently fails issuance from any other; check `dig CAA example.com`.
- **Renewing but not reloading** — the cert on disk is fresh but the running process still holds the old one; wire a reload into the renewal hook.
- **Losing the ACME account key** — back it up; losing it means re-registering and re-authorizing every domain.
- **Port 80 closed for HTTP-01** — the challenge fetch is over plain HTTP; blocking 80 breaks renewal even though the site runs on 443.

## Quick Refs

```bash
# Certbot against STAGING (no rate-limit risk)
certbot certonly --staging --nginx -d example.com

# Dry-run a real renewal of everything
certbot renew --dry-run

# DNS-01 wildcard issuance (manual or via DNS plugin)
certbot certonly --manual --preferred-challenges dns -d '*.example.com' -d example.com

# Days until expiry for a live host
echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null \
  | openssl x509 -noout -enddate

# Is a CAA record blocking my CA?
dig +short CAA example.com

# cert-manager: why is a cert stuck?
kubectl describe certificate <name>
kubectl describe certificaterequest    # shows the ACME order/challenge state
kubectl get challenges -A
```

Challenge picker: **HTTP-01** = simplest, single host, needs port 80; **DNS-01** = required for wildcards and works without inbound ports, needs DNS API creds; **TLS-ALPN-01** = port 443 only, niche.

## Interview Prep

**Mid**: "ACME — what is it?"

**Senior**: "Cert rotation strategy for 1000 services?"

**Staff**: "Wildcard via DNS-01 challenge — automate."

## Next Chapter

→ [C06 — Network Troubleshooting](../C06/README.md)
