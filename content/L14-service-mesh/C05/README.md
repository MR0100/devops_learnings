# L14/C05 — Envoy Standalone

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Filters-Clusters-Listeners.md) | Filters, Clusters, Listeners | 1 hr |
| [T02](T02-xDS-APIs.md) | xDS APIs | 0.5 hr |

## What Envoy Is

A C++ L4/L7 proxy, originally by Lyft (2016), now CNCF graduated.

- Built for service-to-service traffic
- Dynamic config via xDS APIs
- The data plane behind Istio, Consul Connect, App Mesh
- Used standalone by many CDNs and gateways

## Configuration Model

```
LISTENER (where to accept connections)
   │
   ▼
NETWORK FILTERS (TCP-level: proxy, etc.)
   │
   ▼
HTTP CONNECTION MANAGER (parses HTTP)
   │
   ▼
HTTP FILTERS (auth, rate limit, etc.)
   │
   ▼
ROUTER (decides destination)
   │
   ▼
CLUSTER (upstream group of endpoints)
   │
   ▼
LOAD BALANCING + HEALTH CHECKING
   │
   ▼
ENDPOINT (real backend)
```

## Listeners

Sockets Envoy listens on:
```yaml
listeners:
- name: listener_0
  address:
    socket_address: { address: 0.0.0.0, port_value: 8080 }
  filter_chains:
  - filters:
    - name: envoy.filters.network.http_connection_manager
      typed_config:
        codec_type: AUTO
        stat_prefix: ingress_http
        route_config:
          virtual_hosts:
          - name: backend
            domains: ["*"]
            routes:
            - match: { prefix: "/" }
              route: { cluster: my_backend }
        http_filters:
        - name: envoy.filters.http.router
```

## Clusters

Upstream service groups:
```yaml
clusters:
- name: my_backend
  type: STRICT_DNS
  connect_timeout: 5s
  load_assignment:
    cluster_name: my_backend
    endpoints:
    - lb_endpoints:
      - endpoint:
          address:
            socket_address: { address: backend-1, port_value: 8080 }
      - endpoint:
          address:
            socket_address: { address: backend-2, port_value: 8080 }
  health_checks:
  - timeout: 1s
    interval: 5s
    http_health_check: { path: "/health" }
  lb_policy: ROUND_ROBIN
  outlier_detection: { consecutive_5xx: 5, interval: 30s, base_ejection_time: 30s }
  circuit_breakers:
    thresholds:
    - max_connections: 100
      max_pending_requests: 100
      max_requests: 1000
```

## Filters

### Network Filters (L4)
- `tcp_proxy`
- `redis_proxy`
- `mongo_proxy`
- `mysql_proxy`

### HTTP Filters (L7)
- `router` (always last)
- `cors`
- `jwt_authn`
- `oauth2`
- `rate_limit`
- `compressor`
- `ext_authz` (external authz service)
- `lua` / `wasm` (custom logic)

## xDS

Dynamic config delivery from a control plane:

```
- LDS: Listener Discovery Service
- RDS: Route Discovery Service
- CDS: Cluster Discovery Service
- EDS: Endpoint Discovery Service
- SDS: Secret Discovery Service (TLS certs)
- ADS: Aggregated Discovery Service (all of the above on one stream)
```

Envoy connects to control plane via gRPC; control plane streams config updates.

Istio, App Mesh, Consul are essentially "xDS server implementations".

## Standalone Envoy Use Cases

### Edge Proxy
Like nginx but more programmable. Used by Lyft, Snap, others as edge.

### API Gateway
Build your own using Envoy + custom control plane (or use Emissary, Contour, Gloo).

### L4/L7 LB
Better than HAProxy for dynamic, observable LB.

### Front Proxy at Microservice
Sometimes used standalone per-service (not in a mesh) for L7 features.

## Envoy vs Nginx vs HAProxy

| | Envoy | Nginx | HAProxy |
|---|---|---|---|
| Config | Dynamic (xDS) | Static + reloads | Static + reloads + Data Plane API |
| Observability | Excellent (metrics, tracing) | Basic | Good |
| L7 features | Rich | Rich | Good |
| HTTP/2/3 | Yes | Yes | Yes |
| Use | Mesh data plane, modern proxies | Web serving + caching + LB | High-perf LB |

## Interview Themes

- "Walk me through Envoy config"
- "xDS — what is it?"
- "Envoy vs Nginx"
- "How does Envoy do outlier detection?"
- "What's an HTTP filter?"
