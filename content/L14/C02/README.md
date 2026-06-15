# L14/C02 — Istio

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Istio-Architecture.md) | Architecture (istiod, Envoy) | 1 hr |
| [T02](T02-Traffic-Mgmt.md) | Traffic Management (VirtualService, DestinationRule, Gateway) | 1.5 hr |
| [T03](T03-Security.md) | Security (mTLS, AuthorizationPolicy) | 1 hr |
| [T04](T04-Observability.md) | Observability | 0.5 hr |
| [T05](T05-Ambient-Mode.md) | Ambient Mode | 1 hr |

## Architecture

```
[istiod] (control plane, single binary)
   - Pilot: traffic management
   - Citadel: certificates
   - Galley: config validation
            │ xDS
            ▼
[Envoy sidecars] (data plane)
   in each pod
```

Pre-1.5: separate microservices (Pilot, Mixer, etc.). 1.5+: monolithic istiod, removed Mixer (perf gain).

## Install (Demo)
```bash
istioctl install --set profile=demo
kubectl label namespace default istio-injection=enabled
```

After labeling, new pods get an Envoy sidecar automatically.

## Traffic Management

### Gateway
Where external traffic enters the mesh.

```yaml
apiVersion: networking.istio.io/v1
kind: Gateway
metadata:
  name: my-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port: { number: 80, name: http, protocol: HTTP }
    hosts: ["myapp.example.com"]
```

### VirtualService
Defines routing rules. Like an L7 rule set.

```yaml
apiVersion: networking.istio.io/v1
kind: VirtualService
metadata:
  name: my-app
spec:
  hosts: ["myapp.example.com"]
  gateways: ["my-gateway"]
  http:
  - match:
    - headers:
        user-type: { exact: beta }
    route:
    - destination: { host: my-app, subset: v2 }
  - route:
    - destination: { host: my-app, subset: v1 }
      weight: 90
    - destination: { host: my-app, subset: v2 }
      weight: 10
```

### DestinationRule
Defines subsets (versions) and per-destination policy (TLS, LB, circuit breaker).

```yaml
apiVersion: networking.istio.io/v1
kind: DestinationRule
metadata:
  name: my-app
spec:
  host: my-app
  trafficPolicy:
    loadBalancer:
      simple: LEAST_REQUEST
    connectionPool:
      tcp: { maxConnections: 100 }
      http: { http2MaxRequests: 1000, maxRequestsPerConnection: 10 }
    outlierDetection:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s
  subsets:
  - name: v1
    labels: { version: v1 }
  - name: v2
    labels: { version: v2 }
```

### ServiceEntry
Add external services to the mesh:
```yaml
apiVersion: networking.istio.io/v1
kind: ServiceEntry
metadata:
  name: external-api
spec:
  hosts: ["api.external.com"]
  ports:
  - number: 443
    name: https
    protocol: HTTPS
  resolution: DNS
  location: MESH_EXTERNAL
```

## Security

### mTLS (automatic)
By default, mesh traffic gets mTLS. Set policy globally or per-namespace:

```yaml
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT       # also: PERMISSIVE, DISABLE
```

### Identity (SPIFFE)
Each workload gets a SPIFFE ID:
```
spiffe://cluster.local/ns/<namespace>/sa/<serviceaccount>
```

Certificates auto-rotate (default 24h cert lifetime).

### AuthorizationPolicy
L7 authz between services.

```yaml
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata:
  name: allow-payments-from-checkout
  namespace: payments
spec:
  selector:
    matchLabels: { app: payments }
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/checkout/sa/checkout-sa"]
    to:
    - operation:
        methods: ["POST"]
        paths: ["/api/v1/charge"]
```

## Observability

Istio emits to:
- Prometheus (metrics: request count, latency, error rate)
- Jaeger/Zipkin (traces)
- Grafana (Istio dashboards)
- Kiali (service mesh UI: traffic flow, errors)

Out-of-the-box "golden signals" without app changes:
- Request rate
- Error rate (per HTTP status)
- Latency (p50, p90, p99)

## Ambient Mode

Two layers:
- **ztunnel** (DaemonSet) — L4 mTLS for all node traffic
- **waypoint** (Deployment per service) — L7 policies (optional)

Migrate incrementally per namespace:
```bash
kubectl label namespace myns istio.io/dataplane-mode=ambient
```

No sidecars; lower overhead. L7 features require waypoint proxy.

## Common Issues

- **Sidecar injection misses pod** — check `istio-injection` label and `sidecar.istio.io/inject` annotation
- **mTLS broken on legacy traffic** — use `PERMISSIVE` during migration
- **Headless services** — need careful config
- **Liveness probe failures** — Envoy intercepts; configure `holdApplicationUntilProxyStarts`
- **High control plane load** — large ConfigMaps; use Sidecar resource to scope

## Performance

- Per-request latency: ~1-5 ms
- Per-sidecar memory: 50-200 MB
- Per-sidecar CPU: ~50 mCPU idle, more under load

## Interview Themes

- "Istio architecture — describe"
- "How does mTLS work in Istio?"
- "VirtualService vs DestinationRule"
- "Canary deploy with Istio — show me"
- "Sidecar vs Ambient — tradeoffs"
- "Diagnose: traffic not flowing after enabling mTLS"
