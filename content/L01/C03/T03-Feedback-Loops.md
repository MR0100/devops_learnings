# L01/C03/T03 — Feedback Loops at Every Stage

## Learning Objectives

- Enumerate the feedback loops that span DevOps phases and the signal each carries
- Measure the latency of each loop and recognize the symptoms of a slow one
- Apply the principle that shorter loops mean faster learning and smaller corrections
- Design a system for tight loops using local parity, fast CI, and dev-accessible observability

## The Idea

Feedback loops are the operational equivalent of test-driven development: the faster the loop, the smaller the corrections needed. A control-systems analogy is exact — a thermostat that reads the room every second holds temperature within a degree; one that reads every hour oscillates wildly between freezing and roasting. Software delivery is a control loop, and **loop latency is the dominant variable** in how stable and how fast the system can be steered.

The Three Ways (from the Phoenix/DevOps Handbook lineage) name this directly: the **Second Way is the amplification of feedback loops** — making them faster, louder, and impossible to ignore. This topic operationalizes that principle into eight measurable loops.

## The 8 Critical Feedback Loops

| # | Loop | From → To | Signal | Target Latency |
|---|---|---|---|---|
| 1 | IDE → Engineer | Compiler / linter / typechecker | Syntax, types, style | < 1 sec |
| 2 | Local test → Engineer | Unit test results | Logic correctness | < 10 sec |
| 3 | CI build → Engineer | PR check status | Integration, lint, scan | < 10 min |
| 4 | Integration test → Engineer | End-to-end status | Cross-service behavior | < 30 min |
| 5 | Canary → Pipeline | Production canary signal | Real-traffic health | < 5 min |
| 6 | Production → On-call | Incident alert | User-impacting failure | < 1 min |
| 7 | User → Product | Customer signal | Value, satisfaction, adoption | < 1 day |
| 8 | Incident → Process | Postmortem to process change | Systemic improvement | < 1 week |

These nest like Russian dolls: loops 1–2 are the **inner loop** (per-keystroke, per-save), 3–4 are the **CI loop** (per-push), 5–6 are the **production loop** (per-deploy), and 7–8 are the **organizational loop** (per-release-cycle). An engineer runs loop 1 thousands of times a day and loop 8 a handful of times a quarter — so a one-minute regression in loop 1 costs far more aggregate time than a one-day regression in loop 8.

## Why Latency Compounds

If your build takes 30 minutes and your test takes 30 minutes, an engineer might attempt 5–6 cycles a day instead of 30. Productivity isn't linear in feedback latency — it's *exponential* below a threshold, because of context switching:

```
Loop latency vs. effective cycles/day (one engineer)

  < 10 sec   ████████████████████████  stays in flow, ~hundreds of cycles
  ~1 min     ███████████████           waits at desk, dozens of cycles
  ~10 min    ████████                  reads Slack, ~10–20 cycles
  ~30 min    ███                       context-switches to another task, ~5–6
  > 1 hour   █                          "I'll check it tomorrow", ~1–2
```

The cliff is around the **human attention-span threshold (~10 minutes)**: below it the engineer waits and stays in context; above it they switch tasks, and the cost is no longer the wait — it's the cost of *reloading the mental model* when they come back. This is why "make the build under 10 minutes" is a near-universal target, not an arbitrary number.

## Diagnosing Slow Loops

| Symptom | Slow Loop |
|---|---|
| Engineers debug by pushing to CI to see errors | Loop 1 or 2 (inner loop too slow or missing locally) |
| "It works on my machine" syndrome | Loop 3 or 4 (no environment parity) |
| Issues only found after merge, in real traffic | Loop 5 (no canary / no pre-prod signal) |
| Customers report bugs before alerts fire | Loop 6 (alerting gaps; you're monitoring causes, not symptoms) |
| Product ships features users don't want | Loop 7 (no customer signal reaching the team) |
| The same class of problem recurs across services | Loop 8 (postmortems produce no durable change) |

The diagnostic move: **find the loop where people have learned to wait or to route around the system.** When engineers push to CI just to see a type error, loop 1 is broken. When the same incident recurs quarterly, loop 8's action items never landed. The slowest *meaningful* loop is almost always where the biggest productivity win hides.

## A Loop That Doesn't Close Is Worse Than No Loop

A feedback loop only helps if the signal causes an action. Three ways loops silently break:

- **The signal fires but no one acts** — alerts that page into a muted channel; postmortem action items with no owner or deadline (loop 8's classic failure)
- **The signal is too noisy to read** — 200 alerts a night means the one real alert is lost (loop 6 drowned by false positives)
- **The signal never reaches the person who can act** — production observability gated behind an ops team, so the developer who wrote the bug can't see it fail (loop 5/6 with the wrong audience)

A loop you measure but never close is theater. The test of a real loop is: *the last time this signal fired, what changed?*

## Designing for Tight Loops

- **Local dev parity** — devcontainers, Tilt, Telepresence, mirrord so loop 2/4 runs against production-like dependencies, killing "works on my machine"
- **Fast CI** — caching, parallelism, incremental builds, test sharding to keep loop 3 under 10 minutes (see T01)
- **Pre-merge canary on shadow/mirror traffic** — get a loop-5 signal *before* the change is live for anyone
- **Production observability available to developers** — no ops gating; the person who can fix the bug can see it (loops 5–6)
- **Symptom-based SLO alerts** — so loop 6 fires on what users feel, with high signal-to-noise
- **Postmortem action items with owners and deadlines** — the only thing that makes loop 8 real; track them like any other backlog work

## Common Mistakes

- **Optimizing the wrong loop** — pouring effort into a fancy dashboard (loop 6) while the build takes 40 minutes (loop 3); fix the loop engineers hit thousands of times a day first
- **Measuring loops you never close** — tracking MTTR or alert volume while postmortem actions rot unowned, so the same incident recurs
- **Gating production signal behind ops** — developers can't see their own code fail, so loops 5–6 carry no learning back to the author
- **Letting loop 6 drown in noise** — so many false-positive alerts that the real one is missed, which is functionally the same as having no alerting
- **Ignoring loop 7 entirely** — shipping fast with tight technical loops but no customer signal, so the team builds the wrong thing efficiently
- **Treating a slow inner loop as normal** — accepting a 30-second unit-test cycle because "that's just how it is," when it's the single biggest drag on flow

## Best Practices

- **Rank loops by frequency × latency** — the inner loops (1–2) usually win on aggregate time even though each individual delay is tiny
- **Set explicit latency budgets** — under 10 min for CI, under 1 min for alerts; treat a regression past budget as a bug to fix
- **Achieve environment parity** — the cheapest fix for "works on my machine" is making local look like prod, not adding more e2e tests
- **Give developers production observability** — closing loops 5–6 requires the author to see the failure, not a relayed ticket
- **Make every postmortem produce an owned, dated action** — the difference between loop 8 existing and not
- **Measure the loops** — instrument cycle time per loop so "our feedback is slow" becomes a number you can attack

## Quick Refs

```bash
# Measure CI loop latency (loop 3) over recent runs — GitHub Actions
gh run list --limit 50 --json durationMS,conclusion \
  | jq '[.[] | select(.conclusion=="success") | .durationMS] | (add/length)/60000'

# Time the inner loop (loop 2) — how long do unit tests actually take?
time pytest tests/unit -q

# Find the slowest stage in a pipeline to know which loop to fix
gh run view <run-id> --log | grep -E "##\[group\]|Completed in"

# Time to detect (front of loop 6): compare alert-fire time to deploy time
# (in your monitoring tool) — TTD = alert_timestamp - incident_start
```

Mnemonic: **frequency × latency = total drag.** A 10-second delay on a loop you hit 200 times a day costs more than a 1-day delay on a loop you hit once a quarter.

## Interview Prep

**Junior**: "Why do feedback loops matter in DevOps?"
- The faster you learn that something is wrong, the smaller and cheaper the correction — a fast loop catches a bug in seconds at your desk, a slow one catches it days later in production, after you've forgotten the context.

**Mid**: "Name the feedback loops in a delivery pipeline and roughly how fast each should be."
- Inner loop (typecheck < 1s, unit tests < 10s), CI loop (PR checks < 10 min, integration < 30 min), production loop (canary signal < 5 min, alerts < 1 min), and the organizational loop (customer signal within a day, postmortem-to-change within a week).

**Senior**: "Our team complains they 'fight fires' instead of building. Walk me through which loops you'd investigate."
- I'd start at loop 8 (do postmortems produce owned, dated actions, or do the same incidents recur?) and loop 6 (are alerts symptom-based and high-signal, or is the team buried in noise?), then check whether developers even have production observability — chronic firefighting is almost always a loop-8 failure to make durable change plus a loop-6 noise problem.

**Staff**: "You're shipping a global platform; design a feedback architecture that respects 8 zones of latency."
- I'd budget each loop explicitly and engineer to it: devcontainers and parity for the inner loop, a sub-10-minute cached/incremental CI for loop 3, pre-merge canary on mirrored traffic for loop 5, symptom-based SLO alerting with regional routing for loop 6, product analytics feeding the backlog for loop 7, and a postmortem process with tracked action items for loop 8 — then instrument every loop's latency so regressions are visible and ownable.

## Next Topic

→ [T04 — The Infinity Loop Diagram (Deconstructed)](T04-Infinity-Loop-Deconstructed.md)
