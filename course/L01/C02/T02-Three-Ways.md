# L01/C02/T02 — The Three Ways

## Learning Objectives

- Explain Gene Kim's Three Ways model
- Map each Way to specific engineering practices
- Use the model to diagnose where a delivery system is failing

## The Model

```
   ┌─────────────────────────────────────────┐
   │   Way #3 — Continuous Experimentation   │  (vertical: learning)
   │            & Learning                   │
   └─────────────────────────────────────────┘
                  ▲           │
                  │           ▼
        Way #2: Feedback   Way #1: Flow
        right → left       left → right
        (signals upstream) (work downstream)
   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────────┐
   │ Dev  │ → │ CI   │ → │ Test │ → │ Prod     │
   └──────┘   └──────┘   └──────┘   └──────────┘
```

## First Way — Flow

> Maximize the flow of work from Dev to Ops to Customer.

Practices:
- Continuous integration
- Continuous delivery
- Small batch sizes
- Limit work in progress (WIP)
- Visualize work (Kanban)

Anti-pattern: large batched releases.

## Second Way — Feedback

> Amplify fast and constant feedback right-to-left at all stages.

Practices:
- Production monitoring fed back to dev
- Fast, reliable test suites
- Customer telemetry available to engineers
- Postmortems shared widely

Anti-pattern: ops absorbs production pain silently.

## Third Way — Continuous Experimentation & Learning

> Create a culture that fosters experimentation, risk-taking, and learning from failure.

Practices:
- Game days, chaos engineering
- 20% time / hack days
- Blameless postmortems
- Knowledge-sharing rituals (tech talks, learning hours)

Anti-pattern: punishing failure; "we tried that once and it didn't work."

## Mapping to Practices

| Way | Tools/Practices |
|---|---|
| Flow | Jenkins/GHA, ArgoCD, trunk-based dev, feature flags |
| Feedback | Prometheus, Grafana, alerting, SLOs, error budgets |
| Continuous Learning | Postmortems, game days, chaos engineering, learning rituals |

## Diagnosing With the Three Ways

If teams complain "deploys are slow" → Flow problem.
If incidents recur because the same code is shipped again → Feedback problem.
If postmortem action items never land → Continuous Learning problem.

## Interview Prep

**Mid**: "Name the Three Ways."

**Senior**: "Our deploy frequency is fine, but production incidents keep happening because dev doesn't know what's broken. Which Way is failing?"
- Second Way (Feedback). Propose closing the loop: shared dashboards, on-call sharing, error budget policy.

**Staff**: "Design a 90-day plan that addresses all three Ways for a 40-engineer team."

## Next Topic

→ [T03 — Breaking Down Silos](T03-Breaking-Down-Silos.md)
