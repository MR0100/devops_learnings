# L26/C02/T04 — Unit Economics (Cost per Request & per Tenant)

## Learning Objectives

- Define unit economics and why it beats absolute cloud spend as a signal
- Compute cost per request, per active user, and per tenant from allocated cost
- Use unit metrics to spot inefficiency that a falling total bill hides

## Why Unit Economics

The total cloud bill is a misleading signal on its own. A bill that *grows* may
be healthy (you're serving more traffic) and a bill that *shrinks* may be
hiding a problem (cost per request crept up while traffic fell). **Unit
economics** normalizes spend by a unit of business value — a request, an active
user, a tenant, a transaction — so you can tell efficiency from raw volume.

```
                 allocated cost (over a window)
unit cost  =  ─────────────────────────────────────
              units of business value (same window)
```

The headline metrics:

- **Cost per request** — infra cost ÷ requests served
- **Cost per active user** — infra cost ÷ MAU/DAU
- **Cost per tenant** — infra cost ÷ paying tenants (the B2B/SaaS lens)
- **Cost per transaction** — for commerce/payments
- **Gross margin** — (revenue − cost to serve) ÷ revenue

This is the bridge from FinOps to the business: finance and product think in
unit cost and margin, not in EC2-hours.

## Prerequisite: Allocation

You cannot compute a unit cost you can't allocate. Unit economics sits **on top
of** the allocation foundation from this chapter:

```
Tags / labels (T01)  →  allocated cost per service/team
        +
business-volume metric (requests, users, tenants)
        =
unit cost
```

If 30% of resources are untagged, the numerator is wrong and every unit metric
is off. Get allocation right first.

## Computing Cost per Request

Combine allocated cost (CUR/Kubecost) with a request count (load balancer
metrics, application metrics, or Prometheus):

```sql
-- Allocated cost for the API service this month (from CUR, by tag)
SELECT ROUND(SUM(line_item_unblended_cost), 2) AS api_cost_usd
FROM cur
WHERE year='2026' AND month='06'
  AND resource_tags['user_service'] = 'api';
```

```promql
# Requests served by the API over the same window
sum(increase(http_requests_total{service="api"}[30d]))
```

```
cost_per_request = api_cost_usd / requests
# e.g. $42,000 / 8.4e9 req = $0.000005 per request ($5 per million)
```

Track it as a time series, not a one-off number. A *rising* cost-per-request
while traffic is flat is the early-warning signal that an inefficiency (an
oversized fleet, a chatty new dependency, a hot retry loop) crept in — even
while the absolute bill looks fine.

## Cost per Tenant (the SaaS lens)

For multi-tenant SaaS, per-tenant cost is the metric that drives pricing and
identifies unprofitable customers. The challenge is **shared infrastructure**:
most cost is in pooled compute/DB/cache that no single tenant "owns."

Attribution approaches, cheapest to most precise:

| Approach            | How                                              | Precision |
|---------------------|--------------------------------------------------|-----------|
| Even split          | Total ÷ tenant count                             | Low       |
| Usage-weighted      | Split shared cost by each tenant's request/CPU share | Medium |
| Tenant labels       | Tag/label requests/pods by `tenant_id`; allocate via Kubecost | High |
| Dedicated resources | Per-tenant namespace/DB (rare; only for big tenants) | Exact  |

```promql
# Usage-weighted: each tenant's share of API requests this window
sum by (tenant_id) (increase(http_requests_total{service="api"}[30d]))
  / ignoring(tenant_id) group_left
sum(increase(http_requests_total{service="api"}[30d]))
```

Multiply each tenant's share by the shared API cost to get a usage-weighted
per-tenant cost. The output exposes the classic SaaS finding: a small number of
**whale tenants** drive a disproportionate share of cost, and some low-revenue
tenants cost more to serve than they pay.

## What Unit Metrics Reveal

- **Efficiency trend** — cost per request over time, independent of growth
- **Margin by tenant/plan** — which customers or tiers are unprofitable
- **Regression detection** — a deploy that doubled cost per request
- **Right-sizing targets** — services with the worst cost-per-request first
- **Pricing inputs** — set plan prices above cost-to-serve with margin

```
Bill ↓ but cost/request ↑  → efficiency regressed; investigate
Bill ↑ but cost/request ↓  → healthy scaling; you got more efficient
```

## Putting It on a Dashboard

Per team/service, alongside the absolute cost:

- Cost per request (and per 1M requests), trended
- Cost per active user (DAU/MAU)
- Cost per tenant, with a top-N "most expensive tenants" list
- Gross margin per plan (if revenue data is available)

Surfacing unit cost — not just total cost — is what turns a FinOps dashboard
into a product/business tool engineers and PMs actually use (ties into the
engineering-incentives KPIs in C07).

## Common Mistakes

- Watching only the total bill — a flat bill can hide rising cost per request
- Computing unit cost on a broken allocation (untagged resources skew the numerator)
- Even-splitting shared cost across tenants — buries the whales and the unprofitable ones
- Mismatched windows — cost for the month ÷ requests for a day gives nonsense
- Ignoring fixed/baseline cost when traffic is low → per-request cost looks alarming but is just under-utilization
- Treating unit cost as exact when shared-infra attribution is necessarily an estimate

## Best Practices

- Allocate first (tags/labels), then divide by a clean business-volume metric
- Track unit cost as a trended time series, not a single number
- Use usage-weighted or label-based attribution for per-tenant cost; avoid even splits
- Always pair the absolute bill with a unit metric so efficiency is visible
- Surface a "top N most expensive tenants/endpoints" view to drive action
- Feed margin-by-tenant/plan back to product so pricing covers cost-to-serve

## Quick Refs

```
cost per request = allocated_cost / requests_served    (same window!)
cost per user    = allocated_cost / active_users
cost per tenant  = shared_cost × tenant_usage_share + dedicated_cost
gross margin     = (revenue − cost_to_serve) / revenue

Signal: bill flat + cost/request ↑ = efficiency regression
Tenant attribution: even < usage-weighted < label-based < dedicated
```

## Interview Prep

**Junior**: "What are unit economics in cloud cost?" — Cost normalized by a unit of business value — cost per request, per active user, per tenant — instead of the raw total bill. It tells you whether you're getting more or less efficient, separate from how much traffic grew.

**Mid**: "Why track cost per request instead of the total bill?" — The total bill conflates volume and efficiency. Cost per request isolates efficiency: if the bill is flat but cost per request is rising, an inefficiency crept in even though spend looks fine; if the bill grows but cost per request falls, you're scaling healthily.

**Senior**: "How do you compute cost per tenant on shared infrastructure?" — Allocate shared cost by each tenant's usage share — tag or label requests/pods with `tenant_id` and let Kubecost/CUR split pooled compute and DB by that share, plus any dedicated resources. Avoid even-splitting, which hides whale tenants and low-revenue tenants that cost more to serve than they pay.

**Staff**: "How do unit economics change architecture and pricing decisions?" — They turn cost into a per-customer/per-plan margin signal: you identify unprofitable tenants and plans, set prices above cost-to-serve, target the worst cost-per-request services for re-architecture, and catch deploys that regress efficiency before the bill grows. It requires solid allocation (tags/labels) and trended unit metrics on shared dashboards so product, finance, and engineering reason about the same numbers.

## Next Topic

→ Move to [L26/C03 — Compute Optimization](../C03/README.md)
