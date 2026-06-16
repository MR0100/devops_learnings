# L25/C02/T01 — Chaos Monkey (Netflix Origin)

## Learning Objectives

- Explain what Chaos Monkey does and the historical problem it solved
- Map the Simian Army to the failure domains each tool exercises
- Decide when Chaos Monkey still fits versus a modern chaos platform

## Chaos Monkey

Chaos Monkey is the tool that started modern chaos engineering. Netflix built
it around 2010–2011 while migrating from its own data centers to AWS. The
insight: in the cloud, instances *will* disappear without warning, so the only
way to be sure the system tolerates that is to make it happen constantly, on
purpose, during the day when engineers are awake to watch.

What it actually does is narrow on purpose:

- Randomly terminates **one** EC2 instance within a cluster (an ASG)
- Runs on a schedule during **business hours**, not nights or weekends
- Forces every service to be built so a single instance dying is a non-event

The point was never the instance kill itself — it was the *forcing function*.
If a service can't survive losing one node, you find out on a Tuesday at 2pm
with the whole team available, not at 3am during a real AWS event.

## How It Started

The migration to AWS reframed reliability:

- Hardware/instance failure is **inevitable and frequent** at scale
- You can't prevent failure, so you must **design to absorb** it
- The only credible proof that you absorbed it is to **cause** the failure
- Doing it in business hours forces engineers to **own** the resilience

This is the seed of the whole discipline (steady state, blast radius,
continuous experiments) covered in L25/C01.

## Simian Army

Netflix grew Chaos Monkey into a family, each member targeting a different
failure domain or hygiene concern:

| Member            | Failure domain it exercises                      |
|-------------------|--------------------------------------------------|
| Chaos Monkey      | Single instance termination                      |
| Latency Monkey    | Network latency / degraded dependencies          |
| Doctor Monkey     | Detects and removes unhealthy instances          |
| Conformity Monkey | Enforces best-practice/config standards          |
| Janitor Monkey    | Cleans up unused, cost-leaking resources         |
| Security Monkey   | Flags security misconfigurations                 |
| Chaos Gorilla     | Takes out an entire **Availability Zone**        |
| Chaos Kong        | Takes out an entire **Region**                   |

Gorilla and Kong are the important escalation: the same philosophy applied at
AZ and region scale. Chaos Kong is what gave Netflix confidence in regional
evacuation — directly relevant to L27 (DR / multi-region).

## Modern Chaos Monkey (v2)

The current Chaos Monkey is decoupled from the rest of the Simian Army and
integrates with **Spinnaker** (Netflix's CD platform). It terminates instances
in Spinnaker-managed clusters on a configurable cadence and probability:

```yaml
# Chaos Monkey 2.x config — scoped to a Spinnaker cluster
chaos:
  enabled: true
  groupings:
    - cluster: my-service
      frequency: 7d        # eligible to kill at most once per week
      probability: 0.5     # 50% chance it actually kills in a window
      exceptions:          # never kill these
        - account: prod-payments
```

Two knobs do the safety work: `frequency` bounds how often a cluster is
*eligible*, and `probability` makes the kills non-deterministic so teams can't
pattern-match and quietly route around the experiment.

## Principles It Established

These five ideas became the foundation of the field:

- **Continuous** — chaos runs all the time, not as a one-off
- **Random** — you can't predict and pre-mitigate it
- **In production** — the only environment that proves real behavior
- **Business hours** — humans are awake to observe and learn
- **Limited blast radius** — one instance, never the whole fleet at once

## Successors

Chaos Monkey is intentionally narrow (random instance kills in an ASG). Modern
needs — Kubernetes faults, network/IO/clock chaos, managed safety rails,
multi-cloud — are met by:

- **Chaos Mesh** / **Litmus** — Kubernetes-native, broad fault catalog (CRDs)
- **Gremlin** — commercial, multi-platform, built-in safety
- **AWS FIS** — AWS-native infrastructure faults with CloudWatch stop conditions

## When Chaos Monkey Fits

Reach for Chaos Monkey specifically when:

- You run on **EC2 Auto Scaling Groups** and deploy through **Spinnaker**
- You want exactly one thing: continuous, random **instance termination**
- You want a low-ceremony forcing function to enforce statelessness

For anything broader — Kubernetes pod/network/IO faults, latency injection,
region drills, fine-grained targeting, or curated safety — start with a modern
platform instead. The *principles* Chaos Monkey established still apply; the
tool itself is now a niche choice.

## Legacy

Chaos Monkey is still used at Netflix and is the canonical "first chaos tool"
in interviews. Study it for the ideas, not as a default tool: every modern
chaos platform is a generalization of what Chaos Monkey proved was safe and
valuable to do continuously in production.

## Common Mistakes

- Treating Chaos Monkey as a *general* chaos tool — it only does instance kills
- Running it before the service is actually stateless → real outages, not learning
- Excluding so many clusters that it never runs anywhere meaningful
- Killing instances with no dashboards/alerting wired up → no signal to learn from
- Confusing the *tool* (narrow) with the *principles* (broad and still current)
- Skipping Gorilla/Kong-class drills and assuming single-instance resilience scales to AZ/region

## Best Practices

- Start in a non-prod ASG, confirm graceful instance loss, then enable in prod
- Run during business hours so engineers observe and own the outcome
- Scope with `frequency`/`probability`; never kill more than one instance at a time
- Wire steady-state dashboards before enabling — a kill with no observation teaches nothing
- Use `exceptions` for genuinely single-homed/stateful clusters until they're fixed
- Graduate to AZ/region drills (Gorilla/Kong-style) only after single-instance is boring

## Quick Refs

```yaml
# Chaos Monkey 2.x (Spinnaker-integrated)
chaos:
  enabled: true
  groupings:
    - cluster: X
      frequency: 7d       # eligibility cadence
      probability: 0.5    # non-deterministic kill
      exceptions: [...]   # opt-out clusters
# Simian Army scale-up: Chaos Gorilla (AZ) · Chaos Kong (region)
```

## Interview Prep

**Junior**: "What is Chaos Monkey?" — A Netflix tool that randomly terminates one instance in a cluster during business hours, forcing services to be resilient to losing a node. It started modern chaos engineering.

**Mid**: "Why business hours and only one instance?" — Business hours means engineers are awake to observe and learn instead of being paged at 3am; one instance keeps the blast radius small so the experiment is a controlled forcing function, not an outage.

**Senior**: "What is the Simian Army and why does it matter?" — A family of tools each targeting a failure domain: Latency Monkey (degraded deps), Janitor/Conformity/Security (hygiene), and crucially Chaos Gorilla (kills an AZ) and Chaos Kong (kills a region). Gorilla/Kong are how Netflix earned confidence in AZ and regional evacuation.

**Staff**: "Chaos Monkey's origins — what are the lasting lessons?" — Five principles outlive the tool: chaos should be continuous, random, run in production, during business hours, with a bounded blast radius. The tool itself is niche (EC2 ASG + Spinnaker, instance kills only); modern platforms generalize those principles to Kubernetes, network/IO/clock faults, and managed safety.

## Next Topic

→ [T02 — Chaos Mesh](T02-Chaos-Mesh-Detail.md)
