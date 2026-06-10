# L24/C03/T03 — Gateway API (Kubernetes)

## Learning Objectives

- Use Gateway API
- Migrate from Ingress

## Gateway API

K8s SIG-Network:
- Successor to Ingress
- More flexible
- Role-oriented
- Multi-protocol

## Resources

### GatewayClass
Template for gateways:
```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: GatewayClass
metadata:
  name: example
spec:
  controllerName: example.com/gateway-controller
```

Cluster-admin defines.

### Gateway
Instance:
```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: my-gateway
spec:
  gatewayClassName: example
  listeners:
  - name: http
    port: 80
    protocol: HTTP
  - name: https
    port: 443
    protocol: HTTPS
    tls:
      certificateRefs:
      - name: my-cert
```

Operator team.

### HTTPRoute
```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: my-app
spec:
  parentRefs:
  - name: my-gateway
  hostnames:
  - app.example.com
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /api
    backendRefs:
    - name: api-service
      port: 80
  - matches:
    - path:
        value: /
    backendRefs:
    - name: web-service
      port: 80
```

App team.

### TCPRoute, UDPRoute, TLSRoute, GRPCRoute
For other protocols.

## vs Ingress

| | Ingress | Gateway API |
|---|---|---|
| Maturity | mature | growing |
| Multi-protocol | HTTP only | HTTP/TCP/UDP/TLS/gRPC |
| Roles | one resource | separated (Class/Gateway/Route) |
| Annotations | implementation-specific | first-class fields |
| Status | reliable | growing |

For new: Gateway API.
For existing: gradual.

## Implementations

- Istio
- Cilium
- Envoy Gateway
- NGINX Gateway
- Traefik
- Contour

Many ingress controllers also implement.

## Role Separation

- Infrastructure: GatewayClass
- Cluster admin: Gateway
- App developer: HTTPRoute

For: clear ownership.

## Cross-Namespace

Route in app NS; Gateway in shared NS.

```yaml
spec:
  allowedRoutes:
    namespaces:
      from: All   # or Same / Selector
```

Controlled cross-NS access.

## Traffic Splitting

```yaml
rules:
- backendRefs:
  - name: app-v1
    weight: 90
  - name: app-v2
    weight: 10
```

Native canary.

## Path / Header Match

```yaml
matches:
- path: { type: PathPrefix, value: /api }
  headers:
  - name: X-Tenant
    value: acme
```

## Redirects

```yaml
- matches:
  - path: { value: /old }
  filters:
  - type: RequestRedirect
    requestRedirect:
      path: { type: ReplaceFullPath, replaceFullPath: /new }
      statusCode: 301
```

## Header Manipulation

```yaml
filters:
- type: RequestHeaderModifier
  requestHeaderModifier:
    add:
    - name: X-Custom
      value: value
    remove:
    - X-Internal
```

## URL Rewrite

```yaml
filters:
- type: URLRewrite
  urlRewrite:
    path: { type: ReplacePrefixMatch, replacePrefixMatch: /v2 }
```

## Migration

Existing Ingress:
1. Pick Gateway API implementation
2. Translate Ingress rules to HTTPRoute
3. Test in parallel
4. Cut over

For: gradual.

## Best Practices

- New clusters: Gateway API
- Existing: migrate when implementation ready
- Role separation respected
- TLS at gateway
- Filter for headers / redirects

## Common Mistakes

- Mix Ingress + Gateway API (confusion)
- App team touches Gateway (separation broken)
- Wrong namespace permissions

## Quick Refs

```yaml
GatewayClass: controller
Gateway: listeners + TLS
HTTPRoute: paths, backends, filters
TCPRoute / GRPCRoute: other protocols

filters:
  RequestRedirect
  RequestHeaderModifier
  URLRewrite
  ExtensionRef (impl-specific)
```

## Interview Prep

**Mid**: "Gateway API."

**Senior**: "vs Ingress."

**Staff**: "K8s ingress strategy."

## Next Topic

→ Move to [L24/C04 — Service Discovery](../C04/README.md)
