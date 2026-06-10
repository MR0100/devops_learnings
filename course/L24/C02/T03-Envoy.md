# L24/C02/T03 — Envoy

## Learning Objectives

- Use Envoy
- Dynamic config

(Covered L14/C05 — referencing here.)

## Envoy as Proxy

Modern L4/L7 proxy:
- C++
- High performance
- Dynamic config (xDS)
- Service mesh fabric

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

- L7 routing
- mTLS
- Tracing
- Metrics (Prometheus)
- Rate limiting
- Circuit breaking
- Retries

## xDS

Dynamic config via gRPC.

(See L14/C05/T02.)

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

## Quick Refs

```
admin: 9901
listeners + filter chains + clusters
xDS for dynamic

Commands via /clusters /listeners /stats
```

## Interview Prep

**Mid**: "What's Envoy."

**Senior**: "Envoy vs alternatives."

**Staff**: "Envoy in architecture."

## Next Topic

→ [T04 — Traefik](T04-Traefik.md)
