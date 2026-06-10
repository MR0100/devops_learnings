# L26/C01/T02 — Inform, Optimize, Operate Phases

## Learning Objectives

- Apply FinOps phases
- Move through

## Inform

Visibility:
- Tag all resources
- Reports per team / project
- Trends
- Forecasts

Tools:
- AWS Cost Explorer
- Azure Cost Management
- GCP Billing
- Vantage / CloudHealth

## Outputs

- Dashboards
- Anomaly alerts
- Per-team budgets

## Optimize

Action:
- Right-size (T01 / C03)
- Reserved Instances (T02)
- Spot (T03)
- Storage tiers (C04)
- Delete unused

Continuous improvement.

## Operate

Embedded:
- FinOps in roadmap
- Cost in PRR
- Anomaly auto-mitigation
- Culture

## Cycle

```
Inform → Optimize → Operate
   ↑                    ↓
   ← Continuous loop ←
```

For: iterative.

## Inform Examples

```
This month:
- EC2: $40k (up 10%)
- S3: $15k (stable)
- Network: $5k
Per team:
- Team A: $30k
- Team B: $25k
```

For: visibility.

## Optimize Examples

- Idle EC2 stopped: saves $5k/mo
- 3-yr Savings Plan: saves 50% on stable
- Spot for batch: saves 70%
- S3 lifecycle: saves $3k/mo

## Operate Examples

- Tag at create (Terraform module)
- Cost alert at 90% of budget
- Auto-shutdown dev at night
- Cost in PR review

## Metrics

- $/customer
- $/transaction
- $/region
- Waste %

## Per Team

Showback or chargeback:
- Showback: per-team report
- Chargeback: per-team budget

(See L26/C02/T02.)

## Anomaly Detection

ML-based:
- Sudden cost spike
- Alert FinOps + team

Tools:
- AWS Cost Anomaly Detection
- Native cloud
- 3rd party

## Forecasting

- Trend extrapolation
- Seasonal
- ML-based

For: budget planning.

## Best Practices

- Continuous (not one-time)
- Cross-functional
- Embedded in process
- Measure outcomes

## Common Mistakes

- Stuck in Inform
- Optimize but no Operate
- No follow-up

## Quick Refs

```
Inform: visibility
Optimize: action
Operate: embedded

Loop: continuous
```

## Interview Prep

**Mid**: "FinOps phases."

**Senior**: "Implement."

**Staff**: "Org-wide FinOps."

## Next Topic

→ Move to [L26/C02 — Cost Visibility](../C02/README.md)
