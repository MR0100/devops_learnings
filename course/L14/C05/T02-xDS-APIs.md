# L14/C05/T02 — xDS APIs

## Learning Objectives

- Understand xDS
- Build custom control plane

## xDS

Dynamic discovery service. APIs for Envoy:
- LDS (Listener Discovery Service)
- RDS (Route Discovery Service)
- CDS (Cluster Discovery Service)
- EDS (Endpoint Discovery Service)
- SDS (Secret Discovery Service)
- ADS (Aggregated Discovery Service)

## How It Works

```
Envoy → connects to xDS server (gRPC)
   → subscribes to resources
   → receives updates
   → applies hot
```

## SOTW vs Delta

### SOTW (State of the World)
Server sends complete current state.

### Delta
Server sends only changes.

Newer; more efficient.

## ADS

All xDS over single stream:
```yaml
dynamic_resources:
  ads_config:
    api_type: GRPC
    transport_api_version: V3
    grpc_services:
    - envoy_grpc:
        cluster_name: xds_cluster
  cds_config:
    ads: {}
    resource_api_version: V3
  lds_config:
    ads: {}
    resource_api_version: V3
```

For: simplicity, ordering.

## EDS Example

```yaml
clusters:
- name: backend
  type: EDS
  eds_cluster_config:
    eds_config:
      ads: {}
      resource_api_version: V3
```

Endpoints come from xDS server, not static.

## Use Case

### Service Mesh
istiod = xDS server for sidecars.

### Custom Control Plane
Build own; serve to Envoy fleet.

### Hot Reload
Update config without restart.

## Implement xDS Server

Go example (go-control-plane):
```go
import (
  "github.com/envoyproxy/go-control-plane/pkg/cache/v3"
  "github.com/envoyproxy/go-control-plane/pkg/server/v3"
)

snapshotCache := cache.NewSnapshotCache(false, cache.IDHash{}, nil)

snapshot := cache.NewSnapshot(
  "v1",
  []types.Resource{endpoint1, endpoint2},
  []types.Resource{cluster1},
  []types.Resource{route1},
  []types.Resource{listener1},
  nil,
  nil,
)

snapshotCache.SetSnapshot("node-id", snapshot)
```

Envoy connects with `node.id`; gets resources for that node.

## Resource Versioning

xDS uses versions:
- Server sends version with resources
- Client ACKs / NACKs

Optimistic concurrency.

## Eventual Consistency

xDS: eventually consistent.

For routing: brief inconsistency during update OK.

## Performance

Large fleets (10000+ sidecars):
- Server CPU
- Memory (per-sidecar cache)
- Network (push frequency)

Tune:
- Batching
- Per-node filtering (don't send all to all)
- Delta protocol

## Envoy Stats

```bash
# Subscribed resources
curl localhost:9901/clusters

# xDS status
curl localhost:9901/server_info
```

## Control Plane Examples

### Istio
istiod implements xDS.

### Envoy Gateway
Standalone API gateway with xDS.

### Contour
K8s ingress controller; xDS to Envoy.

### Custom
Build with go-control-plane.

## When Custom Control Plane

- App-specific routing
- Beyond standard mesh
- Integration with existing systems
- Research / specialized

For most: use Istio.

## Node Identity

Each Envoy has:
```yaml
node:
  id: my-envoy-001
  cluster: my-cluster
```

Server uses `id` + `cluster` to determine resources.

## xDS Versions

- V2: legacy (deprecated)
- V3: current

## gRPC vs REST

gRPC (default):
- Streaming
- Efficient
- Bi-directional

REST:
- Simpler clients
- Less efficient

## Implementation Layers

```
xDS protocol (gRPC)
   ↑
Discovery server (Pilot, custom, etc.)
   ↑
Data source (K8s API, DB, config)
```

## Resource Caching

Server caches per-node snapshot.

Update flow:
1. Source change (e.g. new K8s Service)
2. Server computes new snapshot
3. Server pushes to subscribed Envoys

## Hot Reload

Envoy doesn't restart for:
- New cluster
- Endpoint changes
- Route changes
- Listener changes

For: zero-downtime updates.

Some config requires drain:
- Filter chain swap
- Major listener changes

## xDS for Mesh

Istio: control plane = xDS server.

Linkerd: not xDS-based (custom protocol).

## SDS

Secrets (certs):
```yaml
transport_socket:
  name: envoy.transport_sockets.tls
  typed_config:
    "@type": ...DownstreamTlsContext
    common_tls_context:
      tls_certificate_sds_secret_configs:
      - name: server-cert
        sds_config:
          ads: {}
```

Server pushes cert; Envoy uses.

For: cert rotation without restart.

## Best Practices

- Use ADS (simpler)
- Delta protocol for scale
- Version resources
- Per-node filtering
- Monitor server CPU
- Hot reload (no drain unnecessarily)

## Common Mistakes

- SOTW at scale (CPU spike)
- No version (cache invalidation)
- All resources to all nodes (waste)
- Slow xDS server (Envoy stale)

## Quick Refs

```yaml
# Envoy config
dynamic_resources:
  ads_config: { api_type: GRPC, grpc_services: ... }

# Check
curl localhost:9901/clusters | grep my-cluster
curl localhost:9901/config_dump
```

## Tools

- go-control-plane (Go library)
- envoy-control-plane (C++ library)
- Envoy Gateway (K8s)
- Contour (ingress)

## Real-World

- Istio: xDS for K8s mesh
- Lyft: original xDS use
- LinkedIn: custom xDS for east-west
- AWS App Mesh: similar pattern

## Interview Prep

**Senior**: "xDS protocol."

**Staff**: "Custom control plane."

**Principal**: "Envoy fleet at scale."

## Next Topic

→ Move to [L14/C06 — Choosing a Mesh](../C06/README.md)
