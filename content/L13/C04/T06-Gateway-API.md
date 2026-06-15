# L13/C04/T06 — Gateway API (The Future of Ingress)

## Learning Objectives

- Understand Gateway API
- Migrate from Ingress

## Why Gateway API

Ingress limitations:
- Annotations explode (per-controller)
- Limited features (L7 routing only)
- No role separation
- Tightly coupled to controller

Gateway API:
- Standard across controllers
- Role-oriented (cluster admin vs app dev)
- Extensible
- More features (header rewrites, mirroring, etc.)

GA in 1.31+.

## Resources

```
GatewayClass (cluster admin)
    ↓
Gateway (cluster admin / infra team)
    ↓
HTTPRoute / TCPRoute / UDPRoute / TLSRoute / GRPCRoute (app team)
    ↓
backendRefs (Services)
```

## GatewayClass

Defines a class of Gateways:
```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: GatewayClass
metadata:
  name: example
spec:
  controllerName: example.com/gateway-controller
```

Created by cluster admin. Indicates which controller implements.

## Gateway

Instance of a GatewayClass:
```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: prod-gateway
  namespace: gateway-system
spec:
  gatewayClassName: example
  listeners:
  - name: http
    protocol: HTTP
    port: 80
  - name: https
    protocol: HTTPS
    port: 443
    tls:
      certificateRefs:
      - name: my-tls
    allowedRoutes:
      namespaces:
        from: All
```

Provisions LB / proxy. Owned by infra team.

## HTTPRoute

App-level routing:
```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: my-app
  namespace: my-app
spec:
  parentRefs:
  - name: prod-gateway
    namespace: gateway-system
  hostnames:
  - "app.example.com"
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /api
    backendRefs:
    - name: api-svc
      port: 80
      weight: 90
    - name: api-canary
      port: 80
      weight: 10
  - matches:
    - path:
        type: PathPrefix
        value: /
    backendRefs:
    - name: web
      port: 80
```

Owned by app team.

## Why Role Separation Matters

- Cluster admin owns Gateway (security, TLS, LB)
- App team owns HTTPRoute (routing, backends)

Without confusion / RBAC issues.

## Multi-Namespace

Gateway in one namespace; HTTPRoutes in many:
```yaml
spec:
  listeners:
  - ...
    allowedRoutes:
      namespaces:
        from: Selector
        selector:
          matchLabels:
            allowed: "true"
```

Only namespaces with label can attach.

## Filters

Modify request/response:
```yaml
rules:
- filters:
  - type: RequestHeaderModifier
    requestHeaderModifier:
      add:
      - name: x-version
        value: v2
      remove:
      - x-old-header
```

For: header manipulation.

## Traffic Splitting

```yaml
backendRefs:
- name: v1
  weight: 90
- name: v2
  weight: 10
```

For: canary deploy.

## Mirroring

```yaml
filters:
- type: RequestMirror
  requestMirror:
    backendRef:
      name: shadow-service
```

Send copy to shadow service. Original response goes back to client.

For: testing under load.

## TCP / UDP Routes

```yaml
apiVersion: gateway.networking.k8s.io/v1alpha2
kind: TCPRoute
spec:
  parentRefs: [...]
  rules:
  - backendRefs:
    - name: my-tcp
      port: 5432
```

For non-HTTP.

## GRPCRoute

```yaml
apiVersion: gateway.networking.k8s.io/v1alpha2
kind: GRPCRoute
spec:
  rules:
  - matches:
    - method:
        type: Exact
        service: my.package.Service
        method: MyMethod
    backendRefs:
    - name: grpc-svc
      port: 50051
```

For gRPC services.

## TLSRoute

```yaml
apiVersion: gateway.networking.k8s.io/v1alpha2
kind: TLSRoute
spec:
  hostnames: [secure.example.com]
  rules:
  - backendRefs:
    - name: tls-svc
```

For TLS passthrough.

## Controllers Supporting

- Istio (Gateway API native)
- Contour
- Envoy Gateway
- Cilium
- NGINX (GA)
- AWS Gateway Controller (early)
- Kong

All implement same API; differ in features.

## Why Better Than Ingress

| | Ingress | Gateway API |
|---|---|---|
| Role separation | None | Yes |
| Path types | Limited | Many |
| Header manipulation | Annotations | Native |
| TLS | Basic | Multiple per Gateway |
| Traffic split | Annotations | Native |
| Cross-namespace | Tricky | Built-in |
| Standardization | Annotations per controller | Standard |

## Migration

Ingress + annotations → Gateway API:
1. Install Gateway API CRDs
2. Install Gateway controller
3. Create GatewayClass + Gateway
4. Convert each Ingress to HTTPRoute
5. Verify
6. Decommission Ingress

For new clusters: Gateway API from start.

## Annotation → Gateway API

Common:
- `nginx.ingress/rewrite-target` → URLRewriteFilter
- `nginx.ingress/ssl-redirect` → HTTPS listener + HTTP redirect
- Traffic split → backendRefs weights
- Header → RequestHeaderModifier

## Cross-Namespace Reference

Backend in different namespace:
```yaml
backendRefs:
- name: my-svc
  namespace: other
  port: 80
```

Requires ReferenceGrant in target namespace.

## ReferenceGrant

Allow cross-namespace ref:
```yaml
apiVersion: gateway.networking.k8s.io/v1beta1
kind: ReferenceGrant
metadata:
  name: allow-from-app
  namespace: other
spec:
  from:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    namespace: app
  to:
  - group: ""
    kind: Service
```

Otherwise: cross-namespace refs blocked (security).

## Implementations

### Istio
```bash
istioctl install --set profile=demo
```

Gateway API native; works with mesh.

### Envoy Gateway
Dedicated implementation:
```bash
helm install envoy-gateway envoy-gateway/envoy-gateway
```

### Contour
```bash
helm install contour bitnami/contour
```

## When NOT Gateway API

- Existing Ingress works
- Simple needs
- Controller doesn't support yet
- Migration cost > benefit

For new: Gateway API. For existing: migrate when value clear.

## Best Practices

- Separate Gateway (infra) from Routes (apps)
- ReferenceGrants for cross-namespace
- Multiple Gateways for environments
- TLS at Gateway
- Document filters

## Common Mistakes

- One Gateway per Route (overkill)
- No allowedRoutes restrictions
- TLS at every Route (use Gateway)
- Ignoring ReferenceGrant security

## Future

Gateway API:
- Active development
- More features (rate limit, auth as filter coming)
- Service Mesh APIs (GAMMA) integration

Direction: declarative L7 standard across implementations.

## kubectl Commands

```bash
kubectl get gateway -A
kubectl get httproute -A
kubectl describe gateway prod-gateway
kubectl describe httproute my-app
```

## Quick Refs

```yaml
# Gateway
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
spec:
  gatewayClassName: nginx
  listeners:
  - name: https
    port: 443
    protocol: HTTPS
    tls:
      certificateRefs:
      - name: tls-secret

# HTTPRoute
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
spec:
  parentRefs: [{name: my-gateway}]
  hostnames: [app.example.com]
  rules:
  - matches: [{path: {type: PathPrefix, value: /}}]
    backendRefs: [{name: web, port: 80}]
```

## Interview Prep

**Mid**: "Gateway API vs Ingress."

**Senior**: "Role separation in Gateway API."

**Staff**: "Migration to Gateway API."

## Next Topic

→ [T07 — NetworkPolicies](T07-NetworkPolicies.md)
