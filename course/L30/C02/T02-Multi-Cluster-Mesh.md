# L30/C02/T02 — Federation / Multi-Cluster Service Mesh

## Learning Objectives

- Federate clusters
- Cross-cluster mesh

## Federation

### Cluster Federation
- API server federation (deprecated)
- ArgoCD: per-cluster
- KubeFed (limited adoption)

### Multi-Cluster Service Mesh
- Istio multi-cluster
- Linkerd multi-cluster
- Cilium cluster mesh

## Istio Multi-Cluster

Modes:
- Primary-Remote
- Multi-Primary

```bash
istioctl install --set values.global.meshID=mesh1 \
  --set values.global.multiCluster.clusterName=cluster1
```

## Cross-Cluster Service Discovery

Service in cluster A reachable from cluster B:
- mTLS
- DNS or env
- Mesh-aware

```yaml
# Istio ServiceEntry
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
spec:
  hosts:
    - foo.cluster-b.local
  location: MESH_INTERNAL
  ports:
    - number: 80
      protocol: HTTP
  endpoints:
    - address: foo.cluster-b.local
```

## Cilium Cluster Mesh

```bash
cilium clustermesh enable
cilium clustermesh connect --destination-context other-cluster
```

For: pod IPs reachable across clusters.

## Failover

Service in cluster A unhealthy:
- Mesh routes to cluster B
- Locality-based LB

```yaml
trafficPolicy:
  localityLbSetting:
    enabled: true
    failover:
      - from: us-east-1
        to: us-west-2
```

## Use Cases

### Geographic
Users → nearest cluster.

### Failover
Cluster down → other.

### Multi-Tenant
Tenant per cluster.

## Best Practices

- One control plane per cluster
- Federated config (Git-based)
- mTLS across
- Locality LB

## Common Mistakes

- Tightly coupled (single ArgoCD for all)
- No mTLS cross-cluster
- Manual config sync

## Quick Refs

```
Mesh: Istio / Linkerd / Cilium
Discovery: ServiceEntry / Cluster Mesh
Failover: Locality LB
GitOps: ArgoCD ApplicationSet
```

## Next Topic

→ [T03 — Cross-Region Failover](T03-Multi-Cluster-Failover.md)
