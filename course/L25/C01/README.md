# L25/C01 — Chaos Engineering Principles

## Topics

- **T01 Hypothesis-Driven Experiments** — Scientific method
- **T02 Steady State, Blast Radius** — Bound risk
- **T03 Maturity Levels** — Crawl/walk/run

## Principles (from principlesofchaos.org)

1. Build a hypothesis around steady-state behavior
2. Vary real-world events
3. Run experiments in production
4. Automate experiments to run continuously
5. Minimize blast radius

## Hypothesis-Driven Experiment

```
Hypothesis: "If the primary DB fails, replica failover completes within 60s
            with < 1% request error rate."

Steady State: 0.05% error rate; p99 latency 80ms.

Method:
1. Verify steady state.
2. Inject DB failure (via FIS).
3. Observe for 5 min.
4. Resolve injection.

Abort Criteria: error rate > 5% sustained, OR customer-impacting alert
                fires that team can't dismiss within 10s.

Expected: 60s of degradation; recovery to baseline within 90s.

Actual: __________

Actions: __________
```

## Steady State

What does "healthy" look like? Define quantitatively:
- Error rate
- Latency p50/p95/p99
- Throughput
- Business metrics (orders/min, signups/hour)

Without baseline, you can't tell what "abnormal" is.

## Blast Radius

Limit impact of experiment:
- Sandbox (dev / staging) — minimum blast
- Single AZ
- Single service
- Single canary cohort
- Small % of traffic
- Off-peak hours

Increase blast radius as confidence grows.

## Maturity Levels

```
L1: Manual experiments in staging
L2: Manual experiments in production (off-peak)
L3: Scheduled experiments in production
L4: Continuous random chaos in production
```

Netflix: L4 (Chaos Monkey kills instances 24/7).
Most enterprises: L2-L3.

## Game Days

Coordinated chaos exercises:
- Quarterly for high-priority services
- Senior team participates
- Simulate realistic failures
- Post-game debrief + AIs

## What to Inject

### Infrastructure
- Pod / VM termination
- AZ failure
- Network latency / loss
- CPU / memory exhaustion
- Disk I/O saturation
- Clock skew

### Dependencies
- DB slow
- Cache unavailable
- Downstream API errors / timeouts
- DNS failures

### Configuration
- Bad config deploy
- Cert expiry
- Rate limit hit
- IAM policy change

## When NOT to Chaos

- During known peak (Black Friday)
- Without informed on-call
- Without abort capability
- When customer harm is highly likely

## Tools (Brief)

- **Chaos Mesh** (K8s, CRD-driven)
- **Litmus** (K8s)
- **Gremlin** (commercial, multi-platform)
- **AWS FIS** (AWS-native)
- **Toxiproxy** (network failures)

Covered in next chapter.

## Cultural Prerequisites

Chaos engineering requires:
- Trusting operators (no blame for triggering issue)
- Time to invest in reliability work
- Strong observability (otherwise experiments are blind)
- Leadership buy-in

Without these: chaos is theater.

## Outcomes

- Validated assumptions about resilience
- Found bugs before customers
- On-call practice
- Confidence to ship faster

## Interview Themes

- "Chaos principles"
- "Steady state — define"
- "Blast radius — limit"
- "Maturity model"
- "When NOT chaos"
