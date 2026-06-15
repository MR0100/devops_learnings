# L14/C02/T02 — Traffic Management

## Learning Objectives

- Use VirtualService, DestinationRule, Gateway
- Apply traffic shifting patterns

## VirtualService

Routes traffic:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
  - reviews
  http:
  - route:
    - destination:
        host: reviews
        subset: v1
      weight: 90
    - destination:
        host: reviews
        subset: v2
      weight: 10
```

90/10 split.

## DestinationRule

Defines subsets + LB:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: reviews
spec:
  host: reviews
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
  trafficPolicy:
    loadBalancer:
      simple: ROUND_ROBIN
    connectionPool:
      tcp:
        maxConnections: 100
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
```

Subsets: filter by pod labels.

## Gateway

Ingress:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: my-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: my-cert
    hosts:
    - example.com
```

Plus binding:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: my-app
spec:
  hosts:
  - example.com
  gateways:
  - my-gateway
  http:
  - route:
    - destination:
        host: my-app
        port:
          number: 80
```

## Canary

```yaml
http:
- route:
  - destination:
      host: app
      subset: v1
    weight: 95
  - destination:
      host: app
      subset: v2
    weight: 5
```

Adjust weights over time.

## A/B by Header

```yaml
http:
- match:
  - headers:
      x-user-type:
        exact: beta
  route:
  - destination:
      host: app
      subset: v2
- route:
  - destination:
      host: app
      subset: v1
```

Beta users see v2; others v1.

## Path-Based

```yaml
http:
- match:
  - uri:
      prefix: /api
  route:
  - destination:
      host: api-service
- match:
  - uri:
      prefix: /static
  route:
  - destination:
      host: static-service
```

## Method-Based

```yaml
http:
- match:
  - method:
      exact: POST
  route:
  - destination:
      host: write-service
- route:
  - destination:
      host: read-service
```

## Retries

```yaml
http:
- route:
  - destination:
      host: app
  retries:
    attempts: 3
    perTryTimeout: 2s
    retryOn: 5xx,reset,connect-failure
```

## Timeouts

```yaml
http:
- route:
  - destination:
      host: app
  timeout: 5s
```

## Circuit Breaker

```yaml
spec:
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 100
        http2MaxRequests: 1000
        maxRequestsPerConnection: 10
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
```

After 5 5xx errors, eject pod for 30s.

## Mirror

```yaml
http:
- route:
  - destination:
      host: app-v1
  mirror:
    host: app-v2
  mirrorPercentage:
    value: 100
```

100% traffic mirrored to v2 (shadow). v1 serves users.

For: production-like testing.

## Fault Injection

```yaml
http:
- fault:
    delay:
      percentage:
        value: 10
      fixedDelay: 5s
    abort:
      percentage:
        value: 5
      httpStatus: 503
  route:
  - destination:
      host: app
```

10% delayed 5s; 5% aborted.

For: chaos testing.

## Header Manipulation

```yaml
http:
- route:
  - destination:
      host: app
    headers:
      request:
        set:
          x-custom: value
        remove:
        - x-internal
      response:
        add:
          x-served-by: istio
```

## Redirect

```yaml
http:
- redirect:
    uri: /new-path
    authority: new-host.com
```

## Rewrite

```yaml
http:
- match:
  - uri:
      prefix: /old
  rewrite:
    uri: /new
  route:
  - destination:
      host: app
```

## External Services

```yaml
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: github
spec:
  hosts:
  - api.github.com
  ports:
  - number: 443
    name: https
    protocol: HTTPS
```

Adds external service to mesh registry.

## Locality LB

```yaml
spec:
  trafficPolicy:
    loadBalancer:
      localityLbSetting:
        enabled: true
        distribute:
        - from: us-east-1/*
          to:
            us-east-1/*: 80
            us-west-2/*: 20
```

Prefer local zone; fall over to remote.

## Gateway API (Standard Direction)

The Kubernetes **Gateway API** (`Gateway` + `HTTPRoute`, group `gateway.networking.k8s.io`) is the standardized, mesh-agnostic successor to Istio's bespoke `Gateway` + `VirtualService` CRDs, and to ingress-controller-specific config generally. Istio supports it natively, and the **GAMMA** initiative extended it to east-west (mesh) traffic, so one API covers both ingress and in-mesh routing across implementations.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: reviews
spec:
  parentRefs:
  - name: reviews        # a mesh Service (east-west) or a Gateway (north-south)
    kind: Service
    group: core
  rules:
  - backendRefs:
    - name: reviews-v1
      port: 9080
      weight: 90
    - name: reviews-v2
      port: 9080
      weight: 10
```

`HTTPRoute` covers the common cases shown above — weighted splits, header/path matching, redirects, rewrites, retries, timeouts, mirroring. Advanced Istio-only features (fault injection, fine-grained outlier detection, locality LB) still need `VirtualService`/`DestinationRule`. The same shift is happening in every major mesh (Linkerd, Cilium, Kuma); see the Linkerd Gateway API note in C03. Prefer Gateway API for portable, new routing; reach for Istio CRDs only for features it doesn't yet express.

## Best Practices

- Subsets for versions (v1, v2)
- Always set timeout
- Reasonable retries (avoid retry storms)
- Circuit breaker on
- Mirror for testing
- Canary then promote
- Health checks tied to outlier detection

## Common Mistakes

- No timeout (hangs)
- High retries (amplify failure)
- No outlier detection (bad pods serve)
- VirtualService without DestinationRule (no subsets defined)
- Conflicting routes

## Quick Refs

```yaml
# Route 90/10
- route:
  - { destination: { host: X, subset: v1 }, weight: 90 }
  - { destination: { host: X, subset: v2 }, weight: 10 }

# Header match
- match: [ { headers: { user: { exact: alice } } } ]

# Retry
retries: { attempts: 3, perTryTimeout: 2s }

# Timeout
timeout: 5s

# Mirror
mirror: { host: X-shadow }
mirrorPercentage: { value: 100 }
```

## Interview Prep

**Mid**: "Canary with Istio."

**Senior**: "Traffic shifting strategy."

**Staff**: "Mesh routing at scale."

## Next Topic

→ [T03 — Security (mTLS, AuthorizationPolicy)](T03-Security.md)
