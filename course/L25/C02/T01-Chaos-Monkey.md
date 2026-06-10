# L25/C02/T01 — Chaos Monkey (Netflix Origin)

## Learning Objectives

- Know Chaos Monkey
- Apply principles

## Chaos Monkey

Netflix; 2010:
- Random EC2 instance kills
- During business hours
- Forces resilience

For: invented modern chaos.

## How It Started

Migrating to AWS:
- Failures inevitable
- Build resilient
- Test by causing failures
- Force engineers to handle

## Simian Army

Family:
- Chaos Monkey: kill instance
- Latency Monkey: add latency
- Doctor Monkey: detect unhealthy
- Conformity Monkey: enforce standards
- Janitor Monkey: clean up unused
- Security Monkey: find vulns
- Chaos Gorilla: kill AZ
- Chaos Kong: kill region

## Modern

Chaos Monkey now Spinnaker integration:
```yaml
# config.yaml
chaos:
  groupings:
    - cluster: my-service
      frequency: 7d   # once per week
      probability: 0.5
```

## Principles Established

- Continuous (always running)
- Random
- Production
- Business hours (engineers awake)
- Limited blast (one instance)

## Successors

Modern tools:
- Chaos Mesh
- Litmus
- Gremlin
- AWS FIS

## When Chaos Monkey

For:
- AWS-based
- Want simple random kills
- Multi-cluster ASG

For new: usually newer tools.

## Legacy

Still used at Netflix.

For ideas: study; principles still apply.

## Quick Refs

```yaml
# Chaos Monkey 2.x (Spinnaker)
spinnaker:
  account: aws-account-1
chaos:
  groupings:
    - cluster: X
      frequency: 7d
```

## Interview Prep

**Mid**: "Chaos Monkey."

**Senior**: "Simian Army."

**Staff**: "Chaos origins + lessons."

## Next Topic

→ [T02 — Chaos Mesh](T02-Chaos-Mesh.md)
