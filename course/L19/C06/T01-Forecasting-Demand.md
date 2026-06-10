# L19/C06/T01 — Forecasting Demand

## Learning Objectives

- Forecast capacity needs
- Plan ahead

## Why Forecast

- Avoid outages from saturation
- Pre-buy commits (cheaper)
- Plan launches
- Budget

## Inputs

- Historical traffic
- Business growth plan
- Marketing campaigns
- New features
- Seasonality

## Methods

### Linear Regression
```python
y = m*t + b
```

For: steady growth.

### Trend + Seasonal
```python
y = trend + seasonal(t) + noise
```

For: cyclical patterns.

### Prophet (Facebook)
Auto-detects:
- Trend
- Seasonality
- Holidays

### ML
For complex patterns.

## Seasonal Patterns

- Daily (peak hours)
- Weekly (weekends)
- Monthly (paydays?)
- Yearly (holidays)
- Black Friday
- Tax season

## Capacity Buffer

```
Forecast peak + buffer = Capacity
```

Buffer:
- 20-50% typical
- Higher for unpredictable

For: handle surge.

## Examples

### Web Traffic
- Forecast: 100k peak QPS in 6 months
- Provision: 150k QPS
- Headroom: 50%

### Storage
- Forecast: 100 TB in 1 year
- Provision: 150 TB
- Or auto-scale

### Compute
- Forecast: 1000 vCPU peak
- Provision: 1500 vCPU
- Or autoscale

## Auto-Scale

For dynamic:
- HPA / Cluster Autoscaler
- Karpenter

Forecasting still useful:
- Set max replicas
- Pre-warm for spikes

## Pre-Warming

Before known event:
- Black Friday
- Product launch
- TV ad

Scale up ahead.

## Pre-Buy Commits

For known sustained growth:
- 1y / 3y commits
- 30-70% discount

Forecast informs commit size.

## Resource Forecasting

Per:
- vCPU
- RAM
- Disk
- Network
- DB IOPS
- Connections

## Bottleneck Identification

Forecast all resources.
Identify smallest headroom.

For: focus.

## Saturation Curves

```
Latency
   ↑
   |          ___
   |        /
   |       /
   |  ___ /
   |____|
   →
       Throughput

Beyond knee: latency spikes
```

For: provision below knee.

## SLO + Capacity

Required capacity = traffic × slow margin.

For 99.9% SLO with 1% errors at saturation: provision for low utilization.

## Cost Trade-Offs

- Over-provision: waste
- Under-provision: outage

For: balance.

## Tools

- Prometheus + ML
- Datadog Forecast
- Cloud Cost tools (Vantage, etc.)
- Custom

## Bytes Sent

For network forecasting:
- CDN
- Egress costs (huge)

For: budget impact.

## Capacity Modes

### Static
Pre-provision.

### Reactive
Auto-scale on demand.

### Predictive
Forecast-driven autoscale.

For: mix.

## Predictive Autoscale

```yaml
# K8s VPA + custom predictor
```

ML predicts demand; provisions ahead.

## Cloud Provider Tools

- AWS Auto Scaling (predictive)
- GCP recommendations
- Azure scaling advisor

For: built-in.

## Real Examples

### Netflix
Forecast viewing peaks.

### Amazon Retail
Forecast Black Friday.

### Snapchat
Forecast user activity.

## When Forecasting Insufficient

- Unprecedented event (viral)
- Auto-scale must handle

For: combine forecast + autoscale.

## Communication

Capacity team to:
- Product (plans)
- Marketing (campaigns)
- Engineering (launches)

For: aligned.

## Best Practices

- Track + forecast
- Buffer
- Re-forecast quarterly
- Multi-resource
- Tooling

## Common Mistakes

- Forecast 1 dimension
- No buffer (cliff edge)
- Linear assumed (real: non-linear)
- No re-forecast
- Surprise launches

## Quick Refs

```
Forecast = trend + seasonal + buffer
Resources: CPU, RAM, disk, net, DB
Methods: regression, Prophet, ML
Buffer: 20-50%
```

## Interview Prep

**Mid**: "Capacity forecasting."

**Senior**: "Forecasting methods."

**Staff**: "Capacity strategy."

## Next Topic

→ [T02 — Load Testing in Anger](T02-Load-Testing.md)
