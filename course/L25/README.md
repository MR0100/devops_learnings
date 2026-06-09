# L25 — Chaos Engineering & Resilience Testing

## Overview

Break it before it breaks you. Chaos engineering is the discipline of proving system resilience through controlled experiments.

**5 chapters, 14 topics.**

## Chapter Map

### [C01](C01/) — Chaos Engineering Principles
- T01 Hypothesis-Driven Experiments
- T02 Steady State, Blast Radius
- T03 Maturity Levels

### [C02](C02/) — Tools
- T01 Chaos Monkey (Netflix Origin)
- T02 Chaos Mesh
- T03 Litmus
- T04 Gremlin
- T05 AWS Fault Injection Simulator (FIS)

### [C03](C03/) — Common Experiments
- T01 Network Latency & Loss
- T02 CPU / Memory Exhaustion
- T03 Disk I/O Saturation
- T04 Pod / Node Kills
- T05 Region Failover

### [C04](C04/) — Game Days
- T01 Planning a Game Day
- T02 Running the Exercise
- T03 Capturing Findings

### [C05](C05/) — Resilience Patterns
- T01 Circuit Breakers
- T02 Bulkheads
- T03 Retries with Backoff & Jitter
- T04 Timeouts (Done Right)
- T05 Idempotency Keys

## Principles of Chaos Engineering (Netflix)

1. Build a hypothesis around steady-state behavior
2. Vary real-world events
3. Run experiments in production
4. Automate experiments to run continuously
5. Minimize blast radius

## Experiment Template

```
Hypothesis: If service B's latency increases to 500ms, service A's p99 stays under 1s.

Steady state: A's p99 = 250ms; success rate = 99.95%

Method:
1. Pre-check steady state in baseline.
2. Inject 500ms latency on B for 5 min.
3. Observe A.
4. Stop injection.
5. Confirm steady state restored.

Abort criteria: A's success rate < 99% OR p99 > 3s.

Result: ___
Action items: ___
```

## Resilience Patterns

### Circuit Breaker
Three states: Closed (normal), Open (rejecting), Half-Open (testing).
- Trip after N failures in window
- Stay open for cooldown
- Half-open allows test traffic; failure → reopen, success → close

### Bulkhead
Isolate resources per-dependency. Thread pool per downstream so one slow dep doesn't drain all threads.

### Retry with Backoff + Jitter
```
delay = base * (2^attempt) + random(0, jitter)
```
Without jitter, retries from many clients synchronize and DOS the recovering service.

### Timeouts
- Set them. Always.
- Higher up the stack, longer the timeout (composition)
- Never default infinity

### Idempotency
- Idempotency key on every write
- Server deduplicates
- Makes retries safe

## Game Day Format

```
Pre: invite participants, brief on scenario, confirm rollback plan
Run: facilitator triggers issue; team responds as in production
During: capture timeline; let team work; abort if real harm risk
Post: debrief; capture findings; create action items
```

## Recommended Reading

- *Chaos Engineering* — Casey Rosenthal, Nora Jones (O'Reilly)
- *Release It!* — Michael Nygard (still the bible on stability patterns)
- principlesofchaos.org

## Interview Themes

- "What's chaos engineering?"
- "Design a chaos experiment for service X"
- "Circuit breaker — how does it work?"
- "Game day — how would you run one?"

## Next

→ [L26 — FinOps & Cloud Cost Optimization](../L26/README.md)
