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

## Canary

Kayenta-style:
- Old vs new
- Metric comparison
- Statistical significance
- Auto-promote / abort

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

**Staff**: "Design deploy platform."

**Principal**: "Multi-cloud CD."

## Next Topic

→ [T07 — Design an Internal Developer Platform](T07-Design-IDP.md)
