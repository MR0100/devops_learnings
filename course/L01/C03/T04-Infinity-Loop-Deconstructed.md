# L01/C03/T04 — The Infinity Loop Diagram (Deconstructed)

## Learning Objectives

- Critique the infinity loop as a teaching diagram
- Recognize what it captures well and what it hides
- Replace it with a richer model

## The Standard Diagram

```
       ╭─── Plan ── Code ── Build ── Test ───╮
       │                                       │
   Continuous                                 Release
       │                                       │
       ╰── Monitor ── Operate ── Deploy ─────╯
```

## What It Captures Well

- Continuous nature of the work (no end-state)
- Cyclical relationship between dev and ops phases
- Phases as roughly equal in importance

## What It Hides

| Reality | The Diagram Suggests |
|---|---|
| Phases run in parallel for different changes | Sequential single-flow |
| Failures and rollbacks are normal | Smooth ring |
| Customers and security are first-class participants | Internal IT view |
| Feedback flows right-to-left across phases | One-way clockwise |
| Some phases are 10× the work of others | Equal sized circles |

## A Better Diagram (proposed)

```
                  ┌─────────────────────────────┐
                  │      USERS / CUSTOMERS      │
                  └──────────┬──────────────────┘
                             │ signals
                             ▼
       ┌────────────────────────────────────────┐
       │   Observation Layer (logs, metrics,    │
       │   traces, business KPIs, support)      │
       └──┬──────────────────────────────────┬──┘
          │                                  │
      ┌───▼────────────┐              ┌──────▼───────┐
      │ Operate /      │              │  Plan /      │
      │ On-Call /      │              │  Prioritize  │
      │ Incident       │              └──────┬───────┘
      └───┬────────────┘                     │
          │                                  ▼
          │                       ┌──────────────────┐
          │                       │ Code / Build /   │
          │                       │ Test (CI)        │
          │                       └──────┬───────────┘
          │                              │
          │                              ▼
          │                       ┌──────────────────┐
          └─ rollback signal ◄────│  Release /       │
                                  │  Deploy (CD)     │
                                  └──────────────────┘
```

This shows that customers drive both planning *and* observation, that operate and plan are continuously informed by the observation layer, and that release/deploy is bidirectional with operate.

## When You Encounter the Standard Diagram in an Interview

A staff candidate uses it as a starting point, then sketches the richer version above. This signals you've actually thought about the model rather than memorized a graphic.

## Interview Prep

**Senior**: "Draw the DevOps lifecycle."
- Draw the standard, then improve it with feedback arrows and the customer layer.

**Staff**: "Critique the infinity loop diagram."
- Hits: sequential illusion, equal-sized phases, missing customer/security, no feedback richness.

## Next Chapter

→ [C04 — Roles, Titles & Career Paths](../C04/README.md)
