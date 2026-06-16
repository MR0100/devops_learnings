# L26/C07/T02 — Forecasting & Budgets

## Learning Objectives

- Forecast cloud spend
- Set budgets

## Forecast

Predict future cost:
- Trend
- Seasonality
- Planned growth

For: budgeting.

## Methods

### Trend
Linear regression on history.

### Seasonal
For seasonal businesses.

### Per-Project
New launches added.

### ML
AWS, Datadog Forecasting.

## AWS Budgets

```bash
aws budgets create-budget --budget ...
```

Alert at:
- 50% spend
- 80%
- 100%
- 120%

For: thresholds.

## Forecast in Budgets

Budgets can forecast.

If trending over: alert.

## Per Team / Project

Set budgets:
- Per cost-allocation tag
- Alert team

For: distributed accountability.

## Quarterly Process

- Forecast
- Set budget
- Monitor
- Adjust

## Cost Drivers

Identify what drives:
- Customer count
- Transaction volume
- Data growth

For: model.

## Show Math

$/customer:
```
Total cloud cost / active customers = $/customer
```

Track over time:
- Decreasing: scale economies
- Increasing: investigate

## Cap Spend

For dev / staging:
- Hard caps
- Auto-shutdown if exceeded

For: prevent runaway.

## Pre-Approval

Spend > $X requires approval.

For: governance.

## Best Practices

- Monthly forecasting
- Per-team budgets
- Alert thresholds
- Track key ratios
- Quarterly adjust

## Common Mistakes

- One global budget
- No alerts
- Forecast = last month (naive)
- No follow-up

## Quick Refs

```bash
aws budgets create-budget --budget '...' --notifications-with-subscribers '...'
```

```python
# Forecast (simple linear)
forecast_month = trend * (now + 30 days)
```

## Interview Prep

**Mid**: "Cost forecasting."

**Senior**: "Budgets."

**Staff**: "FinOps maturity."

## Next Topic

→ [T03 — Engineering Incentives](T03-Engineering-Incentives.md)
