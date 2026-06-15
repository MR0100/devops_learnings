# L28/C04/T06 — Design Netflix's Deployment Platform

## Learning Objectives

- Design deployment platform
- Spinnaker-like

## Requirements

### Functional
- Multi-cloud deploy
- Pipeline orchestration
- Canary
- Rollback
- A/B

### Non-Functional
- 1000+ deploys/day
- Multi-region
- 99.9% uptime
- Self-service

## Estimation (derived)

The interesting number isn't deploys/day — it's concurrent in-flight pipelines, because a deploy with canary analysis runs for a long time:
```
deploys/day        = 1,000
avg_pipeline_min   = 30        (build → canary bake → analysis → rollout)
seconds/day        = 86,400
concurrent (Little)= (1,000/86,400 per s) × (30×60 s) ≈ 21 in flight
peak (bursty: business-hours, pre-release) ≈ 3× ≈ 60+ concurrent pipelines
```
Each pipeline is long-lived and stateful (it waits on canary windows, approvals, bakes), so the orchestrator must **persist pipeline state** and survive its own restart mid-deploy — you can't lose a half-finished production rollout. That's the design driver: durable execution, not raw QPS.
```
state_writes/pipeline ≈ dozens (per stage transition) → modest DB load, but durability is non-negotiable
```

## Components

### Pipeline Engine
- DAG-based
- Steps
- Approvals
- Stages

### Cloud Driver
- AWS, GCP, Azure, K8s
- Abstract operations
- Per-cloud impl

### Orchestrator
- Run pipelines
- State tracking

### Canary Analysis
- Statistical (Kayenta)
- Metric-based decision

### UI
- Pipeline view
- Status
- Logs
- Trigger

### State Store
- Pipeline runs
- Persistent
- Replicable

### Triggers
- Webhook
- Schedule
- Chain (other pipelines)

## Architecture

```
Devs → UI / API → Pipeline Engine → Orchestrator
                                          ↓
                                  Cloud Driver
                                          ↓
                                  AWS / GCP / K8s
                                          ↓
                                  Canary Analysis
                                          ↓
                                  Promote / Abort
```

## Multi-Cloud

Cloud Driver abstracts:
- "Deploy to cluster X"
- "Run health check"
- Same pipeline; different clouds

## Deep Dive: Automated Canary Analysis

The hard problem in a deployment platform is *deciding* whether a new version is safe without a human staring at dashboards. Kayenta-style analysis:
- Run **baseline (current) and canary (new)** side by side, taking the same fraction of traffic so they see comparable load.
- Compare metric **distributions** (error rate, latency p99, CPU) — not single points — using statistical tests (Mann-Whitney / t-test) to ask "is the canary meaningfully worse?" with significance, so noise doesn't trigger false aborts.
- Crucial subtlety: compare canary against a **fresh baseline deployed at the same time**, not against the old long-running instances — otherwise warm-cache and JIT effects make any new version look bad.
- Emit a score → **auto-promote** above threshold, **auto-abort + rollback** below, escalate to a human in the ambiguous middle.

This is what lets 1000 deploys/day happen safely: most are gated by math, not meetings.

## Deep Dive: Durable Orchestration

A pipeline is a long-running stateful workflow (it waits minutes-to-hours on bakes, canary windows, approvals), so the orchestrator (Orca-style) must:
- **Persist every stage transition** to a DB so a crashed orchestrator resumes exactly where it left off — you never re-run a completed production rollout or lose a half-finished one.
- Model the pipeline as a **DAG** so independent stages run in parallel and dependencies are explicit.
- Make stage handlers **idempotent** (C03/T01) so resuming after a crash doesn't double-deploy.

## Spinnaker Components

- Deck (UI)
- Gate (API)
- Orca (orchestration)
- Clouddriver (cloud ops)
- Kayenta (canary)
- Rosco (image bake)
- Front50 (storage)
- Igor (CI)
- Echo (notifications)

## HA

Each component:
- Multi-replica
- Stateless mostly
- DB / Redis for state

## Self-Service

Templated pipelines:
- Service onboards
- Auto pipeline
- Customize via YAML

## Real

Netflix invented Spinnaker.

Used at:
- Many enterprises
- Some FAANGM-adjacent

## Trade-Offs

- Complex (many components)
- Powerful
- Steep learning

For modern: ArgoCD often replacing.

## Best Practices

- Pipeline templates
- Canary for risky
- Manual judgement for prod
- Multi-region rollout
- Notifications

## Common Mistakes

- No canary
- All manual approval (slow)
- No rollback test
- Single replica components

## Quick Refs

```
Components:
- UI / API
- Orchestrator
- Cloud Driver
- Canary
- Storage
- Triggers

Pattern: Pipeline → Stages → Cloud Driver → Deploy
```

## Interview Prep

**Senior**: "How does automated canary analysis decide to promote or roll back?" — It runs the new version (canary) and a freshly-deployed baseline side by side on equal traffic, then compares metric distributions — error rate, latency, resource use — with statistical tests rather than eyeballing single points. A score above threshold auto-promotes, below auto-rolls-back, and the ambiguous middle escalates to a human. Comparing against a fresh baseline (not the warm old instances) is what avoids false negatives.

**Staff**: "Design a deployment platform that does 1000 safe deploys a day." — DAG-based pipelines (build → bake → canary → staged rollout) driven by a durable orchestrator that persists every stage transition, so a crash resumes mid-deploy instead of losing or repeating a rollout. A cloud-driver abstraction makes the same pipeline target AWS/GCP/K8s, automated canary analysis gates risky changes with statistics, and idempotent stage handlers make resume safe. The throughput comes from gating on math, not approvals.

**Principal**: "Make this multi-cloud and resilient to its own failure." — A cloud-driver layer abstracts 'deploy', 'health-check', 'rollback' per provider so one pipeline definition runs anywhere. Each orchestrator component is stateless-with-external-state (DB/Redis) and multi-replica, so losing a node doesn't lose a pipeline. The deploy platform must itself be more available than what it deploys — so it's multi-region, its state store is replicated, and rollback is a first-class, tested path (a rollback you've never exercised is the one that fails during the incident that needs it).

## Next Topic

→ [T07 — Design an Internal Developer Platform](T07-Design-IDP.md)
