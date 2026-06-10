# L14/C05/T01 — Envoy: Filters, Clusters, Listeners

## Learning Objectives

- Configure Envoy directly
- Understand its model

## Envoy

L4/L7 proxy:
- C++; high performance
- Used by Istio, Consul, AWS App Mesh
- Standalone capable
- Edge or sidecar

## Concepts

### Listener
Inbound port; accepts connections.

### Filter
Process traffic (HTTP, TCP, etc.).

### Cluster
Upstream pool of endpoints.

### Endpoint
Backend instance (IP:port).

### Route
HTTP routing rules.

## Sample Config (YAML)

```yaml
static_resources:
  listeners:
  - name: listener_0
    address:
      socket_address: { address: 0.0.0.0, port_value: 10000 }
    filter_chains:
    - filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          stat_prefix: ingress_http
          route_config:
            name: local_route
            virtual_hosts:
            - name: local_service
              domains: ["*"]
              routes:
              - match: { prefix: "/" }
                route: { cluster: backend }
          http_filters:
          - name: envoy.filters.http.router
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router
  clusters:
  - name: backend
    connect_timeout: 5s
    type: STRICT_DNS
    lb_policy: ROUND_ROBIN
    load_assignment:
      cluster_name: backend
      endpoints:
      - lb_endpoints:
        - endpoint:
            address:
              socket_address: { address: backend.example.com, port_value: 80 }
```

## Run

```bash
envoy -c envoy.yaml
```

## Filter Chains

```yaml
filter_chains:
- filter_chain_match:
    server_names: ["api.example.com"]
  filters:
  - name: envoy.filters.network.http_connection_manager
    typed_config: ...

- filter_chain_match:
    server_names: ["web.example.com"]
  filters:
  - name: envoy.filters.network.http_connection_manager
    typed_config: ...
```

SNI-based routing.

## Network Filters

L4:
- `tcp_proxy`
- `http_connection_manager`
- `redis_proxy`
- `mongo_proxy`
- `mysql_proxy`

For: protocol-aware.

## HTTP Filters

Within http_connection_manager:
- `router` (last; routes)
- `cors`
- `jwt_authn`
- `ext_authz` (external auth)
- `rate_limit`
- `lua`
- `wasm`

```yaml
http_filters:
- name: envoy.filters.http.cors
- name: envoy.filters.http.jwt_authn
  typed_config: ...
- name: envoy.filters.http.router  # last
```

## Cluster Types

- `STATIC`: hardcoded endpoints
- `STRICT_DNS`: re-resolve DNS
- `LOGICAL_DNS`: cache DNS
- `EDS`: dynamic endpoints (xDS)

## Load Balancing

```yaml
lb_policy: ROUND_ROBIN | LEAST_REQUEST | RING_HASH | RANDOM | MAGLEV
```

For: distribute traffic.

## Health Check

```yaml
clusters:
- name: backend
  health_checks:
  - timeout: 1s
    interval: 10s
    unhealthy_threshold: 3
    healthy_threshold: 2
    http_health_check:
      path: /health
```

## TLS

```yaml
- name: listener_0
  filter_chains:
  - filters: ...
    transport_socket:
      name: envoy.transport_sockets.tls
      typed_config:
        "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.DownstreamTlsContext
        common_tls_context:
          tls_certificates:
          - certificate_chain:
              filename: /etc/ssl/cert.pem
            private_key:
              filename: /etc/ssl/key.pem
```

## Upstream TLS

```yaml
clusters:
- name: backend
  transport_socket:
    name: envoy.transport_sockets.tls
    typed_config:
      "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.UpstreamTlsContext
      sni: backend.example.com
```

For: mTLS.

## Routing

```yaml
virtual_hosts:
- name: app
  domains: ["app.example.com"]
  routes:
  - match: { prefix: "/api/v1" }
    route: { cluster: api_v1 }
  - match: { prefix: "/api/v2" }
    route: { cluster: api_v2 }
  - match:
      headers:
      - name: x-user
        string_match: { exact: "premium" }
    route: { cluster: premium }
  - match: { prefix: "/" }
    route: { cluster: default }
```

## Weighted Routing

```yaml
route:
  weighted_clusters:
    clusters:
    - { name: v1, weight: 90 }
    - { name: v2, weight: 10 }
```

## Retries

```yaml
route:
  cluster: backend
  retry_policy:
    retry_on: "5xx,connect-failure"
    num_retries: 3
    per_try_timeout: 2s
```

## Timeouts

```yaml
route:
  cluster: backend
  timeout: 30s
```

## Circuit Breaking

```yaml
clusters:
- name: backend
  circuit_breakers:
    thresholds:
    - max_connections: 1024
      max_pending_requests: 1024
      max_requests: 1024
      max_retries: 3
```

## Admin Interface

```yaml
admin:
  address:
    socket_address: { address: 0.0.0.0, port_value: 9901 }
```

```bash
curl localhost:9901/clusters
curl localhost:9901/listeners
curl localhost:9901/stats
curl localhost:9901/config_dump
```

For: introspection.

## Metrics

Envoy exposes Prometheus metrics:
```bash
curl localhost:9901/stats/prometheus
```

Hundreds of metrics:
- request count
- latency histograms
- cluster health
- connection counts

## Use Cases

### API Gateway
Envoy at edge; routes to services.

### Sidecar
Per-pod (Istio).

### Web Frontend
TLS termination, routing.

### TCP Proxy
For non-HTTP services.

## Comparison to nginx

| | Envoy | nginx |
|---|---|---|
| L4 | yes | yes |
| L7 | yes | yes |
| Modern protocols | HTTP/3, gRPC native | partial |
| Dynamic config | xDS | reload |
| Observability | strong | basic |
| Plugin model | filter chain | modules |
| Resource use | higher | lower |

For: dynamic, observable: Envoy.

## xDS

Dynamic config:
- LDS (listeners)
- RDS (routes)
- CDS (clusters)
- EDS (endpoints)
- SDS (secrets)

Pulled from xDS server (e.g. istiod).

## Standalone Use

Beyond mesh: as edge proxy.

E.g. as API gateway:
```yaml
listeners:
- ... (TLS, routing)
clusters:
- ... (per microservice)
```

Or as ingress controller (Contour).

## Best Practices

- Admin interface secured (private)
- Health checks
- Circuit breakers
- Timeouts everywhere
- Metrics scraped
- Config validation (envoy --mode validate)

## Common Mistakes

- No timeouts (hangs)
- Admin exposed (info leak)
- No health checks
- Over-complex filter chains
- Static config when dynamic needed

## Quick Refs

```bash
# Run
envoy -c config.yaml

# Validate
envoy --mode validate -c config.yaml

# Admin
curl localhost:9901/clusters
curl localhost:9901/listeners
curl localhost:9901/stats/prometheus
curl localhost:9901/config_dump
```

## Interview Prep

**Mid**: "Envoy concepts."

**Senior**: "Filter chains."

**Staff**: "Envoy as edge proxy."

## Next Topic

→ [T02 — xDS APIs](T02-xDS-APIs.md)
