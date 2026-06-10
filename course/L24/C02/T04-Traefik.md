# L24/C02/T04 — Traefik

## Learning Objectives

- Use Traefik
- Auto-discovery

## Traefik

Modern reverse proxy:
- Auto-discovers backends
- Docker / K8s / Consul integration
- Let's Encrypt auto
- Dashboard

## Install (Docker)

```bash
docker run -p 80:80 -p 8080:8080 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  traefik
```

## K8s

```bash
helm install traefik traefik/traefik
```

## Auto-Discovery

Docker:
```yaml
services:
  webapp:
    image: my-app
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.webapp.rule=Host(`app.example.com`)"
```

Traefik picks up; routes.

## K8s

IngressRoute CRD:
```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: myapp
spec:
  routes:
  - match: Host(`app.example.com`)
    kind: Rule
    services:
    - name: myapp
      port: 80
```

## Let's Encrypt

```yaml
certificatesResolvers:
  myresolver:
    acme:
      email: me@example.com
      storage: /acme.json
      httpChallenge:
        entryPoint: web
```

Auto SSL.

## Middlewares

```yaml
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: ratelimit
spec:
  rateLimit:
    average: 100
    burst: 50
```

Compose with routes.

## Dashboard

Built-in:
```
http://traefik:8080/dashboard/
```

Visual config.

## Comparison

| | Traefik | Nginx Ingress | HAProxy |
|---|---|---|---|
| Auto-discovery | yes | partial | no |
| Let's Encrypt | built-in | external | external |
| Dashboard | yes | limited | yes |
| K8s | first-class | yes | possible |
| Performance | good | better | best |

For: K8s ingress: Traefik or Nginx Ingress.

## When Traefik

- K8s + want simple
- Need ACME auto
- Dashboard valued

## When Not

- Maximum performance (Envoy / HAProxy)
- Complex routing (Envoy)

## Best Practices

- Labels / CRDs in version control
- Backup acme.json
- Dashboard secured
- Middlewares for rate limit, auth

## Common Mistakes

- Acme storage on container (lost on restart)
- Dashboard public
- No rate limit

## Quick Refs

```yaml
# Docker labels
traefik.enable=true
traefik.http.routers.X.rule=Host(`...`)

# K8s
IngressRoute / Middleware / TLSStore
```

## Interview Prep

**Mid**: "What's Traefik."

**Senior**: "Traefik vs alternatives."

## Next Topic

→ Move to [L24/C03 — API Gateway](../C03/README.md)
