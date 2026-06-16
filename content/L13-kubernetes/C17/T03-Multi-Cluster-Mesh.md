# L13/C17/T03 — Multi-Cluster Service Mesh

## Learning Objectives

- Connect services across clusters
- Use Istio / Cilium multi-cluster

## Why Multi-Cluster Mesh

Cross-cluster service-to-service:
- Service discovery across clusters
- mTLS (secure)
- Failover
- Locality routing

Without mesh: apps know cluster endpoints; manage manually.

## Istio Multi-Cluster

Modes:
- **Single mesh, single network**: clusters in same flat network
- **Single mesh, multi-network**: clusters in different VPCs (most common)
- **Multi-mesh**: federated meshes

## Single Mesh, Multi-Network

Each cluster: Istio control plane + sidecars.
Mesh: shared trust domain.

Cross-cluster:
- East-west gateway in each cluster
- mTLS through gateway
- Endpoints shared via API

```yaml
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
spec:
  values:
    global:
      meshID: mesh1
      multiCluster:
        clusterName: cluster-a
      network: network-a
```

## Setup

1. Install Istio in cluster A (multi-cluster mode)
2. Install in cluster B
3. Configure same root CA (trust)
4. Expose east-west gateway
5. Register remote endpoints

```bash
# Cluster A → B (and vice versa)
istioctl x create-remote-secret --context=cluster-b --name=cluster-b | kubectl apply --context=cluster-a -f -
```

Sidecars in A can route to B's services.

## Service Discovery

Service in cluster B:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: api-svc
  namespace: prod
```

From cluster A, app calls `api-svc.prod.svc.cluster.local` → Istio routes to B's gateway → B's pod.

Transparent.

## Cilium ClusterMesh

eBPF-based multi-cluster:
```bash
cilium clustermesh enable --context=cluster-a
cilium clustermesh enable --context=cluster-b
cilium clustermesh connect --context=cluster-a --destination-context=cluster-b
```

Cilium agents share data; pods route directly cross-cluster (without separate gateway).

For: lower overhead, eBPF performance.

## Linkerd Multi-Cluster

```bash
linkerd multicluster install | kubectl apply -f -
linkerd multicluster link --cluster-name=cluster-b | kubectl apply -f -
```

Mirror services from cluster B to A. Apps call mirrored service.

For: simpler than Istio; lighter.

## Failover

Service in A fails:
- Mesh routes to B
- Automatic; no app change

For: HA across regions.

```yaml
# Istio DestinationRule for failover
spec:
  trafficPolicy:
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
```

After 5 errors: pod ejected; mesh routes elsewhere.

## Locality Routing

Prefer local:
```yaml
spec:
  trafficPolicy:
    localityLbSetting:
      enabled: true
      distribute:
      - from: region1/zone1
        to:
          "region1/zone1": 80
          "region1/zone2": 20
```

80% within zone; 20% to nearby zone.

For: latency optimization.

## mTLS Across Clusters

```yaml
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata:
  name: default
spec:
  mtls:
    mode: STRICT
```

All cross-cluster traffic encrypted + authenticated.

## Trust Domain

All clusters share root CA (trust domain).

```yaml
spec:
  values:
    global:
      meshID: prod-mesh
```

For: identity portability.

## Observability

Istio:
- Traces (Jaeger / Tempo)
- Metrics (Prometheus)
- Logs

For multi-cluster: aggregate to central.

Hubble (Cilium): cross-cluster flow visibility.

## Cilium ClusterMesh vs Istio

| | Istio | Cilium |
|---|---|---|
| Architecture | Sidecar | eBPF (no sidecar) |
| Overhead | High (sidecar per pod) | Lower (kernel) |
| Maturity | Highest | Growing |
| L7 features | Many | Some (newer) |
| Multi-cluster | Complex | Simpler |

For new: try Cilium.
For mature mesh users: Istio multi-cluster.

## Linkerd

Lightweight; simpler than Istio. Multi-cluster via service mirroring.

For: simpler needs.

## Cross-Cluster Traffic Costs

Mesh adds:
- Sidecar latency (1-5 ms)
- Gateway hops (cross-cluster)
- Egress charges (cloud cross-region)

For: optimize locality; budget for traffic.

## When Multi-Cluster Mesh

- HA: failover services
- Latency: local routing
- Migration: shift traffic gradually
- Compliance: data per region with cross-region for non-sensitive

## When NOT

- Single cluster sufficient
- Apps can use external LB
- Cost-sensitive
- No mesh expertise

For simple multi-region: LB + DNS at edge; not mesh.

## Alternatives

Without mesh:
- ExternalDNS + Route53 latency
- Global LB (Cloud)
- App-level discovery (Consul)

Mesh: more features but more overhead.

## Setup Complexity

Istio multi-cluster: weeks of setup + testing.
Cilium ClusterMesh: hours.
Linkerd multi-cluster: hours.

For: pick simplest for need.

## Production Considerations

- Cross-cluster network (peering, TGW, VPN)
- Latency between clusters
- Bandwidth
- Trust + auth
- Monitoring across
- Disaster scenarios (cluster fail)

## Trust Bundle

For mTLS:
- Each cluster: own intermediate CA
- Shared root CA
- Bundle distributed

Manage via SPIRE or cert-manager.

## Federation Old

Service Catalog (legacy). Modern: mesh-based or Karmada-based.

## Networking Models

### Flat
All clusters in same network; pods route directly.

Simplest but requires VPC peering or shared network.

### Multi-Network
Clusters in own networks; gateway between.

Most common.

### Hybrid
Mix.

## Best Practices

- Pick simplest mesh fitting need
- Test failover regularly
- Monitor cross-cluster latency
- Budget for cross-region traffic
- Identity strategy (SPIRE)
- Locality routing for latency

## Common Mistakes

- Multi-cluster without traffic plan
- Not testing failover
- Forgetting cross-cluster cost
- Trust setup wrong

## Use Cases by Example

### Global E-Commerce
- Cluster per region (US, EU, ASIA)
- Mesh for failover (if US down, route to EU)
- Locality routing for latency

### SaaS Multi-Region
- Customers in different regions
- App + DB per region
- Mesh for cross-region admin / metrics

### Hybrid Cloud
- On-prem + AWS
- Mesh bridges
- Gradual migration

## Quick Refs

```bash
# Istio multi-cluster
istioctl install --set values.global.meshID=mesh1 \
  --set values.global.multiCluster.clusterName=cluster-a \
  --set values.global.network=network-a

istioctl x create-remote-secret --context=cluster-b --name=cluster-b

# Cilium
cilium clustermesh enable
cilium clustermesh connect --destination-context=cluster-b

# Linkerd
linkerd multicluster link --cluster-name=cluster-b
```

## Interview Prep

**Mid**: "Multi-cluster mesh purpose."

**Senior**: "Istio multi-cluster modes."

**Staff**: "Global service architecture with mesh."

## Next Topic

→ [T04 — Crossplane](T04-Crossplane.md)
