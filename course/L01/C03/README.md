# L01/C03 — The DevOps Lifecycle

## Chapter Overview

The familiar "infinity loop" diagram. Every textbook shows it; few explain what each phase actually entails and how feedback loops cross phases. This chapter does both.

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Plan-Code-Build-Test.md) | Plan, Code, Build, Test | 45 min |
| [T02](T02-Release-Deploy-Operate-Monitor.md) | Release, Deploy, Operate, Monitor | 45 min |
| [T03](T03-Feedback-Loops.md) | Feedback Loops at Every Stage | 30 min |
| [T04](T04-Infinity-Loop-Deconstructed.md) | The Infinity Loop Diagram (Deconstructed) | 30 min |

## The Lifecycle Diagram

```
       Plan ─→ Code ─→ Build ─→ Test ─→ Release ─→ Deploy
        ▲                                              │
        │                                              ▼
   Continuous                                      Operate
   Improvement                                        │
        │                                              ▼
        └────────────── Monitor ◀──── Feedback ◀──── Users
```

## Learning Outcomes

- Identify the artifact, tools, and SLAs at each phase
- Name the failure modes when a phase is weak
- Diagram feedback loops between phases
- Critique the infinity loop's simplifications (it's a model, not reality)

## Key Insight

Every phase has *both* a left-to-right flow (work) and a right-to-left signal (feedback). The infinity diagram emphasizes flow; the Three Ways model emphasizes both.

## Recommended Reading

- *Continuous Delivery* (Humble & Farley) — for Build, Test, Release, Deploy in depth
- *Lean Enterprise* (Humble, Molesky, O'Reilly) — for Plan and Operate at scale
