# L14/C02/T01 — Istio Architecture (istiod, Envoy)

## Learning Objectives

- Install Istio
- Understand components

## Components

### istiod
Single binary, control plane:
- Pilot (config distribution)
- Citadel (CA)
- Galley (config validation)

Was multiple; consolidated to istiod.

### Envoy
Data plane:
- Sidecar proxy
- C++; high performance
- xDS-driven config

### Gateway
Ingress/egress.
- Envoy at edge
- Public traffic in/out

## Install

```bash
# Install istioctl
curl -L https://istio.io/downloadIstio | sh -
cd istio-1.x.x
export PATH=$PWD/bin:$PATH

# Install
istioctl install --set profile=default
```

Profiles: minimal, default, demo, ambient.

## Helm

```bash
helm install istio-base istio/base -n istio-system --create-namespace
helm install istiod istio/istiod -n istio-system
helm install istio-ingressgateway istio/gateway -n istio-system
```

For: GitOps.

## Verify

```bash
istioctl analyze
kubectl get pods -n istio-system
```

## Sidecar Injection

```bash
# Per-namespace auto-inject
kubectl label namespace prod istio-injection=enabled

# Per-pod opt-out
kubectl patch deploy myapp -p '{"spec":{"template":{"metadata":{"annotations":{"sidecar.istio.io/inject":"false"}}}}}'
```

## Manual Inject

```bash
istioctl kube-inject -f deployment.yaml | kubectl apply -f -
```

## Init Container

Injected:
- istio-init
- Sets iptables rules
- Redirects traffic to sidecar

Sidecar (istio-proxy):
- Envoy + pilot-agent
- Port 15001 (outbound)
- Port 15006 (inbound)
- Port 15090 (Prometheus metrics)

## Pod Traffic Flow

```
App outbound → iptables → Envoy 15001 → mTLS → other pod
Other pod → mTLS → Envoy 15006 → iptables → App inbound
```

Transparent.

## Profiles

```
minimal:    just istiod
default:    istiod + ingress gateway
demo:       all features (heavy)
ambient:    ambient mode
preview:    upcoming features
```

For prod: default.

## Resources

For 1000-pod cluster:
- istiod: 2-4 GB RAM (HA: 3 replicas)
- Sidecars: 100 MB × 1000 = 100 GB
- Ingress GW: 1-2 GB

Plan capacity.

## HA istiod

```yaml
spec:
  replicas: 3
  podAntiAffinity: ...
  topologySpreadConstraints: ...
```

For: failure tolerance.

## CA

istiod issues certs:
- SPIFFE: `spiffe://cluster.local/ns/NS/sa/SA`
- Auto-rotated (24h default)
- Embedded CA or external (Vault)

## External CA

```yaml
spec:
  values:
    pilot:
      env:
        ENABLE_CA_SERVER: "false"
        EXTERNAL_CA: "ISTIOD_RA_KUBERNETES_API"
```

For: enterprise PKI.

## xDS

Envoy fetches:
- LDS: Listeners
- RDS: Routes
- CDS: Clusters
- EDS: Endpoints

From istiod over gRPC.

Hot updates without restart.

## CRDs

```bash
kubectl get crd -l 'chart=istio'
# DestinationRule, VirtualService, Gateway, ServiceEntry, Sidecar, PeerAuthentication, AuthorizationPolicy, ...
```

## Telemetry

Built-in:
- Prometheus metrics (sidecar /stats/prometheus)
- Access logs
- Tracing (Jaeger, Zipkin, Datadog)

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: mesh-default
  namespace: istio-system
spec:
  tracing:
  - providers:
    - name: jaeger
```

## Gateway

Ingress:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: my-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: my-cert
    hosts:
    - "*.example.com"
```

Plus VirtualService binding routes.

## Egress

For controlled outbound:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: external-api
spec:
  hosts:
  - api.example.com
  ports:
  - number: 443
    name: https
    protocol: HTTPS
```

Sidecar allows / proxies to external.

## ServiceMesh + Cluster

Cluster-wide: every pod in mesh-enabled namespaces.

Cross-namespace: free.

Cross-cluster: more setup (multi-cluster).

## Multi-Cluster

```
Primary-Remote:
  Primary: istiod
  Remote: istiod connects to primary

Or Multi-Primary:
  Each cluster: own istiod, federated
```

For: cross-region.

## Resource Recommendations

```yaml
spec:
  components:
    pilot:
      k8s:
        resources:
          requests: { cpu: 500m, memory: 2Gi }
          limits:   { cpu: 1000m, memory: 4Gi }
```

Tune for cluster size.

## Sidecar Resource

```yaml
spec:
  global:
    proxy:
      resources:
        requests: { cpu: 100m, memory: 128Mi }
        limits: { cpu: 500m, memory: 256Mi }
```

Tune per workload.

## Best Practices

- HA istiod (3+ replicas)
- Per-namespace injection (not all)
- Resource limits on sidecars
- Telemetry to Prometheus + Jaeger
- mTLS strict in prod
- Upgrade quarterly
- Monitor istiod CPU/memory

## Common Mistakes

- All namespaces injected (kube-system etc.)
- Single istiod replica
- No resource limits (OOM)
- Skip upgrade (security)
- Verbose logging in prod (cost)

## Quick Refs

```bash
# Install
istioctl install --set profile=default

# Status
istioctl analyze
istioctl proxy-status

# Sidecar config
istioctl proxy-config cluster|listener|route|endpoint POD

# Bug report
istioctl bug-report

# Upgrade
istioctl upgrade
```

## Interview Prep

**Mid**: "Istio components."

**Senior**: "istiod role."

**Staff**: "Istio at scale."

## Next Topic

→ [T02 — Traffic Management (VirtualService, DestinationRule, Gateway)](T02-Traffic-Mgmt.md)
