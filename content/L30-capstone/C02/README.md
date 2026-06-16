# L30/C02 — Project 2: Multi-Region Kubernetes Platform

## Topics

- **T01 Cluster Topology** — Layout
- **T02 Federation / Multi-Cluster Service Mesh** — Cross-region
- **T03 Cross-Region Failover** — DR demonstration

## Goal

Two EKS clusters in two regions, with cross-region service mesh and failover demonstration.

## Architecture

```
[Route 53 latency policy]
   ↓
   ├──→ [us-east-1: EKS] ──→ App pods + DB
   └──→ [us-west-2: EKS] ──→ App pods + DB
              │
   [Istio multi-cluster mesh]
   - Service discovery cross-region
   - mTLS
   - Locality-weighted load balancing
```

## Cluster Setup

```bash
# Region 1: us-east-1
eksctl create cluster --name=east --region=us-east-1 \
  --version=1.30 --node-type=m6i.large --nodes=3

# Region 2: us-west-2
eksctl create cluster --name=west --region=us-west-2 \
  --version=1.30 --node-type=m6i.large --nodes=3
```

## Istio Multi-Cluster (Primary-Remote)

```bash
# Install Istio on both with shared root CA
istioctl install --context east --set values.global.meshID=mesh1 \
  --set values.global.network=east --set values.global.multiCluster.clusterName=east

istioctl install --context west --set values.global.meshID=mesh1 \
  --set values.global.network=west --set values.global.multiCluster.clusterName=west

# Cross-cluster connectivity
istioctl create-remote-secret --context east --name east | kubectl apply --context west -f -
istioctl create-remote-secret --context west --name west | kubectl apply --context east -f -
```

## Cross-Cluster Service Discovery

```yaml
apiVersion: networking.istio.io/v1
kind: VirtualService
metadata:
  name: my-app
spec:
  hosts: ["my-app.example.com"]
  http:
    - route:
        - destination: { host: my-app.east.svc.cluster.local }
          weight: 100   # locality-weighted; adjust on failure
```

Locality-aware: prefer local region, failover to remote.

## Database Strategy

### Option 1: Aurora Global Database
- Primary in one region (writes)
- Replica in other (reads + failover)
- Manual promotion on primary failure

### Option 2: DynamoDB Global Tables
- Multi-region multi-active
- LWW conflict resolution
- Simpler

For demo: DynamoDB Global Tables (easier to demo).

## Stateless App Multi-Region

```yaml
# Same Deployment in both clusters
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  template:
    spec:
      containers:
        - name: app
          image: ghcr.io/me/app:v1
          env:
            - name: REGION
              value: us-east-1   # different per cluster
            - name: DDB_TABLE
              value: global-table
```

## Route 53 Failover

```hcl
resource "aws_route53_health_check" "east" {
  fqdn = "east.api.example.com"
  type = "HTTPS"
  resource_path = "/healthz"
  failure_threshold = 3
  request_interval = 30
}

resource "aws_route53_record" "api_east" {
  zone_id = aws_route53_zone.main.zone_id
  name = "api.example.com"
  type = "A"
  
  set_identifier = "east"
  failover_routing_policy { type = "PRIMARY" }
  
  alias {
    name = aws_lb.east.dns_name
    zone_id = aws_lb.east.zone_id
    evaluate_target_health = true
  }
  health_check_id = aws_route53_health_check.east.id
}

resource "aws_route53_record" "api_west" {
  zone_id = aws_route53_zone.main.zone_id
  name = "api.example.com"
  type = "A"
  
  set_identifier = "west"
  failover_routing_policy { type = "SECONDARY" }
  
  alias {
    name = aws_lb.west.dns_name
    zone_id = aws_lb.west.zone_id
    evaluate_target_health = true
  }
}
```

## Failover Demo

### Manual Test
1. Verify both regions healthy: `curl api.example.com`
2. Simulate east failure: Scale east deployment to 0
3. Health check fails
4. Route 53 routes to west
5. Verify: `curl api.example.com` → goes to west
6. Restore east; traffic returns

### Game Day Mode
- Plan + brief team
- Trigger; verify
- Document timing (RTO measurement)

## Failover Time Budget

```
Detection: 30s × 3 failures = 90s
DNS propagation: TTL 60s; client caching adds ~60s more
Total: ~3 min realistic
```

For sub-minute: use Global Accelerator (anycast IPs) instead of DNS.

## Cross-Region Observability

Federated Grafana:
- Each cluster has Prometheus
- Mimir aggregates both
- One Grafana queries both

Loki: separate per region; Grafana queries both with `cluster` label.

Tempo: similar; trace context propagates cross-region via OTel.

## Argo CD Multi-Cluster

One Argo CD manages both clusters:
```bash
argocd cluster add east
argocd cluster add west

# Application per cluster:
argocd app create my-app-east --dest-server <east-api> ...
argocd app create my-app-west --dest-server <west-api> ...

# Or ApplicationSet across clusters:
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
spec:
  generators:
    - clusters: {}     # all registered clusters
  template:
    metadata: { name: '{{name}}-app' }
    spec:
      source: { repoURL: ..., path: app }
      destination: { server: '{{server}}', namespace: app }
```

## Demo Script

10-min Loom:
1. Architecture (1 min)
2. Show both clusters healthy (1 min)
3. Verify cross-cluster discovery (1 min)
4. Demonstrate locality-weighted routing (2 min)
5. Trigger east failure; show failover (3 min)
6. Recovery (1 min)
7. Lessons (1 min)

## Cost
- 2 EKS control planes: $146/month
- 6 m6i.large worker nodes: $300/month
- Aurora Global / DynamoDB: ~$100/month
- Cross-region traffic: $20-50/month
- Total: ~$600/month

Don't leave running. Bring up for demo, tear down.

## What to Highlight

- True multi-region, not just multi-AZ
- Sub-minute failover (Global Accelerator) or 3-min (Route 53)
- mTLS preserved across regions
- Operationally observable
- Reasonable cost

## README Template

```markdown
# Multi-Region Kubernetes Platform

## Demo
- 2 EKS clusters, 2 regions
- Istio multi-cluster mesh
- Cross-region service discovery + failover
- DynamoDB Global Tables
- Route 53 failover

## Failover Time
Measured RTO: 2 min 45 seconds

## How to Run
[steps]

## What I Learned
[specific findings]
```

## Interview Themes

- "Multi-region design tradeoffs"
- "How did you handle cross-region state?"
- "Failover time achieved?"
- "What's the cost?"
- "Locality-aware routing"
