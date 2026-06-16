# FAANGM Interview Prep

Company-specific interview guidance for DevOps / SRE / Platform / Cloud roles. This is the strategic layer; the depth lives in [L29 — FAANGM Interview Mastery](content/L29-interview-mastery/README.md) and the graded **Interview Prep** section at the bottom of every topic file.

> The whole course is interview prep. This doc is the map: what each loop tests, what each company weights, and how to spend the last few weeks.

---

## The Universal Loop

Most DevOps/SRE loops at scale share the same five signals:

| Round | What it tests | Where to prepare |
|---|---|---|
| **Phone screen** | Linux/networking fundamentals, scripting, "debug this" | [L02](content/L02-linux-and-os-foundations/README.md), [L03](content/L03-networking/README.md), [L04](content/L04-bash-scripting/README.md), [L29/C01](content/L29-interview-mastery/C01/README.md) |
| **Coding** | DSA — yes, it's real for SRE/SWE-SRE | [L29/C02](content/L29-interview-mastery/C02/README.md), [L06](content/L06-programming-for-devops/README.md) |
| **System Design** | The round that decides your level | [L28](content/L28-system-design/README.md), [L29/C03](content/L29-interview-mastery/C03/README.md) |
| **Ops/Troubleshooting** | "The dashboard is red — go" | [L17](content/L17-observability/README.md), [L19](content/L19-sre/README.md), [L13](content/L13-kubernetes/README.md) |
| **Behavioral** | Scope, ownership, influence, conflict | [L29/C04](content/L29-interview-mastery/C04/README.md) |

---

## The Level Rubric

System design and behavioral rounds level you. The same problem gets a different grade by altitude:

| Level | System design expectation | Behavioral expectation |
|---|---|---|
| **L3 / Junior** | Build the happy path; name the components | Owns tasks; learns fast |
| **L4 / Mid** | Handle scale + the obvious failure modes | Owns features; unblocks self |
| **L5 / Senior** | Trade-offs, SLOs, blast radius, cost | Owns systems; drives projects |
| **L6 / Staff** | Multi-region, org impact, build-vs-buy, migration strategy | Owns ambiguity; influences without authority |

Every topic file's graded Interview Prep mirrors this — read the **Senior** and **Staff** answers for any topic you'll be probed on.

---

## System Design — The Decider

This is where most candidates under-level. The reusable structure (from [L29/C03](content/L29-interview-mastery/C03/README.md)):

```
1. Requirements   — functional + non-functional; pin numbers (QPS, data size, SLO)
2. Estimation     — back-of-envelope: traffic, storage, bandwidth
3. High-level     — boxes and arrows; the happy path
4. Deep dive      — the 1-2 hard parts the interviewer steers to
5. Bottlenecks    — what breaks first; how you'd know (observability)
6. Trade-offs     — what you chose NOT to do, and why
```

DevOps/SRE system-design favorites — all covered in [L28](content/L28-system-design/README.md):

- Design a CI/CD platform for 1000 engineers
- Design a multi-region active-active service (RTO/RPO) — see [L27](content/L27-disaster-recovery/README.md)
- Design a metrics/observability pipeline at 5M samples/sec — see [L17](content/L17-observability/README.md)
- Design a globally consistent config/feature-flag system
- Design an internal developer platform (paved road) — see [L28](content/L28-system-design/README.md) platform chapters
- Rate limiter, log aggregator, deployment system, secrets manager

Always anchor in **SLOs, blast radius, and cost** — that's the senior+ signal.

---

## Company-Specific Signals

Deep dives live in [L29/C05](content/L29-interview-mastery/C05/README.md). Summary:

### Amazon
- **Leadership Principles drive everything.** Every behavioral answer maps to an LP; the **Bar Raiser** is looking for evidence, not vibes.
- Heavy **operational excellence** focus: on-call, COE (correction of error) writing, "how do you handle the page."
- STAR stories with **metrics**. Ownership and Dive Deep are the LPs DevOps candidates most often miss.

### Google
- **SRE bar**: error budgets, toil reduction, the *SRE Book* vocabulary. Expect "non-abstract large system design."
- Coding is real and graded against SWE standards. Don't skip [L29/C02](content/L29-interview-mastery/C02/README.md).
- "Googleyness" + the leveling committee decide the offer, not the interviewers alone.

### Meta (Facebook)
- Fast, pragmatic, **move-fast** culture. Production engineering (PE) loop = systems + coding + architecture.
- Strong Linux/systems internals signal in the early rounds — [L02](content/L02-linux-and-os-foundations/README.md) pays off.

### Microsoft
- **Manager-driven hiring** (vs external bar raiser). Team fit matters; the hiring manager has real weight.
- Mixed loop: design + coding + behavioral. Generally calibrated, humane pace.

### Apple
- **Team-assembled loop** — varies a lot by org; match the specific team's language.
- Secrecy norms; deep specialization; ICT ladder. Expect domain depth over breadth.

### Netflix
- Senior-only culture; **freedom & responsibility**. Expect to justify high-judgment, autonomous decisions.
- Strong emphasis on operating real distributed systems and chaos/resilience — [L25](content/L25-chaos-engineering/README.md).

---

## Negotiation & Offer

Covered in [L29/C06](content/L29-interview-mastery/C06/README.md):

- Know the **comp components**: base, bonus, equity (RSU vesting schedule — note Amazon's back-loaded vest, even-vest at others).
- **Competing offers** are the strongest lever; create them honestly.
- Level matters more than starting comp — negotiate the level first.

---

## The 4-Week Crunch Plan

| Week | Focus | Lectures |
|---|---|---|
| 1 | Fundamentals + ops | [L02](content/L02-linux-and-os-foundations/README.md), [L03](content/L03-networking/README.md), [L13](content/L13-kubernetes/README.md), [L17](content/L17-observability/README.md), [L19](content/L19-sre/README.md) |
| 2 | System design daily | [L28](content/L28-system-design/README.md), [L29/C03](content/L29-interview-mastery/C03/README.md) |
| 3 | Coding + behavioral + company prep | [L29/C02](content/L29-interview-mastery/C02/README.md), [L29/C04](content/L29-interview-mastery/C04/README.md), [L29/C05](content/L29-interview-mastery/C05/README.md) |
| 4 | Mock interviews + portfolio | [L30](content/L30-capstone/README.md) |

---

## Common Reasons Strong Engineers Get Down-Leveled

- Solved the system-design problem but never stated **SLOs, blast radius, or cost** → reads as mid, not senior.
- Behavioral stories used "we" everywhere → no individual ownership signal.
- Great on tools, thin on **why** and **failure modes** → breadth without depth.
- Skipped coding prep assuming "SRE doesn't code" → it does at most FAANGM.
- No back-of-envelope numbers in design → looks like hand-waving.

---

## See Also

- [L29 — FAANGM Interview Mastery](content/L29-interview-mastery/README.md) — the full lecture
- [L28 — System Design for DevOps](content/L28-system-design/README.md) — the decider round
- [L30 — Capstone Projects & Portfolio](content/L30-capstone/README.md) — proof of skill
- [LEARNING_PATHS.md](LEARNING_PATHS.md) — Path 7 is the interview crunch
- [README.md](README.md) — Course overview
