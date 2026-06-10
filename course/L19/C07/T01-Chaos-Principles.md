# L19/C07/T01 — Chaos Engineering Principles

## Learning Objectives

- Apply chaos
- Build resilience

## Chaos Engineering

Deliberately break things to find weaknesses.

Origin: Netflix Chaos Monkey (2010).

## Why

- Production has hidden failures
- Tests find issues before customers
- Build resilience
- Confidence in recovery

## Principles (from Principles of Chaos)

1. Hypothesis: steady state
2. Vary real-world events
3. Run in production
4. Automate continuously
5. Minimize blast radius

## Steady State

What's normal?
- Throughput
- Error rate
- Latency

Define before testing.

## Hypothesis

"System tolerates 1 zone down without SLO violation."

Test it.

## Real Events

- Pod kill
- Network latency
- DB slow
- CPU spike
- Memory leak
- Region down

For: realistic.

## Production

Yes; in prod:
- Real conditions
- Real systems
- Real data

But: scoped, observed.

## Automate

- Scheduled chaos
- Game days
- Random injection

For: continuous.

## Blast Radius

Limit:
- One pod
- One zone
- One region

Recover quickly.

For: safety.

## Workflow

```
1. Define steady state
2. Hypothesis: X holds during failure Y
3. Inject Y
4. Observe (steady state held?)
5. If not: learn + fix
6. Repeat
```

## Chaos vs Testing

- Test: known scenarios
- Chaos: unknown unknowns

For: emergent issues.

## Examples

### Pod Kill
"App survives random pod kill."

Inject: kubectl delete pod.

Observe: did SLO hold?

### Region Failover
"App works if region us-east-1 down."

Inject: block traffic.

Observe: traffic to other regions; SLO held.

### DB Slow
"App degrades gracefully if DB latency spikes."

Inject: add latency to DB calls.

Observe: timeouts, cache fallback.

### Network Partition
"Inter-zone partition handled."

Inject: drop packets between zones.

Observe: behavior.

## Tools

- Chaos Mesh
- Litmus
- Gremlin (commercial)
- AWS Fault Injection Simulator (FIS)
- Pumba (Docker)
- Chaos Monkey (Spinnaker)

(See T02.)

## Maturity Levels

### L1
Ad-hoc; manual.

### L2
Scheduled chaos in lower env.

### L3
Production chaos; limited.

### L4
Continuous; many failure types.

### L5
Org-wide; all teams; auto.

## Game Days

Scheduled chaos exercises:
- Team + chaos team
- Inject failure
- Respond
- Postmortem

(See T03.)

## Pre-Chaos Checklist

- Monitoring solid
- Alerts configured
- Runbooks ready
- Rollback works
- Team trained

If not: don't chaos yet.

## Observation

During chaos:
- All metrics watched
- Customer impact monitored
- Stop if too bad

For: don't break customers.

## Stop Conditions

- Error rate > X%
- Customer complaints
- Cascading failure

Pre-defined; auto-stop.

## Communication

Before:
- Internal: announce
- Customer: usually not (transparent)

After:
- Postmortem
- Action items

## Anti-Patterns

### Test Without Monitoring
Don't know what happened.

### Too Big Blast
Real outage.

### No Hypothesis
"Just break stuff."

### Skip Postmortem
Don't learn.

## Cultural

Chaos requires:
- Psychological safety (failures expected)
- Leadership backing
- Pre-prep

For: org buy-in.

## Real Use

- Netflix: invented; uses heavily
- AWS: FIS service
- Google: DiRT (Disaster Recovery Testing)
- Many

## Best Practices

- Start small (one pod)
- Define steady state
- Hypothesis-driven
- Observe + abort
- Iterate
- Game days

## Common Mistakes

- Skip observability (no signal)
- Too big (real outage)
- No hypothesis
- No follow-up

## Quick Refs

```
1. Steady state
2. Hypothesis
3. Inject
4. Observe
5. Learn
6. Repeat

Blast radius: minimal
Production: yes (carefully)
Tools: Chaos Mesh, Litmus, FIS
```

## Interview Prep

**Mid**: "What's chaos engineering."

**Senior**: "Chaos in prod."

**Staff**: "Chaos org maturity."

## Next Topic

→ [T02 — Tools (Chaos Mesh, Litmus, Gremlin, AWS FIS)](T02-Chaos-Tools.md)
