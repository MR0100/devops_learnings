# L01/C02/T02 — The Three Ways

## Learning Objectives

- Explain Gene Kim's Three Ways model and the direction each Way moves in
- Map each Way to specific, concrete engineering practices and tools
- Use the model to diagnose where a delivery system is actually failing
- Sequence improvements, since each Way builds on the one before it

## The Model

The Three Ways come from *The Phoenix Project* and *The DevOps Handbook* (Gene Kim et al.). They are not three separate initiatives — they are three reinforcing flows of work, signal, and knowledge through the same delivery system.

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

The order is deliberate. You cannot have meaningful Feedback until work Flows (a 3-month release train gives you feedback once a quarter). You cannot have a Learning culture until Feedback is fast and blameless. Skipping ahead — running game days while your pipeline takes a week — is a common waste.

## First Way — Flow

> Maximize the flow of work from Dev to Ops to Customer.

The First Way optimizes the *whole* system's throughput, never a local department's. It draws directly from Lean: make work visible, shrink batches, and stop starting / start finishing.

Practices:
- Continuous integration (merge to trunk many times a day)
- Continuous delivery (every commit is releasable)
- Small batch sizes — the single highest-leverage Flow lever
- Limit work in progress (WIP) — Little's Law: `lead time = WIP / throughput`
- Visualize work (Kanban) and make queue depth visible
- Reduce handoffs; automate them where they're unavoidable

Anti-pattern: large batched releases; "we'll ship it all at the end of the quarter." Big batches inflate lead time, hide defects, and make every deploy high-risk.

## Second Way — Feedback

> Amplify fast and constant feedback right-to-left at all stages.

The Second Way makes problems visible *upstream*, where they're cheap to fix. Cost-of-defect rises roughly an order of magnitude per stage it escapes — a bug caught in CI is trivial; the same bug in production is an incident.

Practices:
- Production monitoring and alerting fed back to the developers who wrote the code
- Fast, reliable, deterministic test suites (flaky tests are anti-feedback)
- Customer telemetry available to engineers, not locked in a BI team
- SLOs and error budgets as a shared, quantified feedback signal
- "Andon cord" / stop-the-line: anyone can halt the pipeline on a quality signal
- Postmortems shared widely (see T04)

Anti-pattern: ops absorbs production pain silently; the people who could fix the root cause never see the signal, so the same defect ships again.

## Third Way — Continuous Experimentation & Learning

> Create a culture that fosters experimentation, risk-taking, and learning from failure.

The Third Way makes the system *anti-fragile* — it gets better by being stressed. It requires the psychological safety from T04 and feeds organizational learning back into Flow and Feedback.

Practices:
- Game days and chaos engineering (deliberately inject failure to learn)
- Dedicated improvement time (the Toyota "improvement kata"; 20% time / hack days)
- Blameless postmortems that produce real systemic action items
- Knowledge-sharing rituals — internal tech talks, learning hours, inner-source
- Deliberately injecting faults in production-like conditions to build resilience

Anti-pattern: punishing failure; "we tried that once and it didn't work" — which trains everyone to stop experimenting and stop reporting.

## Mapping to Practices

| Way | Direction | Tools / Practices |
|---|---|---|
| Flow | left → right | Jenkins/GHA, ArgoCD/Flux, trunk-based dev, feature flags, Kanban |
| Feedback | right → left | Prometheus, Grafana, OpenTelemetry, alerting, SLOs, error budgets |
| Continuous Learning | vertical | Postmortems, game days, chaos engineering, learning rituals, inner-source |

## Diagnosing With the Three Ways

The model is most useful as a diagnostic. Match the symptom to the failing Way:

| Symptom | Failing Way | First move |
|---|---|---|
| "Deploys are slow / batched / scary" | Flow | Shrink batch size, automate the pipeline, limit WIP |
| "The same incident keeps recurring" | Feedback | Close the loop: shared dashboards, on-call sharing, error-budget policy |
| "Postmortem action items never land" | Continuous Learning | Make improvement work first-class on the backlog; protect the time |
| "Tests are flaky so no one trusts them" | Feedback | Quarantine and fix flaky tests; treat the suite as a product |
| "One team improved but no one else benefited" | Continuous Learning | Inner-source the fix; run a brown-bag |

## Common Mistakes

- **Treating the Ways as independent projects** — they're sequential; Feedback is meaningless without Flow
- **Jumping to the Third Way for the culture optics** — chaos game days on a week-long pipeline are theater
- **Confusing local speed with Flow** — a fast dev team feeding a slow QA queue hasn't improved system flow
- **Building dashboards no one acts on** — that's monitoring, not Feedback; the loop has to close back to the author
- **Logging postmortem action items with no owner or deadline** — the Third Way dies in the backlog

## Best Practices

- **Fix Flow first** — it's the prerequisite and usually the cheapest high-leverage win (smaller batches)
- **Route production signal to the author** — page the team that wrote the code, surface customer telemetry to engineers
- **Make the test suite a deterministic, fast feedback machine** — treat flakiness as a Sev incident, not a nuisance
- **Protect improvement time** — schedule it like any other commitment, or the Third Way never happens
- **Use error budgets to connect all three Ways** — they quantify Feedback, gate Flow, and trigger Learning

## Quick Refs

```
Way 1 — Flow      (→) : CI/CD, small batches, limit WIP, visualize work
Way 2 — Feedback  (←) : monitoring→author, fast tests, SLOs, error budgets
Way 3 — Learning  (↕) : game days, chaos, blameless postmortems, sharing

Little's Law:  lead time = WIP / throughput   → cut WIP to cut lead time
Order matters: Flow → Feedback → Learning. Don't skip.
```

## Interview Prep

**Junior**: "Name the Three Ways."
- Flow (work moving left-to-right, Dev → Ops → Customer), Feedback (signal moving right-to-left so problems surface upstream), and Continuous Experimentation & Learning (the vertical learning loop).

**Mid**: "Why does the order of the Three Ways matter?"
- Each builds on the prior — Feedback is worthless if work only Flows quarterly, and a Learning culture needs fast, blameless Feedback to learn from — so you fix Flow first, then Feedback, then invest in Learning.

**Senior**: "Our deploy frequency is fine, but production incidents keep recurring because dev doesn't know what's broken. Which Way is failing?"
- The Second Way, Feedback — production signal isn't reaching the people who can fix the root cause; I'd close the loop with shared dashboards, put devs on the on-call rotation, and add an error-budget policy so reliability data drives behavior.

**Staff**: "Design a 90-day plan that addresses all three Ways for a 40-engineer team."
- Days 0–30: instrument the value stream and attack Flow (trunk-based dev, smaller batches, CD pipeline); days 30–60: build Feedback (route alerts to authoring teams, define SLOs and error budgets, fix the flaky suite); days 60–90: institutionalize Learning (blameless postmortems with owned action items, first game day, inner-source the wins) — sequenced so each Way stands on the previous one.

## Next Topic

→ [T03 — Breaking Down Silos](T03-Breaking-Down-Silos.md)
