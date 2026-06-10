# L20/C08/T02 — SPIFFE/SPIRE

## Learning Objectives

- Use SPIFFE identities
- Run SPIRE

## SPIFFE

Secure Production Identity Framework For Everyone:
- Workload identity standard
- Cloud-native
- CNCF

## SPIFFE ID

```
spiffe://example.com/ns/prod/sa/api
```

URI format:
- Trust domain (example.com)
- Path (any structure)

## SVID

SPIFFE Verifiable Identity Document:
- X.509 cert (most common)
- JWT
- Encodes SPIFFE ID

For: authenticate workload.

## SPIRE

SPIFFE runtime:
- Server (CA)
- Agent (per-node)
- Issues SVIDs

## Workflow

```
1. Workload starts
2. Agent verifies workload (selectors)
3. Server signs cert
4. Workload uses SVID for mTLS
```

## Install

```bash
helm install spire spiffe/spire-stack
```

K8s integration.

## Selectors

How agent verifies workload:
- K8s SA
- Pod labels
- Process attributes (UID, binary path)

```yaml
# Registration
spec:
  selectors:
    - "k8s:ns:prod"
    - "k8s:sa:api"
```

For: only matching workloads get cert.

## Federation

Cross-domain:
- prod.example.com trusts dev.example.com
- mTLS across domains

For: multi-cluster.

## mTLS Use

```python
import grpc
from pyspiffe.workloadapi import default_workload_api_client

client = default_workload_api_client()
svid = client.fetch_x509_svid()

# Use SVID in mTLS
```

Workload fetches; uses.

## Integration

- Istio (built-in support)
- Consul Connect
- Custom (gRPC, HTTP)

## Auto-Rotation

Short-lived SVIDs (1 hr):
- Auto-renew
- Push to workload

For: compromise mitigation.

## OIDC

SVID-JWT for OIDC flows.

For: API auth.

## Compared

| | SPIFFE | TLS cert | App-managed |
|---|---|---|---|
| Identity | URI | DN | varies |
| Rotation | auto | manual | manual |
| Workload-aware | yes | no | varies |
| Standard | open | open | proprietary |

## Why

Mature alternative:
- Same identity across platforms
- Auto-rotation
- Standard

vs:
- App-specific secrets
- Manual cert mgmt
- Inconsistent

## Use Cases

### Service Mesh
Istio uses SPIFFE.

### K8s
SPIRE-Workload Identity.

### VMs
SPIRE agent on each.

### Hybrid
Consistent across K8s + VMs.

## Architecture

```
SPIRE Server (CA)
   ↕ provisions
SPIRE Agent (per node)
   ↕ Workload API (Unix socket)
Workload
```

Local socket; no network for SVID fetch.

## Trust Bundle

Public certs of trust domain.

```bash
curl http://spire-server/bundle
```

Workloads use to verify peers.

## Best Practices

- Short SVID lifetime (1 hr)
- Selectors restrictive
- Audit registration
- Federation careful
- Backup SPIRE keys

## Common Mistakes

- Long SVID (compromise window)
- Loose selectors (anything gets cert)
- No federation strategy
- Single SPIRE (no HA)

## Adoption

- Growing in K8s
- Service mesh standard
- Multi-cloud

For: future-proof workload identity.

## Quick Refs

```
SPIFFE ID: spiffe://trust-domain/path
SVID:      X.509 or JWT
SPIRE:     Server + Agent
Selectors: k8s:ns, k8s:sa, unix:uid

Tools:
- spiffe/spire
- pyspiffe / go-spiffe
- Istio
```

## Interview Prep

**Mid**: "What's SPIFFE."

**Senior**: "Workload identity."

**Staff**: "Zero Trust workload."

## Next Topic

→ [T03 — mTLS Everywhere](T03-mTLS-Everywhere.md)
