# L14/C02/T05 — Ambient Mode

## Learning Objectives

- Install ambient
- Use waypoints

## Install

```bash
istioctl install --set profile=ambient
```

Or Helm:
```bash
helm install istio-base istio/base
helm install istio-cni istio/cni --set profile=ambient
helm install istiod istio/istiod --set profile=ambient
helm install ztunnel istio/ztunnel
```

## Components

### ztunnel
- DaemonSet
- Per-node mTLS L4 proxy
- ~50-100 MB RAM

### Waypoint (optional)
- L7 features
- Per service or SA
- Deployed as standard Pod

## Enable Per-Namespace

```bash
kubectl label namespace prod istio.io/dataplane-mode=ambient
```

All pods: L4 mTLS via ztunnel.

No sidecar injection.

## Verify

```bash
istioctl ztunnel-config workloads
```

## Apply Waypoint

```bash
istioctl x waypoint apply --enroll-namespace prod
```

Or per-SA:
```bash
istioctl x waypoint apply --service-account my-app -n prod
```

## L4 (Always)

mTLS between pods on different nodes:
```
Pod A → ztunnel A → mTLS → ztunnel B → Pod B
```

L4 features:
- mTLS
- L4 authorization
- Identity

## L7 (Waypoint)

If waypoint deployed:
```
Pod A → ztunnel A → waypoint (for Pod B's identity) → ztunnel B → Pod B
```

L7 features:
- HTTP routing
- Retries
- Timeouts
- L7 authorization (path, method)

## Per-Namespace Waypoint

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: waypoint
  namespace: prod
  labels:
    istio.io/waypoint-for: service
spec:
  gatewayClassName: istio-waypoint
  listeners:
  - name: mesh
    port: 15008
    protocol: HBONE
```

## VirtualService / Routing

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: my-app
spec:
  hosts:
  - my-app
  http:
  - route:
    - destination:
        host: my-app
        subset: v1
      weight: 90
    - destination:
        host: my-app
        subset: v2
      weight: 10
```

Same as sidecar; waypoint applies.

## Authorization (L4)

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: l4-policy
spec:
  selector:
    matchLabels:
      app: my-app
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/prod/sa/frontend"]
    to:
    - operation:
        ports: ["8080"]
```

L4: principal, port. No HTTP-level.

## Authorization (L7)

```yaml
spec:
  rules:
  - to:
    - operation:
        methods: ["GET"]
        paths: ["/api/*"]
```

Requires waypoint.

## Sidecar + Ambient Mix

```
Namespace A: sidecar mode
Namespace B: ambient mode
```

Traffic between works (mTLS via either).

For: gradual migration.

## Migration

Existing sidecar:
1. Install ambient (add ztunnel + CNI)
2. Test in new namespace
3. Migrate namespace by namespace
4. Disable sidecar in migrated
5. Add waypoint where L7 needed

## When Waypoint

- L7 routing
- L7 authorization
- Retries / timeouts (L7 features)

Otherwise: skip; lower cost.

## Resource Comparison

For 100 pods, 5 nodes:

| | Sidecar | Ambient L4 | Ambient + Waypoint |
|---|---|---|---|
| RAM | 10 GB (sidecars) | 500 MB (ztunnel) | 500 MB + waypoint pods |
| CPU | high | low | medium |
| Restart for upgrade | Yes (all pods) | No | Waypoint pods |

## L7 Mediation

For services without L7 needs: L4 ambient only. Minimal overhead.

For services with: waypoint added.

For: per-service optimization.

## CNI Plugin

Ambient installs CNI plugin:
- Redirects traffic to ztunnel
- Per-node configuration

For: K8s CNI must be compatible.

## Multi-Cluster Ambient

Cross-cluster mTLS via ztunnel HBONE.

For: future feature; check current support.

## Tracing in Ambient

Waypoint emits traces (L7).
ztunnel L4 metrics only (no spans).

For: full traces need waypoint.

## Debug

```bash
# ztunnel config
istioctl ztunnel-config workloads
istioctl ztunnel-config service
istioctl ztunnel-config policies

# Waypoint config (like sidecar config)
istioctl proxy-config cluster waypoint-pod
```

## Best Practices

- Use ambient for new installs (lower cost)
- Sidecar mode if proven workflow
- Waypoint per-service (not blanket)
- Monitor ztunnel resources
- Test L7 features in staging
- Upgrade ztunnel via DaemonSet rollout

## Common Mistakes

- Skip waypoint, expect L7
- Mix sidecar + ambient without understanding
- Don't monitor ztunnel
- Outdated ambient features (rapid evolution)

## Status

GA since Istio 1.22 (Nov 2024).

For prod: viable for new adoption.

## Quick Refs

```bash
# Install ambient
istioctl install --set profile=ambient

# Enable namespace
kubectl label namespace prod istio.io/dataplane-mode=ambient

# Waypoint
istioctl x waypoint apply --enroll-namespace prod
istioctl x waypoint apply --service-account SA -n prod

# Config
istioctl ztunnel-config workloads / service / policies

# Check
istioctl x version
```

## Interview Prep

**Senior**: "Ambient mode."

**Staff**: "Sidecar vs ambient choice."

**Principal**: "Mesh cost optimization."

## Next Topic

→ Move to [L14/C03 — Linkerd](../C03/README.md)
