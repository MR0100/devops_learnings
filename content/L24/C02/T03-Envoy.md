# L24/C02/T03 — Envoy

## Learning Objectives

- Explain Envoy's data-plane role and core config model (listeners, filter chains, clusters)
- Configure a standalone L7 proxy with static config and understand when to move to dynamic (xDS)
- Use Envoy's resilience features: health checking, outlier detection, circuit breaking, retries
- Know when to choose Envoy over Nginx/HAProxy and how it fits edge vs mesh roles

L14/C05 covers Envoy as a service-mesh sidecar and xDS in depth. This topic treats Envoy as a **standalone edge/load-balancing proxy** — the production-networking angle.

## Envoy as Proxy

Modern L4/L7 proxy, originally from Lyft, now a CNCF graduated project:
- Written in C++; predictable low latency, no GC pauses
- API-driven dynamic config (**xDS**) — update routes/endpoints with no reload or restart
- First-class observability (per-cluster stats, distributed tracing, access logs)
- The data plane behind Istio, Contour, Gloo, AWS App Mesh, and many API gateways

### Config Model

Four nouns do most of the work:

- **Listener** — a port Envoy binds to (e.g. `:10000`).
- **Filter chain** — the ordered filters a connection passes through; for HTTP the key one is `http_connection_manager` (HCM).
- **Route config** — inside HCM: match on host/path → pick a cluster.
- **Cluster** — a named group of upstream endpoints + the LB policy, health checks, and circuit breakers for them.

Request flow: `listener → filter chain (HCM) → route match → cluster → endpoint`.

## Standalone

```yaml
admin:
  address:
    socket_address: { address: 0.0.0.0, port_value: 9901 }

static_resources:
  listeners:
  - address:
      socket_address: { address: 0.0.0.0, port_value: 10000 }
    filter_chains:
    - filters:
      - name: envoy.filters.network.http_connection_manager
        ...
  clusters:
  - name: backend
    type: STRICT_DNS
    load_assignment:
      cluster_name: backend
      endpoints:
      - lb_endpoints:
        - endpoint:
            address:
              socket_address: { address: backend, port_value: 8080 }
```

## Run

```bash
envoy -c envoy.yaml
```

## Features

- L7 routing (host/path/header) and L4 TCP proxying
- mTLS termination/origination
- Distributed tracing + access logs
- Rich Prometheus metrics per listener/cluster
- Rate limiting (local + global via an external rate-limit service)
- Circuit breaking, retries, timeouts, outlier detection

### Resilience Building Blocks

These are why teams reach for Envoy over a basic LB:

- **Active health checks** — Envoy probes endpoints (`/healthz`) and ejects unhealthy ones.
- **Outlier detection (passive)** — eject an endpoint after N consecutive 5xx/connection failures, then gradually let it back (`base_ejection_time`). Catches degraded backends that still pass active checks.
- **Circuit breakers** — per-cluster caps on connections, pending requests, and concurrent retries; when exceeded Envoy fails fast instead of piling load on a struggling upstream.
- **Retries** — bounded (`num_retries`, `retry_on: 5xx,reset,connect-failure`) with a budget so retries can't amplify an outage.

```yaml
clusters:
- name: backend
  connect_timeout: 1s
  health_checks:
  - timeout: 1s
    interval: 5s
    http_health_check: { path: /healthz }
  outlier_detection:
    consecutive_5xx: 5
    base_ejection_time: 30s
  circuit_breakers:
    thresholds:
    - max_connections: 1024
      max_pending_requests: 1024
      max_retries: 3
```

## xDS

The static YAML above is fine for a fixed topology. At scale Envoy fetches config dynamically over gRPC/REST from a **control plane** (the xDS APIs): LDS (listeners), RDS (routes), CDS (clusters), EDS (endpoints). This is how endpoints update on autoscaling/deploys with **no reload** — the key advantage over Nginx/HAProxy.

(xDS protocol + control planes covered in depth in L14/C05/T02.)

## vs HAProxy / Nginx

| | Envoy | HAProxy | Nginx |
|---|---|---|---|
| Dynamic | yes (xDS) | reload only | reload only |
| Observability | strong | medium | basic |
| L7 | rich | rich | basic |
| Modern | yes | yes | yes |
| Use | mesh / edge | LB | LB + web |

## Use Cases

- API gateway
- Service mesh sidecar
- Edge proxy

## Common Mistakes

- Treating Envoy as a drop-in Nginx and hand-editing huge static YAML — the payoff is xDS; without a control plane you lose its main edge.
- Unbounded retries with no retry budget — turns one slow backend into a retry storm that amplifies the outage.
- No circuit breakers — under load Envoy queues unlimited pending requests against a dying upstream instead of shedding.
- Relying only on active health checks — a backend returning fast 5xx passes the check; you also need **outlier detection**.
- Forgetting the admin port (`:9901`) is unauthenticated — never expose it publicly; bind to localhost or firewall it.
- Misreading stats: alert on `upstream_rq_5xx`, ejection counts, and circuit-breaker `overflow`, not just listener throughput.

## Best Practices

- Use a control plane (Istio/Contour/Gloo or your own xDS) for anything dynamic; reserve static config for simple, fixed edge proxies.
- Set timeouts at every layer (connect, route, idle) — Envoy defaults are generous; pin them to your SLOs.
- Bound retries (`num_retries` + retry budget) and combine with circuit breakers so failure stays contained.
- Enable outlier detection alongside active health checks to eject "up but degraded" endpoints.
- Scrape the Prometheus endpoint and alert on ejections, 5xx rate, and circuit-breaker overflow per cluster.
- Restrict the admin interface to localhost; expose only the read-only stats you need.

## Quick Refs

```
admin: 9901
listeners + filter chains + clusters
xDS for dynamic

Commands via /clusters /listeners /stats
```

## Interview Prep

**Mid**: "What is Envoy and how is its config structured?" — A high-performance C++ L4/L7 proxy. Config is listeners (ports) → filter chains (HTTP via the connection manager) → route configs (match host/path) → clusters (upstream endpoints + LB/health/circuit-breaking). A request flows listener → HCM → route → cluster → endpoint.

**Senior**: "Why pick Envoy over Nginx or HAProxy?" — Dynamic config via xDS (update endpoints/routes with no reload), far richer observability (per-cluster stats, tracing, access logs), and built-in resilience (outlier detection, circuit breakers, retry budgets). Nginx/HAProxy need a reload to change config and give coarser telemetry; pick them for simple static LB/web serving.

**Staff**: "How does Envoy keep a degraded backend from taking down the service?" — Layered defense: active health checks eject down endpoints, outlier detection ejects "up but erroring" ones, circuit breakers cap connections/pending/retries so Envoy fails fast instead of queueing, and a retry budget stops retries from amplifying the failure. Driven dynamically by a control plane (EDS) so the endpoint set tracks reality during incidents.

## Next Topic

→ [T04 — Traefik](T04-Traefik.md)
