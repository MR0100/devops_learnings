# L01/C03/T03 — Feedback Loops at Every Stage

## Learning Objectives

- Enumerate the feedback loops that span DevOps phases
- Measure the latency of each loop
- Apply the principle: shorter loops = faster learning = better systems

## The Idea

Feedback loops are the operational equivalent of test-driven development. The faster the loop, the smaller the corrections needed.

## The 8 Critical Feedback Loops

| # | Loop | From → To | Target Latency |
|---|---|---|---|
| 1 | IDE → Engineer | Compiler / linter / typechecker errors | < 1 sec |
| 2 | Local test → Engineer | Unit test results | < 10 sec |
| 3 | CI build → Engineer | PR check status | < 10 min |
| 4 | Integration test → Engineer | End-to-end status | < 30 min |
| 5 | Canary → Pipeline | Production canary signal | < 5 min |
| 6 | Production → On-call | Incident alert | < 1 min |
| 7 | User → Product | Customer signal | < 1 day |
| 8 | Incident → Process | Postmortem to process change | < 1 week |

## Why Latency Compounds

If your build takes 30 minutes and your test takes 30 minutes, an engineer might attempt 5–6 cycles a day instead of 30. Productivity isn't linear in feedback latency — it's *exponential* below a threshold.

## Diagnosing Slow Loops

Symptoms:

| Symptom | Slow Loop |
|---|---|
| Engineers debug locally, push to find errors | Loop 1 or 2 |
| "It works on my machine" syndrome | Loop 3 or 4 |
| Issues only found in production | Loop 5 |
| Customers report bugs before alerts fire | Loop 6 |
| Same problem recurs across services | Loop 8 |

## Designing for Tight Loops

- Local dev parity (devcontainers, telepresence, mirrord)
- Fast CI (caching, parallelism, incremental builds)
- Pre-merge canary on shadow traffic
- Production observability available to devs (no ops gating)
- Postmortem action items with deadlines

## Interview Prep

**Mid**: "Why do feedback loops matter?"

**Senior**: "Our team complains they 'fight fires' instead of building. Walk me through what loops you'd investigate."

**Staff**: "You're shipping a global platform; design a feedback architecture that respects 8 zones of latency."

## Next Topic

→ [T04 — The Infinity Loop Diagram (Deconstructed)](T04-Infinity-Loop-Deconstructed.md)
