# L14/C01/T02 — Data Plane vs Control Plane

## Learning Objectives

- Understand mesh architecture
- Debug split between planes

## Architecture

```
Control Plane (config, certs)
   ↓ pushes config
Data Plane (proxies handling traffic)
   ↓ proxies app traffic
```

## Control Plane

Brain:
- Config (CRDs)
- Cert authority (issue, rotate)
- Service discovery
- Configures sidecars

Examples: istiod (Istio), linkerd-controller, Consul server.

## Data Plane

Workhorse:
- Per-pod or per-node proxy
- Handles actual traffic
- Enforces policy
- Emits telemetry

Examples: Envoy (Istio), linkerd2-proxy (Linkerd), Consul Connect proxy.

## Sidecar Model (Standard)

```
Pod
├─ App container (port 8080)
└─ Sidecar proxy (Envoy / linkerd2-proxy)
   └─ Intercepts in/out traffic
```

For: full visibility, easy injection.

## Init Container

Injected to set iptables redirect:
```
iptables: redirect all traffic 8080 → sidecar 15001
       → sidecar 15006 → app 8080
```

Transparent to app.

## CRDs (Istio)

- `VirtualService`: routing rules
- `DestinationRule`: load balancing, mTLS
- `Gateway`: ingress
- `ServiceEntry`: external services
- `Sidecar`: per-pod sidecar config
- `PeerAuthentication`: mTLS policy
- `AuthorizationPolicy`: authz

## Communication

```
istiod
  ↓ xDS (gRPC)
Envoy sidecar
```

xDS APIs: dynamic config push.
- LDS (listeners)
- RDS (routes)
- CDS (clusters)
- EDS (endpoints)

Sidecar polls; control plane streams updates.

## Push Model

Config change → istiod reconciles → push to sidecars.

No restart needed; hot reload.

## Cert Authority

istiod (built-in CA):
- Issues SPIFFE-formatted certs to sidecars
- Auto-rotates (24h typical)
- mTLS between sidecars

Or external CA (Vault).

## Service Discovery

istiod watches K8s API:
- Services
- Endpoints
- Pods

Pushes to sidecars.

For: sidecar knows where to route.

## Failure Modes

### Control Plane Down
- Sidecars keep last config
- No new config pushes
- Traffic continues
- Cert rotation fails eventually

For: control plane HA important.

### Sidecar Down
- That pod loses mesh features
- Traffic might fail (if mTLS strict)
- Restart sidecar

## istiod HA

```yaml
spec:
  replicas: 3
  topologySpreadConstraints: ...
```

For: redundancy.

## Sidecar Resources

Typical:
- 50-200 MB RAM
- 0.1-0.5 vCPU
- Tunable

For 100 pods: 5-20 GB RAM.

For latency: ~1-5 ms per hop.

## Sidecar Injection

Auto:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: prod
  labels:
    istio-injection: enabled
```

Pods in prod get sidecar.

Manual: `istioctl kube-inject`.

## Ambient Mode (Sidecarless)

Istio newer:
```
ztunnel (per node) → handles L4 mTLS
Waypoint proxy (per identity, optional) → L7 features
```

No per-pod sidecar:
- Lower overhead
- Per-node proxy
- L7 only when needed

For: future direction.

## Linkerd Architecture

```
Control plane: linkerd-destination, linkerd-identity, linkerd-proxy-injector
Data plane: linkerd2-proxy (Rust; small)
```

Simpler than Istio; less features but easier.

## Consul Connect

```
Consul servers (control plane)
   ↓ ACLs, intentions
Sidecar proxies (Envoy or built-in)
```

Works with VMs + K8s.

## Comparison

| | Istio | Linkerd | Consul |
|---|---|---|---|
| Data plane | Envoy | linkerd2-proxy | Envoy |
| Control plane | istiod | linkerd-* | Consul |
| Language (DP) | C++ | Rust | Consul |
| Footprint | Heavier | Lighter | Medium |
| Features | Most | Core | Strong |
| Learning | Steep | Easier | Medium |

## Multi-Cluster

Mesh across clusters:
- Single control plane (manage all)
- Multi control plane (each cluster own)
- Sidecars across clusters: cross-cluster service discovery

For: cross-region.

## Debugging

Control plane:
```bash
kubectl logs -n istio-system -l app=istiod
istioctl analyze
```

Data plane:
```bash
istioctl proxy-config cluster POD
istioctl proxy-config route POD
istioctl proxy-status   # sync status
```

For: see what config sidecars received.

## Operator vs Helm

Istio: Operator + Helm.

```bash
istioctl install --set profile=demo
# or
helm install istio-base ...
helm install istiod ...
```

For: managed install.

## Best Practices

- Control plane HA
- Sidecar resource limits set
- Monitor istiod (it can OOM)
- Use admin port for debug
- Document CRDs
- Test failure modes
- Auto-injection per namespace

## Common Mistakes

- One istiod replica (SPOF)
- No resource limits on sidecars
- Wide mesh policy (everything)
- Inject all namespaces (kube-system included by mistake)
- Skip TLS for control plane comms

## Quick Refs

```bash
# Istio
istioctl proxy-status
istioctl proxy-config cluster|listener|route|endpoint POD
istioctl analyze
istioctl version

# Linkerd
linkerd check
linkerd viz dashboard
linkerd tap deploy/X

# Consul Connect
consul connect proxy-config
```

## Interview Prep

**Mid**: "Data vs control plane."

**Senior**: "How sidecar gets config."

**Staff**: "Mesh failure modes."

## Next Topic

→ [T03 — Sidecar vs Sidecarless (Ambient Mesh)](T03-Sidecar-Ambient.md)
