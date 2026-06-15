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

CNCF open source — the open core, **created and donated by Kubecost** (the
company), not the other way around:
- Cost allocation per pod / namespace / label
- Multi-cloud
- Prometheus-based
- Vendor-neutral spec for in-cluster cost monitoring

```bash
helm install opencost opencost-charts/opencost
```

## Kubecost

Commercial product **built on top of OpenCost** (Kubecost donated OpenCost to
the CNCF; OpenCost is the engine, Kubecost is the productized layer). It is
*not* a fork of OpenCost — the lineage runs the other direction:
- Rich UI and dashboards
- More features (savings recommendations, alerts, SSO, multi-cluster)
- Free tier + paid Enterprise tier

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

**Junior**: "Why do you need Kubecost/OpenCost?" — The cloud bill is per-cluster, but a cluster is multi-tenant, so you can't see which team or workload drove the cost. OpenCost/Kubecost allocate the node cost down to pods/namespaces/labels using Prometheus metrics, giving per-team cost.

**Mid**: "How is per-pod cost calculated?" — Each pod is charged for its share of node resources: CPU used (or requested) × the node's vCPU price, memory × RAM price, plus storage and network. Summing by label/namespace gives per-team allocation, and the gap between requests and usage is the 'idle' cost you can reclaim.

**Senior**: "Kubecost vs OpenCost — what's the relationship?" — OpenCost is the CNCF open-source allocation engine that Kubecost (the company) created and donated; Kubecost is the commercial product built *on top of* OpenCost, adding UI, savings recommendations, alerts, SSO, and multi-cluster aggregation. Kubecost is not a fork of OpenCost — the lineage is the other way around.

**Staff**: "How would you run FinOps for Kubernetes across many teams?" — Make labels (team/app/env/cost-center) mandatory and enforced so allocation is possible, deploy OpenCost/Kubecost with multi-cluster aggregation, surface per-namespace cost and idle (request-vs-usage) back to teams as showback, wire alerts on cost spikes, and feed the right-sizing/bin-packing/spot recommendations into a monthly review loop so the data drives action rather than sitting in a dashboard.

## Next Topic

→ [T02 — Pod Right-Sizing](T02-Pod-Right-Sizing.md)
