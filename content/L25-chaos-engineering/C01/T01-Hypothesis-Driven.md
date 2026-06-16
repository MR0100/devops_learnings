# L25/C01/T01 — Hypothesis-Driven Experiments

## Learning Objectives

- Run chaos with hypothesis
- Learn from each

## Hypothesis

Before chaos:
- "System tolerates X without SLO violation"

Test: does it?

## Why Hypothesis

- Focus
- Measurable outcome
- Documented
- Learn

vs:
- "Let's break stuff"
- Unclear

## Components

### Statement
"App availability stays > 99.9% when one pod is killed every 30 sec for 10 min."

### Steady State
What's normal?
- p99 latency < 200ms
- Error rate < 0.1%
- Throughput 1000 RPS

### Variables
What we change:
- Kill pods

### Constants
Production-like.

### Outcomes
Did steady state hold?

## Process

1. Define steady state
2. Hypothesize
3. Vary real-world events
4. Run + observe
5. Stop if exceeds blast
6. Analyze
7. Improve

## Example

Hypothesis: "Order service stays available when DB has 100ms added latency for 5 min."

Steady state:
- Order p99 < 500ms
- Error rate < 0.1%

Inject: 100ms latency on DB.

Observe:
- p99 < 1s (degraded but OK)
- Error rate 0.05% (good)

Result: hypothesis confirmed.

OR:
- Errors spike
- Hypothesis falsified
- Action: improve resilience

## Document

Per experiment:
```markdown
## Experiment: DB Latency

### Hypothesis
...

### Steady State
...

### Method
...

### Result
... pass / fail ...

### Observations
- Slow query timeouts
- Retries spiked
- Cache hit unchanged

### Action Items
- Increase retry budget
- Adjust cache TTL
```

## Repeatable

Reproducible:
- Same experiment monthly
- Track changes over time
- Regression check

## Trust Building

Iterate:
- Small experiments
- Build muscle
- Trust in system

For: continuous.

## Best Practices

- Hypothesis before chaos
- Steady state defined
- Blast radius limited
- Observe carefully
- Stop conditions
- Postmortem each

## Common Mistakes

- "Break stuff" without plan
- No baseline
- Too big blast
- Skip postmortem

## Quick Refs

```
1. Steady state
2. Hypothesis
3. Vary
4. Observe
5. Stop if bad
6. Learn
```

## Interview Prep

**Mid**: "Chaos hypothesis."

**Senior**: "Hypothesis-driven."

**Staff**: "Chaos engineering rigor."

## Next Topic

→ [T02 — Steady State, Blast Radius](T02-Steady-Blast.md)
