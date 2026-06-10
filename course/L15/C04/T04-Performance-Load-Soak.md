# L15/C04/T04 — Performance, Load, Soak Tests

## Learning Objectives

- Define test types
- Use k6 / similar

## Types

### Performance
Measure: response time, throughput.

### Load
At expected peak; verify SLAs.

### Stress
Beyond peak; find breaking point.

### Spike
Sudden load increase.

### Soak (Endurance)
Sustained over hours; find leaks.

### Capacity Planning
What can system handle?

## When

- Pre-launch
- After major changes
- Quarterly
- On suspicion

## k6

Modern load testing:
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 },   // ramp up
    { duration: '5m', target: 100 },   // sustain
    { duration: '2m', target: 0 },     // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function() {
  const res = http.get('https://api.example.com/users/1');
  check(res, {
    'status is 200': (r) => r.status === 200,
    'duration < 500ms': (r) => r.timings.duration < 500,
  });
  sleep(1);
}
```

```bash
k6 run script.js
```

## k6 Outputs

- Stdout
- InfluxDB / Grafana
- Prometheus
- CloudWatch
- Datadog
- k6 Cloud

For: visualize.

## Distributed k6

```bash
k6 run --out cloud script.js   # k6 Cloud
```

Or k6 Operator (K8s):
```yaml
apiVersion: k6.io/v1alpha1
kind: TestRun
spec:
  parallelism: 10
  script: ...
```

For: real load (millions of RPS).

## JMeter

Java-based; older but powerful:
- GUI test creation
- Distributed
- Many protocols

For: legacy, complex.

## Gatling

Scala DSL:
```scala
val scn = scenario("Basic")
  .exec(http("get").get("/users/1").check(status.is(200)))

setUp(
  scn.inject(rampUsers(100).during(60))
).protocols(http.baseUrl("https://api.example.com"))
```

For: code-first.

## Locust

Python:
```python
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def get_users(self):
        self.client.get("/users/1")

    @task(3)  # 3x weight
    def get_products(self):
        self.client.get("/products/1")
```

For: Python-friendly.

## Wrk2

Lightweight, fast:
```bash
wrk -t12 -c400 -d30s --latency http://api.example.com/users/1
```

For: quick checks.

## Metrics

### RPS (Requests/sec)
Throughput.

### Latency
p50, p95, p99.

### Error Rate
% non-2xx.

### Concurrent Users
Active sessions.

### Resource Usage
CPU, memory, network of system under test.

## Load Test Stages

```
1. Smoke: 1 user; verify endpoint works
2. Load: expected peak; check SLA
3. Stress: 2x expected; find breaking point
4. Spike: 0→peak quickly; verify autoscale
5. Soak: peak for hours; find leaks
```

## SLA Thresholds

```javascript
thresholds: {
  http_req_duration: ['p(95)<500', 'p(99)<1000'],
  http_req_failed: ['rate<0.01'],   // < 1% errors
  http_reqs: ['rate>1000'],          // > 1000 RPS
}
```

Fail test if violated.

## In CI

```yaml
- name: Load test
  run: k6 run --out json=results.json load-test.js
- name: Check results
  run: |
    p95=$(jq '.metrics.http_req_duration.values."p(95)"' results.json)
    if (( $(echo "$p95 > 500" | bc -l) )); then
      echo "p95 too high: $p95"
      exit 1
    fi
```

## Schedule

- PR: smoke (1 user, 30 sec)
- Main: load (peak, 5 min)
- Nightly: soak (peak, hours)
- Weekly: stress, spike

For: layered.

## Soak Test

```javascript
options: {
  stages: [
    { duration: '5m', target: 1000 },
    { duration: '4h', target: 1000 },   // long
    { duration: '5m', target: 0 },
  ],
}
```

Find:
- Memory leaks
- Connection exhaustion
- Cache pollution
- DB connection leaks

## Stress Test

Push until failure:
```javascript
stages: [
  { duration: '5m', target: 100 },
  { duration: '5m', target: 500 },
  { duration: '5m', target: 1000 },
  { duration: '5m', target: 2000 },
  { duration: '5m', target: 5000 },  // break here?
],
```

Find capacity.

## Spike Test

```javascript
stages: [
  { duration: '1m', target: 10 },
  { duration: '10s', target: 10000 },   // spike!
  { duration: '5m', target: 10000 },
  { duration: '10s', target: 10 },
]
```

Test autoscaling, surge handling.

## Capacity Planning

From stress test:
- Max RPS: X
- Per-user RPS: 1
- Max concurrent users: X

For: capacity model.

## Profiling Under Load

Use APM:
- Datadog
- New Relic
- Dynatrace
- Honeycomb

Profile during load test.

For: find bottlenecks.

## Realistic Data

```javascript
const users = JSON.parse(open('./users.json'));

export default function() {
  const user = users[Math.floor(Math.random() * users.length)];
  http.get(`/users/${user.id}`);
}
```

For: real cardinality.

## Don't Test Production (Generally)

Risks:
- DDoS your own service
- Affect real users
- Cost

Test:
- Staging (production-like)
- Pre-prod
- Carefully in prod with rate limits + feature flag

## Continuous Performance Testing

```
Every deploy:
- Smoke load test
- Compare baseline
- Fail if regression > 5%
```

For: regression detection.

## Baseline

Run on stable version; save metrics.
Compare future runs.

Tools: k6 Cloud, custom.

## Cost

- Run on real infra (AWS test account)
- Or self-hosted runners
- Or SaaS (k6 Cloud, BlazeMeter)

For: budget.

## Best Practices

- Tests in CI
- Production-like target
- Realistic data
- Layered (smoke / load / stress / soak)
- Compare to baseline
- Profile during runs
- Tear down test infra

## Common Mistakes

- Test prod
- Unrealistic data (cache pollution)
- One run = decision (variance)
- Skip thresholds (no pass/fail)
- No baselines

## Quick Refs

```bash
# k6
k6 run script.js
k6 run --vus 100 --duration 5m script.js
k6 run --out cloud script.js

# JMeter
jmeter -n -t test.jmx -l results.csv

# wrk
wrk -t12 -c400 -d30s URL

# locust
locust -f locustfile.py --headless -u 1000 -r 100 -H URL
```

## Interview Prep

**Mid**: "Load test types."

**Senior**: "k6 in CI."

**Staff**: "Performance testing strategy."

## Next Topic

→ [T05 — Security Tests in CI](T05-Security-Tests.md)
