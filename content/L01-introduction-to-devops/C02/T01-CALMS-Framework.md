# L01/C02/T01 — The CALMS Framework

## Learning Objectives

- Define each CALMS dimension and the failure mode it guards against
- Use CALMS as a structured audit tool to score an organization's DevOps maturity
- Recognize the concrete organizational signals of weakness in each dimension
- Sequence an improvement roadmap from an imbalanced CALMS profile

## What CALMS Is

A mnemonic for the five dimensions any DevOps adoption must address. The original four (CAMS) came from **Damon Edwards** and **John Willis** after the 2010 DevOpsDays discussions; **Jez Humble** added **Lean** to make it CALMS. It is deliberately not a maturity *model* with certified levels — it's a lens for asking "where is this organization actually weak?"

**C**ulture · **A**utomation · **L**ean · **M**easurement · **S**haring

The framing matters: CALMS leads with Culture and ends with Sharing because the two human dimensions bookend the technical ones. Most failed adoptions are technically literate and culturally illiterate — they buy the A and chase the M while the C and S rot.

## The Five Dimensions

### Culture

The foundation; every other dimension degrades without it.

- Shared responsibility for outcomes, not handoffs of blame
- Blameless learning from failure (see T04)
- Curiosity across functional lines — devs care about ops pain and vice versa
- Trust that lets people deploy on a Friday
- **Signal of weakness**: "That's not my team's problem"; a change-approval board that exists to assign blame; deploys frozen before holidays "to be safe"

### Automation

The force multiplier that makes the other dimensions repeatable.

- Eliminate manual handoffs and snowflake servers
- Reproducible builds, immutable deploys, Infrastructure as Code
- Self-service for the common path (provision, deploy, roll back)
- **Signal of weakness**: deploy steps live in a runbook PDF; "ask Dave, he knows how prod works"; a release requires a 40-step wiki page executed by hand

### Lean

Borrowed directly from the Toyota Production System and Lean software (Poppendieck).

- Small batch sizes — ship the smallest shippable increment
- Value-stream thinking — ask *where is the delay?*, not *who is slow?*
- Limit work in progress (WIP); finish before you start
- Eliminate waste: waiting, rework, handoffs, partially-done work
- **Signal of weakness**: 3-month release trains; 200-file pull requests; tickets sitting "in QA" for weeks

### Measurement

Instrumentation that informs decisions rather than scoring people.

- Both technical (DORA: deploy frequency, lead time, CFR, MTTR) and human (SPACE)
- Metrics drive conversations, not performance reviews
- Make the value stream observable end-to-end, not per-silo
- **Signal of weakness**: vanity metrics ("lines of code", "story points completed"); dashboards no one looks at; metrics weaponized in stack-ranking

### Sharing

The dimension that turns one team's learning into the whole org's capability.

- Knowledge, tooling, and code flow across team boundaries
- Inner-source: internal repos other teams can read, fork, and contribute to
- Shared postmortems, internal tech talks, cross-team rotations
- **Signal of weakness**: tribal knowledge silos; "the auth service is a black box"; every team reinventing the same Terraform module

## Using CALMS as a Maturity Audit

For each dimension, score 1–5 against evidence, not vibes:

| Score | Meaning | Example evidence |
|---|---|---|
| 1 | Hostile | Blame culture; manual everything; explicitly rejects the idea |
| 2 | Aware but not investing | Leadership talks about it; no budget or behavior change |
| 3 | Inconsistent | Some teams do it well, most don't; no shared standard |
| 4 | Consistent, room to deepen | The default for new work; legacy gaps remain |
| 5 | Cultural default | Invisible because it's just "how we work" |

Plot the five scores as a radar chart. The *shape* matters more than the total — a spiky profile reveals exactly where the next investment belongs.

```
            Culture
              5
              |
  Sharing 4---+---2 Automation
           \  |  /
            \ | /
       3 ----+---- 4
     Lean         Measurement

  Profile: C5 A2 L3 M4 S4
  → Automation is the bottleneck dragging
    a strong culture down.
```

## Common Imbalances

- **Strong A, weak C** — *automation theater*: the tools exist, but behavior never changed; engineers still throw work over the wall, now via a pipeline
- **Strong M, weak C** — *metric obsession*: teams game numbers (deploy frequency goes up by splitting one deploy into ten no-op deploys)
- **Strong C, weak A** — *believer culture*: great empathy and intentions, but execution is painful and slow because everything is manual
- **Strong A & M, weak L & S** — *local optima*: each team is fast and measured, but the end-to-end value stream is slow and no one shares improvements
- **Strong everything, weak L** — large batches quietly cap your throughput no matter how good the tooling is

## Sequencing the Roadmap

From an imbalanced profile, fix the *lowest leverage point first*, which is usually Culture or the weakest human dimension — automation built on a blame culture just makes blame faster. A typical sequence for a `C2 A4 L2 M4 S2` org: invest in blameless practice and psychological safety (C), then value-stream-map to attack batch size (L), then stand up inner-source to spread the wins (S). Resist the temptation to deepen the already-strong dimensions.

## Common Mistakes

- **Treating CALMS as a checklist** — scoring 5/5 on a self-assessment while the value stream is still 6 weeks long
- **Auditing tools instead of behavior** — "we have Jenkins, so Automation is a 5" ignores whether deploys are actually self-service
- **Skipping Culture because it's hard to measure** — it's the dimension most predictive of the rest
- **Letting Measurement become surveillance** — the fastest way to destroy the Culture score
- **Optimizing the strongest dimension** — deepening A from 4 to 5 while C sits at 2 yields nothing

## Best Practices

- **Score with evidence and multiple voices** — survey ICs, not just leadership; the gap between the two scores is itself a finding
- **Re-audit quarterly** — CALMS is a trend line, not a snapshot
- **Pair every weak dimension with one concrete experiment** — e.g., weak Sharing → launch one inner-source repo with a real first consumer
- **Use DORA + SPACE together for the M dimension** — technical throughput plus human sustainability
- **Make the radar chart visible** — shared situational awareness is itself a Culture and Sharing win

## Quick Refs

```
C — Culture       : shared ownership, blameless learning, trust
A — Automation    : IaC, reproducible builds, self-service, no manual handoffs
L — Lean          : small batches, value-stream thinking, limit WIP
M — Measurement   : DORA + SPACE, metrics inform (never blame)
S — Sharing       : inner-source, shared postmortems, rotations

Audit: score each 1–5 → radar chart → fix the spike, not the total.
Mnemonic: "Calms the chaos" — Culture first, Sharing last.
```

## Interview Prep

**Junior**: "What does CALMS stand for?"
- Culture, Automation, Lean, Measurement, Sharing — a mnemonic for the five dimensions a DevOps adoption has to address, originally CAMS plus Lean.

**Mid**: "Why is Culture listed first?"
- Because the other four degrade without it — automation on a blame culture just makes blame faster, and metrics on a blame culture get gamed; Culture is the dimension most predictive of overall success.

**Senior**: "Your team scores 4-4-2-4-2 on CALMS. What do you prioritize?"
- Lean and Sharing are the weak spots — likely big batches and isolated teams — so I'd run a value-stream mapping exercise to attack batch size and stand up one inner-source initiative with a real consumer, rather than deepening the already-strong A and M.

**Staff**: "You're hired into a 500-engineer org with great automation but a blame culture. Where do you start?"
- I'd treat the strong A as a trap (automation theater) and start on Culture: introduce genuinely blameless postmortems, separate metrics from performance reviews to rebuild trust, and pilot it in one influential team before scaling — because nothing else moves while the C score stays low.

## Next Topic

→ [T02 — The Three Ways](T02-Three-Ways.md)
