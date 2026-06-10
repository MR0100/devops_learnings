# L26/C06/T01 — Kubecost / OpenCost

## Learning Objectives

- Allocate K8s cost
- Use tools

## Problem

K8s clusters:
- Multi-tenant
- Multi-team
- Multi-workload

Cloud bill: per-cluster.
Need: per-namespace / team / workload.

## OpenCost

CNCF open source:
- Cost allocation per pod / namespace / label
- Multi-cloud
- Prometheus-based

```bash
helm install opencost opencost-charts/opencost
```

## Kubecost

Commercial fork of OpenCost:
- UI rich
- More features
- Paid tier

## Allocation

Per pod:
- CPU * vCPU price (per node)
- Memory * RAM price
- Storage
- Network

For: actual cost per workload.

## Labels

Cost by labels:
- team
- app
- env
- cost-center

```
opencost: cost by namespace by team
```

## Reports

- Per namespace
- Per workload
- Per label
- Trends

## Recommendations

Kubecost:
- Right-size pods
- Reserved capacity
- Spot opportunities

## Multi-Cluster

- All clusters
- Aggregated view
- Federated

## Showback

Generate report:
- Team A: $X
- Team B: $Y
- Shared infra: $Z

For: chargeback / showback.

## Integration

- Slack alerts
- Prometheus
- Datadog
- Grafana

## Best Practices

- Install early
- Mandatory labels
- Monthly review
- Identify waste

## Common Mistakes

- No labels (can't allocate)
- Multi-cluster not aggregated
- No follow-up on recommendations

## Quick Refs

```bash
# Install
helm install opencost opencost-charts/opencost
helm install kubecost kubecost/cost-analyzer

# API
GET /allocation?window=7d&aggregate=namespace
GET /assets
```

## Interview Prep

**Mid**: "K8s cost."

**Senior**: "Allocation."

**Staff**: "FinOps for K8s."

## Next Topic

→ [T02 — Pod Right-Sizing](T02-Pod-Right-Sizing.md)
