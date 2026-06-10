# L19/C06/T03 — Headroom Management

## Learning Objectives

- Manage headroom continuously
- Avoid capacity surprises

## Headroom

Difference between current load and capacity:
```
Headroom = (Capacity - Current Load) / Capacity
```

For:
- 1000 capacity, 700 load → 30% headroom
- 1000 capacity, 950 load → 5% headroom (alert!)

## Target

- 30-50% typical
- 20% minimum
- 50%+ for surge-prone

## Why

- Handle spikes
- Failover (if one zone drops)
- Maintenance
- Growth between scaling events

## Tracking

```promql
1 - (sum(rate(http_requests_total[5m])) / capacity_max)
```

Per-service.

## Multi-Dimensional

Per resource:
- CPU
- Memory
- DB connections
- IO bandwidth

Each separately.

## Alert

```yaml
- alert: LowHeadroom
  expr: headroom_pct < 0.20
  for: 30m
  labels: { severity: warning }
```

For: 30-day notice before saturation.

## Failover Reserve

If zone failover causes 50% loss:
- Need 50% extra in surviving zones
- Headroom 50%+ at zone level

For: HA.

## Capacity Per Zone

```
3 zones × 33% load (with 50% headroom each)
1 zone fails → 2 zones × 50% load
```

For: handle.

## Auto-Scale + Headroom

Auto-scale handles dynamic:
- Headroom set by max replicas
- Headroom triggered by metric

For: still need max set.

## Scaling Cliffs

- Approach max replicas
- Latency rises
- Customers affected

For: alert before hit max.

## Pre-Scaling

Before peak:
- Scale up
- Faster than auto-scale

For: campaigns, launches.

## Capacity Roadmap

Quarterly:
- Forecast 3 months
- Plan provisioning
- Pre-buy commits

For: ahead.

## Bottleneck Shifts

After fix CPU bottleneck:
- DB connections new limit

Re-test; new bottleneck.

For: continuous.

## Resource Budgets

Per team:
- Allocated vCPU, RAM
- Track usage
- Notify if approaching

For: governance.

## Cost vs Headroom

More headroom = more cost.

Balance:
- Critical: 50%
- Important: 30%
- Internal: 20%

## Capacity Communication

- Capacity team → service teams
- Plans visible
- Quarterly reviews

For: aligned.

## Tools

- Cloud cost (Vantage, CloudHealth)
- Custom dashboards (Grafana)
- Internal capacity tracker

## Quick Win Examples

### CPU
Auto-scale; min replicas 3; max 30.
Headroom maintained 30%.

### DB Connections
Pool 100; alert at 80; max-conns 200.

### Disk
Auto-grow if > 80%.

## Tipping Points

Identify:
- 95% CPU: latency rises
- 90% memory: GC pressure
- 80% connections: queueing

Set alerts before these.

## Real Examples

### Black Friday
- Pre-scale 3× normal
- Monitor headroom
- Add reserve

### Service Launch
- Forecast
- Provision 2× forecast (uncertain)
- Monitor; adjust

### Region Failover
- Survivor regions: 2× capacity ready

## Capacity Tests

Periodic:
- Load test
- Verify headroom assumption
- Update model

For: real numbers.

## Best Practices

- Track per resource
- Alerts before saturation
- Quarterly roadmap
- Multi-zone reserve
- Auto-scale + max
- Communicate

## Common Mistakes

- One metric (CPU only)
- No alert (surprise saturation)
- Max replicas too low (cliff)
- No failover reserve
- Skip re-test

## Quick Refs

```
Headroom = (Capacity - Load) / Capacity
Target:   30-50%
Alert:    < 20%
Failover: 50%+ at zone level
Multi-dim: CPU, RAM, conn, IO
```

## Interview Prep

**Mid**: "What's headroom."

**Senior**: "Headroom strategy."

**Staff**: "Capacity at scale."

## Next Topic

→ Move to [L19/C07 — Chaos Engineering](../C07/README.md)
