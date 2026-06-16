# L26/C07 — Building a FinOps Practice

## Topics

- **T01 Anomaly Detection** — Spot cost spikes
- **T02 Forecasting & Budgets** — Plan
- **T03 Engineering Incentives** — Culture

## Anomaly Detection

### AWS Cost Anomaly Detection
- Free
- ML-based
- Per-account or per-service monitors
- Email alerts

### Vantage / Cloudability
- Real-time
- Smarter classification (root-cause analysis)
- Slack/PagerDuty integration

### DIY
- CUR + Athena
- Daily query for "service cost > 2 SD above 7-day average"
- Alert via SNS / Slack

### What to Catch
- A team spun up a $1000/day load test (forgot to stop)
- An untagged resource bloating to outsize cost
- A misconfigured logging shipper (10× ingest)
- A runaway Lambda recursion
- Anomalous egress

### Response Process
1. Anomaly fires → on-call notified
2. Identify resource and owner
3. Decide: terminate / contain / monitor
4. Document root cause
5. AI for prevention

## Forecasting

### Methods
- Linear regression on historical (simple, common)
- Per-product growth projections (top-down)
- Per-team allocations (bottom-up)
- ML (Prophet, ARIMA) — for sophisticated cases

### Tools
- AWS Cost Explorer forecasting
- Vantage / Apptio forecast
- Custom (CUR + Python + Prophet)

### Use
- Annual budget setting
- Spot capacity reservations
- Capacity decisions
- Migration ROI calculations

## Budgets

### AWS Budgets
- Set monthly/quarterly/annual
- Per service / per tag / per account
- Email + SNS on threshold (50%, 80%, 100%)

### Process
- Each team has a monthly budget
- 80% threshold → soft alert
- 100% threshold → escalate
- Over-budget → require justification + remediation plan

### Engineering Incentives

Cost should be visible to engineers continuously.

#### Visibility
- Cost dashboard per team in Grafana
- Service catalog (Backstage) shows cost per service
- PR-time cost estimation (Infracost)

#### KPIs
- Cost per request / per active user
- Cost per build (CI)
- Cost growth rate
- Cost efficiency (output / spend)

#### Recognition
- Cost win stories
- "Best optimization" awards
- Internal blog of savings achieved

#### Process
- Cost in design reviews
- Cost in OKRs (per quarter)
- Cost-aware architecture decisions

## Cost Tagging Enforcement

### SCP / Org Policy
Block resources without required tags:
```json
{
  "Effect": "Deny",
  "Action": "ec2:RunInstances",
  "Resource": "*",
  "Condition": {
    "Null": {"aws:RequestTag/team": "true"}
  }
}
```

### Cloud Custodian
Policies that auto-tag, alert, or remediate untagged resources.

## Centralized vs Decentralized Ownership

### Centralized FinOps Team
- Tooling + dashboards + reports
- Coordinate optimization initiatives
- Cross-team consistency

### Decentralized Engineering Ownership
- Each team owns their cost
- Daily decisions belong to engineers
- FinOps team coordinates, doesn't dictate

Mature orgs: centralized core (1-5 FTEs) + distributed engineer ownership.

## Monthly Operating Rhythm

### Week 1
- Last month's spend by team
- Anomalies + waste
- Action item review

### Week 2
- Team-by-team cost reviews
- Optimization opportunities

### Week 3
- Architecture / strategy reviews
- Major migration assessments

### Week 4
- Forecast + planning
- Budget vs actual
- Senior leadership report

## Cross-Functional Engagement

- **Finance**: budget alignment, accruals, forecasting
- **Product**: feature ROI, cost in roadmap
- **Engineering**: implementation, optimization
- **Leadership**: priorities, tradeoffs

Without finance and leadership engagement, engineers won't sustain effort.

## Cost as a Quality Signal

> If you can't pay for it sustainably, you can't run it.

Cost-out-of-control = architecture flaw, not just spending issue. Treat as engineering problem.

## Anti-Patterns

- **Cost-only KPIs** — engineers cut reliability
- **Surprise budget cuts** — no data → bad decisions
- **Manual review only** — doesn't scale
- **No automation** — engineers burn out
- **Finance owns FinOps** — without engineering = adversarial
- **Engineering owns FinOps** — without finance = no organizational lever

## Real Wins (typical year 1)

Starting points:
- 20-30% via right-sizing (every team)
- 25-40% via Savings Plans (compute baseline)
- 50-90% on dev (off-hours shutdown)
- 60-90% on batch (Spot)
- 20-40% on compute (Graviton)

Combined: 30-50% reduction in year 1 is realistic for unoptimized orgs.

## Interview Themes

- "Build a FinOps practice"
- "Anomaly detection — implementation"
- "Engineering incentives for cost"
- "Monthly cadence"
- "Common cost wins"
