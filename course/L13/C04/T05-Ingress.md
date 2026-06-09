# L13/C04/T05 — Ingress Controllers (Nginx, Traefik, HAProxy, AWS ALB)

## Learning Objectives

- Configure Ingress
- Pick controller

## Ingress

L7 routing for HTTP/HTTPS:
- Path / host based
- TLS termination
- One LB; many services

vs LoadBalancer Service (per service LB; expensive).

## Ingress vs Ingress Controller

Ingress: K8s resource (routing rules).
Ingress Controller: pod that watches Ingress + implements (nginx, ALB, etc.).

Must install controller separately.

## Ingress Resource

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  tls:
  - hosts: [app.example.com]
    secretName: app-tls
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-svc
            port:
              number: 80
      - path: /web
        pathType: Prefix
        backend:
          service:
            name: web-svc
            port:
              number: 80
```

## Path Types

- **Exact**: `/foo` → matches `/foo` only
- **Prefix**: `/foo` → matches `/foo`, `/foo/`, `/foo/bar`
- **ImplementationSpecific**: controller decides

## Host Rules

```yaml
rules:
- host: api.example.com
  http:
    paths:
    - path: /
      pathType: Prefix
      backend:
        service:
          name: api
          port: {number: 80}

- host: web.example.com
  http:
    paths:
    - path: /
      pathType: Prefix
      backend:
        service:
          name: web
          port: {number: 80}
```

Wildcard:
```yaml
host: "*.example.com"
```

## TLS

```yaml
spec:
  tls:
  - hosts:
    - app.example.com
    secretName: app-tls    # Secret with tls.crt and tls.key
```

cert-manager auto-provisions Let's Encrypt:
```yaml
metadata:
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
```

## Controllers

### Nginx Ingress
Most popular OSS:
- Many annotations
- Powerful
- Mature

```bash
helm install nginx-ingress ingress-nginx/ingress-nginx
```

### Traefik
Modern; cloud-native:
- Auto-discovery
- Let's Encrypt built-in
- Dashboard

### HAProxy
Performance-focused. Less common in K8s; popular for legacy.

### AWS Load Balancer Controller (ALB)
AWS-managed:
- Creates real ALB
- Integrates with WAF, ACM
- Per-Ingress = one ALB (or IngressGroup for shared)

```yaml
annotations:
  kubernetes.io/ingress.class: alb
  alb.ingress.kubernetes.io/scheme: internet-facing
  alb.ingress.kubernetes.io/target-type: ip
```

### Cilium Ingress
eBPF-based; no separate controller.

### Contour, Gloo, Kong, etc.
Various; each with strengths.

## IngressClassName

```yaml
spec:
  ingressClassName: nginx
```

Specifies which controller. For multi-controller cluster.

## Annotations

Per controller; non-portable.

### Nginx
- `nginx.ingress.kubernetes.io/rewrite-target: /`
- `nginx.ingress.kubernetes.io/ssl-redirect: "true"`
- `nginx.ingress.kubernetes.io/rate-limit: "100"`
- `nginx.ingress.kubernetes.io/cors-allow-origin: "*"`

### ALB
- `alb.ingress.kubernetes.io/scheme: internet-facing`
- `alb.ingress.kubernetes.io/listen-ports: '[{"HTTPS":443}]'`
- `alb.ingress.kubernetes.io/certificate-arn: arn:...`
- `alb.ingress.kubernetes.io/group.name: my-group` (share ALB)

## Sharing ALB

For ALB controller:
```yaml
annotations:
  alb.ingress.kubernetes.io/group.name: shared
  alb.ingress.kubernetes.io/group.order: "1"
```

Multiple Ingresses → one ALB. Cost savings.

## Comparison

| | Nginx | Traefik | ALB | Cilium |
|---|---|---|---|---|
| Open source | Yes | Yes | Bundled w/ AWS | Yes |
| Cloud-native | OK | Strong | AWS | Strong |
| Performance | Strong | Strong | Native | Strongest |
| Annotations | Many | Many | Many | Different model |
| Cost | Free | Free | ALB fees | Free |
| Setup | Easy | Easy | Medium | More |

For AWS: ALB controller.
For multi-cloud: Nginx / Traefik.
For perf: Cilium.

## HTTPS Setup

1. Get cert (cert-manager, ACM, manual)
2. Create Secret (TLS type)
3. Ingress references Secret in `tls`

For ALB: use ACM cert ARN annotation (no K8s Secret).

## cert-manager

Auto-issues / renews certs (Let's Encrypt, Vault, etc.):
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
annotations:
  cert-manager.io/cluster-issuer: letsencrypt-prod
```

Auto: cert issued; renewed; Secret updated.

## Multi-Tenant

Per-team Ingresses + RBAC. Annotations isolate.

Or per-team Ingress Controller (more isolation).

## Performance

For high-traffic:
- HPA on controller pods
- Tune Nginx config (worker_processes, keepalive)
- Sized appropriately

## Monitoring

Metrics (Prometheus):
- Request count
- Latency
- Error rate
- Connections

For controllers exposing:
```yaml
spec:
  ports:
  - name: metrics
    port: 10254
```

ServiceMonitor / annotation for Prom scrape.

## Common Issues

### 502 Bad Gateway
Backend not ready / not reachable.

Check:
- Service endpoints
- Pod readiness
- Network policy
- Path / port match

### 503 Service Unavailable
No backends. Pods not ready.

### Slow Response
- Backend slow
- Connection limits
- DNS resolution slow in cluster

## Anti-Patterns

- Single huge Ingress for all (hard to manage)
- No TLS
- Wide CORS
- No rate limit
- No monitoring

## Best Practices

- One Ingress per app (separated)
- Shared ALB via IngressGroup
- cert-manager for HTTPS
- WAF in front
- Rate limit
- Monitoring
- HPA on controller

## When NOT Ingress

- Non-HTTP (TCP, UDP) → use NLB Service
- Internal-only → could be Service ClusterIP
- Simple single service → LoadBalancer Service

## Future: Gateway API

Gateway API replaces Ingress (covered T06):
- Better separation (Gateway, GatewayClass, HTTPRoute)
- More flexible
- Standard across controllers

Modern K8s: consider Gateway API for new.

## kubectl Commands

```bash
kubectl get ingress
kubectl describe ingress my-ingress
kubectl get ingressclass

# Logs of controller
kubectl logs -n ingress-nginx <controller-pod>
```

## Quick Refs

```yaml
# Basic
apiVersion: networking.k8s.io/v1
kind: Ingress
spec:
  ingressClassName: nginx
  tls:
  - hosts: [app.example.com]
    secretName: app-tls
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web
            port: {number: 80}
```

## Interview Prep

**Junior**: "Ingress vs LoadBalancer Service."

**Mid**: "Path-based routing."

**Senior**: "Ingress controller choice."

**Staff**: "Multi-team Ingress strategy."

## Next Topic

→ [T06 — Gateway API (The Future of Ingress)](T06-Gateway-API.md)
