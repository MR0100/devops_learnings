# L30/C05/T03 — Cost Dashboards

## Learning Objectives

- Visualize cost
- Per-team

## Why Cost Dashboards Close the Loop

Saving 70% on Spot is invisible unless you can *show* it — and you can't optimize
what you can't attribute. This topic makes the savings real: it turns a lump-sum
AWS bill into per-team, per-service cost, which is what enables **showback**
(everyone sees their spend) and, eventually, **chargeback** (teams own their
budget). The hard problem in Kubernetes specifically is that a shared cluster's
bill doesn't come itemized by team — you have to *allocate* it.

### The Allocation Problem (and OpenCost/Kubecost's job)

A node costs $X/hour, but ten teams' pods share it. OpenCost/Kubecost solve this
by attributing each pod's share of node cost based on its resource *requests*
(and actual usage), then rolling that up by namespace and by label. That's why
**labeling discipline is the prerequisite** — a pod with no `team` label is
unattributable cost, and "unallocated" is where showback credibility goes to die.

### Rationale & Trade-offs

- **OpenCost (free, CNCF) vs Kubecost (commercial)** — OpenCost gives the core
  allocation engine and Prometheus metrics for free; Kubecost adds a richer UI,
  savings recommendations, and multi-cluster. Note OpenCost was *donated by*
  Kubecost — same lineage. OpenCost is the right call for a capstone.
- **K8s allocation (OpenCost) vs cloud detail (CUR + Athena)** — OpenCost covers
  in-cluster spend; the AWS Cost and Usage Report covers everything else (RDS,
  S3, data transfer). A complete FinOps picture needs both.
- **Request-based allocation rewards right-sizing** — because cost follows
  requests, over-requesting shows up as cost, which nudges teams to set
  realistic requests. That's a feature.

## OpenCost

```bash
helm install opencost opencost-charts/opencost
```

Allocates shared K8s cost down to:
- Per namespace
- Per pod
- Per label (team, cost-center) — only as good as your labeling

## Grafana

Datasource: Prometheus (OpenCost metrics).

Dashboards:
- Total cost
- Per team
- Per namespace
- Trends

## Sample Queries

```promql
sum by (namespace) (
  pod_memory_request_avg{} * pod_memory_unit_price
  + pod_cpu_request_avg{} * pod_cpu_unit_price
)
```

For: per-namespace cost.

## Showback

Monthly report:
```
Team A: $20k
Team B: $15k
Team C: $10k
```

Trend up/down.

## CUR + Athena (AWS)

For non-K8s:
```sql
SELECT line_item_resource_tags_user_team, SUM(line_item_unblended_cost)
FROM cur
WHERE month = '2026-01'
GROUP BY 1
ORDER BY 2 DESC
```

## CUDOS

AWS-built dashboards:
- Pre-built
- QuickSight

For: starting point.

## Vantage / Cloudability

Commercial:
- Multi-cloud
- Anomaly detection

## Alerts

```promql
# Budget exceeded
sum(team_cost{team="A"}) > 25000
```

Notify Slack.

## Best Practices

- Per-team visibility
- Tagging strict
- Anomaly alerts
- Quarterly review

## Common Mistakes

- No tagging
- No alerts
- Dashboard nobody sees

## Acceptance Criteria

- OpenCost allocates cluster cost per namespace and per team label
- A Grafana dashboard shows total cost, per-team breakdown, and a trend
- "Unallocated" cost is near zero (proves labeling discipline)
- The Spot before/after savings is visible as a number on the dashboard
- A budget-exceeded alert fires to Slack

## Quick Refs

```
OpenCost: in-cluster allocation (free, CNCF; donated by Kubecost)
Kubecost: + UI, savings recs, multi-cluster (commercial)
CUR + Athena: AWS-wide detail (RDS/S3/transfer)   CUDOS: prebuilt AWS dashboards
Allocation follows requests → labeling discipline is the prerequisite
```

## Interview Prep

**Junior**: "What does a tool like OpenCost do?" — It takes the cost of your
Kubernetes nodes and splits it across the pods running on them, so you can see
how much each namespace, team, or service is spending — instead of just one big
cluster bill.

**Mid**: "Why is cost allocation harder in Kubernetes than on raw cloud?" —
Because a node is shared. Ten teams' pods run on the same instance, so the AWS
bill says 'one m6i.large,' not 'team A used 30% of it.' OpenCost/Kubecost
allocate each pod's share of the node cost based on its resource requests and
usage, then roll it up by namespace and label. That only works if pods are
labeled with an owner — unlabeled pods become 'unallocated' cost nobody owns.

**Senior**: "How do you turn cost data into actual savings behavior?" — Visibility
is necessary but not sufficient — a dashboard nobody looks at changes nothing. I'd
make it operational: per-team showback delivered where teams already work (a
monthly report, a Slack digest), with trend and anomaly alerts so a cost spike is
noticed in days not at month-end. Because allocation follows resource requests,
over-provisioning shows up as cost, which gives teams a concrete reason to
right-size — and I'd pair the dashboard with efficiency metrics
(usage/request) so the conversation is 'you're requesting 4x what you use,' not
just 'you're expensive.' The goal is to make cost a feedback signal teams act on,
not a finance report they ignore.

**Staff**: "How do you stand up a FinOps practice that actually controls cloud
spend at org scale?" — Three pillars, in order. First, **visibility and
attribution** — get to near-zero unallocated cost with enforced labeling
(unlabeled = blocked or auto-tagged), combining in-cluster allocation (OpenCost)
with the cloud CUR for everything else, so every dollar has an owner. Second,
**accountability** — move from showback (you can see your spend) to chargeback or
budgets (you own your spend), so teams have skin in the game; cost becomes a
metric they're measured on alongside reliability. Third, **optimization as a
flywheel** — bake the wins into the platform: right-sizing recommendations,
Spot-by-default in the golden path, Savings Plans/Reserved coverage for the
stable baseline, and automated anomaly detection. The staff framing for
leadership is *unit economics* — cost per request, per tenant, per transaction —
because absolute spend going up is fine if it's going up slower than revenue. A
FinOps program that only reports numbers fails; one that changes defaults and
gives teams ownership is what bends the curve.

## Next Topic

→ Move to [L30/C06 — Portfolio Presentation](../C06/README.md)
