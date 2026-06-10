# L13/C19/T03 — Certificate Rotation

## Learning Objectives

- Manage internal + external certs
- Rotate before expiry

## K8s Certs

Many certs in cluster:
- API server cert + key
- etcd peer + server certs
- kubelet client + server certs
- Front-proxy certs
- Service Account signing key
- CA

Default validity: 1 year for most.

## Self-Managed (kubeadm)

Check expiration:
```bash
kubeadm certs check-expiration
# CERTIFICATE                EXPIRES                  RESIDUAL TIME
# admin.conf                 Jun 09, 2026 10:00 UTC   365d
# apiserver                  Jun 09, 2026 10:00 UTC   365d
# apiserver-etcd-client      ...
# ...
```

## Renew

```bash
kubeadm certs renew all
# Or specific
kubeadm certs renew apiserver
```

Renews; restarts components as needed.

Or auto-renew on upgrade.

## Auto-Rotation

kubelet auto-rotates its certs:
```yaml
# kubelet config
rotateCertificates: true
serverTLSBootstrap: true
```

Default for modern K8s.

## CA Rotation

Most critical:
- Year 5+: CA expires (default 10 yr)
- Need migration

For: complex; plan ahead.

```bash
kubeadm certs renew --csr-only --csr-dir /tmp/csr
# Generates CSR; sign with new CA
```

## Managed K8s

EKS / GKE / AKS:
- Provider rotates internal certs
- Transparent
- You handle external (Ingress) certs

## External Certs (Ingress)

For TLS termination at Ingress.

### Manual
```bash
openssl req ...
kubectl create secret tls my-tls --cert=tls.crt --key=tls.key
```

Renew before expiry; recreate secret.

### cert-manager

Automatic ACME (Let's Encrypt):
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: me@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

Ingress:
```yaml
metadata:
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts: [app.example.com]
    secretName: app-tls
```

cert-manager auto-issues + auto-renews.

## DNS01 Challenge

For wildcard certs or where HTTP01 not feasible:
```yaml
solvers:
- dns01:
    route53:
      region: us-east-1
      hostedZoneID: ...
```

Requires DNS provider credentials.

## ACME Providers

- Let's Encrypt (free)
- ZeroSSL (free)
- Sectigo, DigiCert (paid)

For prod: Let's Encrypt works.

## cert-manager Components

- cert-manager controller
- webhook (validates Certificate CRs)
- cainjector (injects CA bundles)

## Monitoring

Alert on expiring:
```yaml
- alert: CertExpiringSoon
  expr: probe_ssl_earliest_cert_expiry - time() < 86400 * 14
  for: 5m
```

14 days before expiry.

cert-manager metrics:
- certmanager_certificate_expiration_timestamp_seconds

Alert if < 30 days.

## Service Account Tokens

Pre-1.21: Secrets with long-lived tokens.
Modern (1.21+): projected volumes; short-lived; auto-rotating.

For modern: no rotation needed.

## ETCD Certs

Separate from API server certs. Renew similarly:
```bash
kubeadm certs renew etcd-server
kubeadm certs renew etcd-peer
```

Restart etcd after.

## Internal vs External

Internal (cluster-internal):
- Managed by kubeadm / managed service
- Often auto-rotated

External (Ingress, gateways):
- Managed by you / cert-manager
- Often ACME-based

## Pre-Production Test

Renew in staging first:
- Verify no API outage
- Components restart cleanly
- App still works

Then prod.

## Procedure (Self-Managed)

For all control plane nodes:
```bash
# Backup
cp -r /etc/kubernetes/pki /etc/kubernetes/pki.bak

# Renew
kubeadm certs renew all

# Restart static pods (they detect cert change)
mv /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/
sleep 30
mv /tmp/kube-apiserver.yaml /etc/kubernetes/manifests/
# kubelet restarts
```

Verify:
```bash
kubectl get nodes
kubeadm certs check-expiration
```

## Kubeconfig

Admin kubeconfig also has cert:
```bash
kubectl config view --raw -o jsonpath='{.users[0].user.client-certificate-data}' | base64 -d | openssl x509 -text -noout | grep "Not After"
```

After cert renewal: regenerate kubeconfig:
```bash
cp /etc/kubernetes/admin.conf ~/.kube/config
```

## Long-Validity Certs

For some use cases (kubelet bootstrap):
- Longer-validity certs
- Less rotation overhead

But: violates best practice.

For: prefer short + auto-rotation.

## Trust Distribution

For mTLS across services:
- Pods need updated CA bundles
- cert-manager + cainjector handles

For: complex setups (mesh, custom).

## Webhook Certs

Admission / conversion webhooks need TLS:
- cert-manager.io/inject-ca-from annotation
- cainjector auto-updates

Common pattern with operators.

## Best Practices

- Monitor expiration (alert 30 days out)
- Auto-renewal where possible
- Test renewal in non-prod
- Document procedure
- Backup certs before renewal
- cert-manager for external

## Common Mistakes

- Forgetting to monitor
- Certs expire during incident → bigger incident
- Manual rotation without testing
- No backup before renewal

## Disaster: Cert Expired

If API cert expired:
```
Unable to connect to the server: x509: certificate has expired
```

Recovery:
```bash
kubeadm certs renew all
# Restart kube-apiserver
```

For weeks-old expiration: longer process.

## Common Cert Issues

- Wrong CA in client config
- Cert/key mismatch
- Time skew (cert "not yet valid")
- Long DNS propagation (DNS01)

## Monitoring Probes

blackbox_exporter:
```yaml
- job_name: 'blackbox'
  metrics_path: /probe
  params:
    module: [http_2xx]
  static_configs:
  - targets:
    - https://api.example.com
  relabel_configs:
  ...
```

Probes cert expiry.

## Quick Refs

```bash
# kubeadm
kubeadm certs check-expiration
kubeadm certs renew all

# cert-manager
kubectl get certificate -A
kubectl describe certificate my-cert
kubectl get clusterissuer

# Inspect cert
openssl x509 -in cert.crt -text -noout
openssl s_client -connect host:443 -showcerts
```

## Interview Prep

**Mid**: "K8s certs."

**Senior**: "cert-manager flow."

**Staff**: "Org-wide cert lifecycle."

## Next Topic

→ [T04 — Capacity Planning](T04-Capacity-Planning.md)
