# L08/C08/T05 — App Mesh

## Learning Objectives

- Understand App Mesh
- Decide vs Istio / Linkerd

## App Mesh

AWS managed service mesh based on Envoy proxy.

Note: AWS announced App Mesh end-of-life September 2026. Migrate to alternatives.

## What Service Mesh

Layer between services for:
- mTLS
- Traffic routing (weighted, canary)
- Retries / timeouts
- Circuit breaking
- Observability
- Authorization

Implemented via sidecar proxies (Envoy) on each pod / task.

## App Mesh Components

- **Mesh**: top-level container
- **Virtual Service**: abstract service name
- **Virtual Node**: actual service implementation (ECS task, EKS deployment)
- **Virtual Router**: traffic routing
- **Virtual Gateway**: ingress
- **Route**: rules within router

```
Mesh
└── Virtual Service (orders.example.com)
    └── Virtual Router
        └── Routes (weighted)
            ├── Virtual Node v1 (90%)
            └── Virtual Node v2 (10%)
```

## Integration

ECS / EKS / Fargate. Envoy sidecar added.

ECS task with App Mesh:
```json
{
  "containerDefinitions": [
    {
      "name": "envoy",
      "image": "840364872350.dkr.ecr.us-west-2.amazonaws.com/aws-appmesh-envoy:v1...",
      "essential": true
    },
    {
      "name": "app",
      "image": "myapp:v1",
      "dependsOn": [{"containerName": "envoy", "condition": "HEALTHY"}]
    }
  ],
  "proxyConfiguration": {
    "type": "APPMESH",
    "containerName": "envoy",
    "properties": [...]
  }
}
```

## Features

### mTLS
Sidecars handle TLS; mutual auth via ACM Private CA.

### Traffic Routing
Weighted routes for canary:
```
Service v1: 90%
Service v2: 10%
```

### Retries
Per route:
- Max attempts
- Backoff
- Per HTTP status code

### Timeouts
Per route: idle / per-request.

### Circuit Breaking
Outlier detection: remove unhealthy hosts.

### Observability
Envoy emits metrics, traces (X-Ray integration).

## App Mesh vs Istio / Linkerd / Cilium

| | App Mesh | Istio | Linkerd | Cilium |
|---|---|---|---|---|
| Managed | Yes | No (or by Anthos) | No | No |
| AWS integration | Native | Add-on | Add-on | Add-on |
| Lock-in | High | Low | Low | Low |
| Features | Decent | Most | Lean | eBPF-based |
| Community | Smaller | Huge | Solid | Growing |
| 2025 status | EOL | Active | Active | Hot |

For new: Istio, Linkerd, or Cilium (App Mesh EOL Sep 2026).

## When Service Mesh

- Many microservices (10+) talking to each other
- mTLS required
- Need traffic routing (canary)
- Centralized observability

For 5 services: mesh overhead > benefit. App-level libraries.

## Why Not App Mesh in 2025+

EOL Sep 2026. Don't start new App Mesh projects.

Existing migrations to:
- Istio (most full-featured)
- Linkerd (simplest)
- AWS VPC Lattice (managed; service-to-service communication)
- Cilium (eBPF; high perf)

## VPC Lattice

AWS service for service-to-service (alternative to mesh):
- Managed by AWS
- No sidecar
- HTTP/gRPC routing
- IAM-based auth
- Cross-account / cross-VPC

For: simple service-to-service; AWS-native; no sidecar.

vs Service Mesh:
- Lattice: simpler; less features
- Mesh: rich features; sidecar overhead

For most: Lattice is easier path.

## Cilium / Service Mesh Mode

Cilium (CNI) has mesh mode:
- eBPF (no sidecar)
- L7 routing
- Lower overhead than Envoy sidecar
- Newer; less mature

Promising; evaluate.

## When Each

| Use case | Pick |
|---|---|
| AWS-native; simple svc-to-svc | VPC Lattice |
| K8s; full mesh; mature | Istio |
| K8s; minimal | Linkerd |
| K8s; performance | Cilium |
| Existing App Mesh | Migrate before EOL |

## VPC Lattice

```yaml
# Service network: group of services
# Service: HTTP/gRPC endpoint with targets (ALB, ECS, EC2)
# Target Group: who serves the traffic
```

```bash
aws vpc-lattice create-service-network --name my-network
aws vpc-lattice create-service --name my-service --target-group ...
```

Cost: per-hour + per-request + data.

## Service Mesh Costs

Generally:
- Envoy: ~50-100 MB RAM per sidecar
- ~5-10% CPU overhead per sidecar
- Mesh control plane

For 100 pods: extra ~10 GB RAM. Real cost.

## Migration App Mesh → Istio

1. Stand up Istio cluster (or add to EKS)
2. Gradually move services
3. Same Envoy underneath; config translates
4. Cut over; retire App Mesh

Process takes months for large fleets.

## Observability

App Mesh + X-Ray: traces.
Plus CloudWatch metrics from Envoy.
Plus structured logs.

For Istio: Prometheus + Grafana + Jaeger / Tempo stack.

## App Mesh Limits

- Number of meshes per region
- Virtual services per mesh
- Routes per router

Check current quotas.

## Common Mistakes (Historical)

- Adopting App Mesh in 2025+ (EOL)
- Mesh for 3 services (overkill)
- Skipping observability
- Manual Envoy configs

## Best Practices (Forward)

- Lattice for simple AWS-native
- Istio for full features
- Linkerd for simplicity
- Cilium if eBPF needs
- Plan observability from start
- mTLS by default

## What To Tell Interviewers

If asked about App Mesh:
- Know it exists; managed Envoy
- Note: EOL 2026
- Discuss alternatives (Istio, Linkerd, VPC Lattice)

For service mesh design questions: pick Istio or Linkerd typically.

## Migration Strategy

For App Mesh users:
1. Inventory current mesh usage
2. Pick replacement
3. Test in staging
4. Migrate workload by workload
5. Decommission App Mesh

## Quick Refs

```bash
# Old App Mesh (avoid for new)
aws appmesh create-mesh --mesh-name my-mesh
aws appmesh create-virtual-service ...

# VPC Lattice
aws vpc-lattice create-service-network --name my-network
aws vpc-lattice create-service --name my-svc ...
```

## Interview Prep

**Mid**: "Service mesh — what."

**Senior**: "VPC Lattice vs Istio."

**Staff**: "Migrate from App Mesh."

## Next Topic

→ Move to [L08/C09 — Edge Services](../C09/README.md)
