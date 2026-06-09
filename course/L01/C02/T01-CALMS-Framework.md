# L01/C02/T01 — The CALMS Framework

## Learning Objectives

- Define each CALMS dimension
- Use CALMS as an audit tool for DevOps maturity
- Recognize organizational signals of weakness in each dimension

## What CALMS Is

A mnemonic from Jez Humble (~2010) for the five dimensions a DevOps adoption must address. Originally proposed by Damon Edwards and John Willis.

**C**ulture · **A**utomation · **L**ean · **M**easurement · **S**haring

## The Five Dimensions

### Culture
- Shared responsibility for outcomes
- Blameless learning from failures
- Curiosity across functional lines
- **Signal of weakness**: "That's not my team's problem"

### Automation
- Eliminate manual handoffs
- Reproducible builds, immutable deploys, IaC
- **Signal of weakness**: deploy steps in a runbook PDF

### Lean
- Small batch sizes
- Value stream thinking (where is the delay?)
- Limit work in progress
- **Signal of weakness**: 3-month release trains

### Measurement
- Metrics inform, not blame
- Both technical (DORA) and human (SPACE)
- **Signal of weakness**: vanity metrics (e.g., "lines of code")

### Sharing
- Knowledge and tools flow across teams
- Inner-source code, shared learnings
- Cross-team rotations
- **Signal of weakness**: tribal knowledge silos

## Using CALMS as a Maturity Audit

For each dimension, score 1–5:

| Score | Meaning |
|---|---|
| 1 | Hostile to this dimension |
| 2 | Aware but not investing |
| 3 | Inconsistent practice |
| 4 | Consistent, room to deepen |
| 5 | Cultural default |

Plot as a radar chart. Imbalances reveal where the next investment belongs.

## Common Imbalances

- **Strong A, weak C** — automation theater; tools exist, behavior hasn't changed
- **Strong M, weak C** — metric-obsessed; teams game numbers
- **Strong C, weak A** — believer culture, painful execution
- **Strong A & M, weak L & S** — local optima per team, no value stream view

## Interview Prep

**Mid**: "What does CALMS stand for?"

**Senior**: "Your team scores 4-4-2-4-2 on CALMS. What do you prioritize?"
- Lean and Sharing are weak. Likely symptoms: big batches and isolated teams. Propose value stream mapping + an inner-source initiative.

**Staff**: "You're hired into a 500-engineer org. They have great automation but blame culture. Where do you start?"

## Next Topic

→ [T02 — The Three Ways](T02-Three-Ways.md)
