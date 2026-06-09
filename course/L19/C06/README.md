# L19/C06 — Capacity Planning

## Topics

- **T01 Forecasting Demand** — Predicting growth
- **T02 Load Testing in Anger** — Validating at scale
- **T03 Headroom Management** — Operational margin

## Why Capacity Planning

Cloud's "infinite scale" myth: it's not infinite or free. You need to know:
- Will we run out before our autoscale kicks in?
- Can we survive an AZ failure?
- What does Black Friday look like?
- Are we paying for headroom we don't need?

## Forecasting

### Sources of Data
- Historical trends (last 6-24 months)
- Product roadmap (new feature with X expected users)
- Marketing campaigns (predicted traffic)
- Seasonality (holiday peaks, business hours)
- Growth assumptions (10% MoM, 100% YoY)

### Methods
- **Linear regression** — simple growth lines
- **Time-series models** — Prophet, ARIMA
- **Custom queries** on telemetry warehouse

### Output
Per service, per region:
- Expected requests per second at peak (3-12 months out)
- Expected data size
- Expected cost
- Triggers for re-evaluation (campaign goes live, new product, etc.)

## Load Testing

### Goals
- Confirm system can handle projected peak
- Find break points (knee in curve)
- Measure cost per unit load
- Validate autoscaling triggers

### Test Types

**Load Test** — sustain projected peak for 30+ min.
**Stress Test** — push past peak; find where it breaks.
**Soak Test** — moderate load for hours/days; find memory leaks.
**Spike Test** — sudden burst; verify autoscaling.

### Tools
- **k6** (modern; JS scripts)
- **Locust** (Python)
- **Gatling** (Scala)
- **Vegeta** (Go; CLI-friendly)
- **JMeter** (mature; heavy)

### k6 Example
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  scenarios: {
    ramping: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '5m', target: 100 },
        { duration: '30m', target: 1000 },
        { duration: '5m', target: 0 },
      ],
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<500'],
  },
};

export default function () {
  const res = http.get('https://api.example.com/');
  check(res, { 'status 200': (r) => r.status === 200 });
  sleep(1);
}
```

## Production Load Testing

Best test = real prod traffic on a new stack. Strategies:

### Shadow Traffic
Mirror prod traffic to new stack; observe (don't return responses).

### Read-Only Replay
Replay prod traffic against staging that has prod-data-shaped DB.

### Gradual Rollout
Production is its own load test. Canary 1% → 100% reveals scale issues.

### Synthetic Probes
Continuous low-volume traffic to ensure system stays warm + alive.

## Headroom

Cushion between current usage and capacity:
- **Compute**: aim 30-50% headroom at steady state
- **DB connections**: 20-30% headroom
- **Storage**: 30% headroom (so growth doesn't surprise)
- **Queue depth**: should drain in seconds at peak

### Why Headroom Matters
- Failures + spikes consume slack
- Autoscaling takes time (seconds to minutes)
- AZ failure means surviving AZs absorb everything

### AZ Failure Math
3 AZs serving equal traffic = 1/3 of capacity per AZ.
If 1 AZ fails, remaining 2 absorb 50% more load each.
Pods must scale to 1.5× steady state.
At 50% baseline utilization, surviving AZs go to 75%. Manageable.
At 70% baseline, surviving AZs go to 105% — overload.

So: keep utilization ≤ 50-60% when multi-AZ.

## Autoscaling Doesn't Save You

### Cold Start Latency
- HPA reaction: ~30s
- Pod startup: 10s-2min (image pull, init)
- Node provisioning (cluster autoscaler): 1-3 min
- Karpenter: 30-60 sec

If your traffic doubles in 10 sec, autoscaler is too slow. Need pre-provisioned headroom OR predictive scaling.

### Predictive Scaling
- Pre-warm pods before known peak (cron-based scaling)
- KEDA for event-driven (queue depth, etc.)
- Schedule based: scale up 10 min before 9am peak

## Capacity Forecasts as a Process

Quarterly:
1. Pull last 90 days metrics per service
2. Project next 90 days
3. Identify services at risk of exceeding capacity
4. Engineering work to address (autoscale tuning, infra investment)
5. Cost projection

Annual:
- Multi-year capacity plan
- Investment decisions (multi-region, new architecture)

## Tools

- **Grafana** custom dashboards for capacity metrics
- **CloudWatch / Datadog** capacity alerts
- **VPA Reporter** for resource recommendations
- **Kubecost** for K8s-specific
- **AWS Compute Optimizer** for EC2/Lambda

## Interview Themes

- "Capacity plan for X workload"
- "AZ failure math"
- "Load testing — strategies"
- "Headroom — how much and why"
- "Autoscaling doesn't save you — explain"
