# L20/C08/T03 — mTLS Everywhere

## Learning Objectives

- Implement mTLS
- At scale

## mTLS

Both client + server cert auth:
- Mutual identity
- Encryption

For: Zero Trust internal.

## Why

- Internal traffic encrypted
- Both ends authenticated
- Defense in depth

## Implementation Options

### Service Mesh
Istio / Linkerd: auto mTLS.

### SPIRE + Manual
SVIDs; app uses for mTLS.

### App Lib
TLS lib in each app.

### LB Termination
Don't (defeats purpose for internal).

## Service Mesh

Easiest path:
- Install Istio / Linkerd
- mTLS default
- Workload identity

(See L14.)

## Istio mTLS

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: prod
spec:
  mtls:
    mode: STRICT
```

All pod-to-pod: mTLS or reject.

## Linkerd

mTLS default; no config.

## SPIRE Manual

Workload:
```python
client = default_workload_api_client()
svid = client.fetch_x509_svid()
context = ssl.create_default_context()
# Use SVID
```

For: more control.

## Cert Rotation

mTLS certs:
- Short-lived (1-24 hr)
- Auto-rotated
- Workload re-fetches

## Performance

Overhead:
- ~1-3 ms per connection (handshake)
- < 5% throughput
- Negligible for most

For: most apps OK.

## Mesh Overhead

Sidecar:
- 50-200 MB RAM per pod
- Some CPU

For: cost.

## Sidecarless (Ambient / Cilium)

Lower overhead:
- ztunnel per node
- Cilium eBPF

(See L14/C01/T03.)

## Migration Strategy

```
Phase 1: PERMISSIVE (both plain + mTLS)
Phase 2: Most workloads mesh-enabled
Phase 3: STRICT per-namespace
Phase 4: STRICT cluster-wide
```

Years for large org.

## Verify

```bash
kubectl exec -n prod -it pod -c istio-proxy -- openssl s_client -connect other-service:8080
```

Check cert.

## AuthZ on Top

mTLS proves identity.
AuthZ decides access.

```yaml
kind: AuthorizationPolicy
spec:
  rules:
  - from:
    - source:
        principals: ["...sa/frontend"]
```

Per-identity allow.

## North-South mTLS

Client (browser) → API:
- TLS (one-way) usually
- Client cert for high-sec

For: not typical for web.

## East-West Critical

Internal traffic:
- mTLS strict
- Same standard

## Multi-Cluster

- Shared trust (CA)
- Federation
- Cross-cluster mTLS

For: zero trust across.

## Tools

- Istio
- Linkerd
- Consul Connect
- Cilium mesh
- SPIRE
- Application libraries

## Compliance

- PCI-DSS encryption everywhere
- HIPAA in transit
- SOC 2

mTLS evidences.

## Best Practices

- Service mesh for easy mTLS
- STRICT in prod
- Short cert lifetime
- AuthZ on top
- Multi-cluster federation
- Monitor cert health

## Common Mistakes

- PERMISSIVE forever
- No rotation
- Long-lived certs
- LB terminates and forwards plain
- Skip AuthZ

## Quick Refs

```yaml
# Istio
PeerAuthentication: STRICT

# Linkerd
default (annotated namespace)

# Cert lifetime
1-24 hours; auto rotate
```

```bash
# Check
openssl s_client -connect svc:port -showcerts
```

## Interview Prep

**Mid**: "What's mTLS."

**Senior**: "mTLS at scale."

**Staff**: "Zero Trust east-west."

## Next Topic

→ Move to [L20/C09 — Compliance](../C09/README.md)
