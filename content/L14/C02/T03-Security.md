# L14/C02/T03 — Security (mTLS, AuthorizationPolicy)

## Learning Objectives

- Enforce mTLS
- Define authorization

## mTLS

Mutual TLS between sidecars:
- Each pod has identity (SPIFFE)
- Cert from istiod CA
- Auto-rotated
- Default: PERMISSIVE (both mTLS + plain accepted)

## STRICT mTLS

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: prod
spec:
  mtls:
    mode: STRICT
```

Reject non-mTLS. Stronger.

For prod: STRICT.

## PERMISSIVE

```yaml
spec:
  mtls:
    mode: PERMISSIVE
```

Accept both. For migration period.

## Disable

```yaml
spec:
  mtls:
    mode: DISABLE
```

For: specific debug. Not prod.

## Per-Workload

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: my-app
  namespace: prod
spec:
  selector:
    matchLabels:
      app: my-app
  mtls:
    mode: STRICT
```

## SPIFFE Identity

Format: `spiffe://cluster.local/ns/<NS>/sa/<SA>`

Examples:
- `spiffe://cluster.local/ns/prod/sa/frontend`
- `spiffe://cluster.local/ns/prod/sa/backend`

Issued by istiod CA.

## Cert Rotation

Default: 24h.

Tune:
```yaml
spec:
  values:
    global:
      defaultConfigOverrides:
        proxyMetadata:
          ISTIO_META_SECRET_TTL: "1h"
```

For: shorter window.

## AuthorizationPolicy

Service-to-service authz:
```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-frontend
  namespace: prod
spec:
  selector:
    matchLabels:
      app: backend
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/prod/sa/frontend"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/*"]
```

Backend only accepts from frontend SA.

## Deny

```yaml
spec:
  action: DENY
  rules:
  - from:
    - source:
        namespaces: ["dev"]
```

Block dev → prod.

## Allow-All / Deny-All

```yaml
# Allow nothing (deny-all default if AuthorizationPolicy with no rules matches)
spec:
  selector:
    matchLabels:
      app: backend
  action: ALLOW
  rules: []  # zero rules = deny

# Allow all
spec:
  action: ALLOW
  rules:
  - {}  # one empty rule = allow all
```

Default: no policy = allow all.

## Conditions

```yaml
when:
- key: request.headers[x-token]
  values: ["valid-token"]
- key: source.ip
  values: ["10.0.0.0/24"]
- key: request.auth.claims[iss]
  values: ["https://issuer.example.com"]
```

For: header / IP / JWT-based.

## JWT Validation

```yaml
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: jwt-example
spec:
  selector:
    matchLabels:
      app: api
  jwtRules:
  - issuer: "https://issuer.example.com"
    jwksUri: "https://issuer.example.com/.well-known/jwks.json"
```

Combined with AuthorizationPolicy:
```yaml
rules:
- from:
  - source:
      requestPrincipals: ["https://issuer.example.com/*"]
```

For: end-user auth.

## External Auth

Connect to external authz:
```yaml
spec:
  extensionProviders:
  - name: oauth2-proxy
    envoyExtAuthzHttp:
      service: oauth2-proxy.auth.svc.cluster.local
      port: 4180
```

Use:
```yaml
spec:
  action: CUSTOM
  provider:
    name: oauth2-proxy
```

For: complex auth.

## Multi-Cluster

mTLS works across clusters:
- Same root CA (or federated)
- SPIFFE identities consistent
- Cross-cluster traffic encrypted

## Identity Federation

External CA:
```yaml
spec:
  values:
    pilot:
      env:
        EXTERNAL_CA: ISTIOD_RA_KUBERNETES_API
```

For: corp PKI.

## Egress mTLS

Outbound to external service:
```yaml
spec:
  trafficPolicy:
    tls:
      mode: SIMPLE  # client TLS to external
```

Or MUTUAL with client cert.

## Best Practices

- mTLS STRICT in prod
- AuthorizationPolicy per service
- Default-deny pattern
- JWT for end-user
- Audit logs on
- Short cert TTL
- External CA for regulated

## Common Mistakes

- PERMISSIVE in prod forever
- No AuthorizationPolicy (anything reaches anything)
- Overly permissive rules
- No JWT validation (rely on apps)
- Skip cross-cluster identity setup

## Migration to STRICT

Stages:
1. Install mesh (PERMISSIVE)
2. All workloads injected
3. Verify mTLS traffic
4. Set to STRICT per-namespace
5. Cluster-wide STRICT

## Common Patterns

### Default Deny + Allow Specific
```yaml
# Deny all
spec:
  action: ALLOW
  rules: []
---
# Allow frontend
spec:
  action: ALLOW
  rules:
  - from:
    - source:
        principals: [".../sa/frontend"]
```

Two policies; allows only frontend.

### Per-Method
```yaml
rules:
- from:
  - source:
      principals: [".../sa/frontend"]
  to:
  - operation:
      methods: ["GET"]
- from:
  - source:
      principals: [".../sa/admin"]
  to:
  - operation:
      methods: ["GET", "POST", "DELETE"]
```

### Per-Path
```yaml
to:
- operation:
    paths: ["/api/public/*"]
```

## Telemetry / Audit

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: access-log
spec:
  accessLogging:
  - providers:
    - name: envoy
```

Logs all requests; includes principal.

For: audit, forensics.

## Compliance

PCI / HIPAA:
- mTLS strict
- Audit logs
- Authz policies
- Restrict egress
- Cert rotation

Mesh helps.

## Quick Refs

```yaml
# mTLS strict
kind: PeerAuthentication
spec: { mtls: { mode: STRICT } }

# Authz
kind: AuthorizationPolicy
spec:
  action: ALLOW
  rules:
  - from: [{ source: { principals: [...] } }]
    to: [{ operation: { methods: [...] } }]

# JWT
kind: RequestAuthentication
spec:
  jwtRules:
  - issuer: ...
    jwksUri: ...
```

## Interview Prep

**Mid**: "Istio mTLS."

**Senior**: "Authorization design."

**Staff**: "Mesh security architecture."

## Next Topic

→ [T04 — Observability](T04-Observability.md)
