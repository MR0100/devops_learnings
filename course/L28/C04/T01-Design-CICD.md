# L28/C04/T01 — Design a CI/CD Platform

## Learning Objectives

- Design CI/CD
- Cover scale

## Requirements

### Functional
- Build code
- Run tests
- Deploy
- Multi-language
- Many teams

### Non-Functional
- 10k builds/day
- < 10 min typical
- 99.9% availability
- Self-service

## Capacity

10k builds/day:
- ~7/min peak
- Some long (1 hr); most short (5 min)

Concurrent: ~50-200.

## Components

### Triggers
- Push webhook
- Schedule
- Manual

### Queue
Builds queued.

### Runners
- Executors
- Auto-scale
- Multiple types (Linux, macOS, GPU)

### Storage
- Source checkout
- Caches
- Artifacts

### Logging
- Per-build
- Searchable
- Long retention

### UI
- Pipeline status
- Logs
- Trigger

## Architecture

```
GitHub webhook → Controller → Queue → Runner pool → Artifact storage
                                                  → Logging
```

## Runner Pool

K8s + Karpenter:
- Per-job pod
- Spot for cost
- Auto-scale

## Artifacts

- Container images (ECR)
- Build outputs (S3)
- SBOMs

## Caching

- Dep cache (Maven, npm)
- Docker layer
- Distributed (S3-backed)

For: speed.

## Secrets

- Vault / Secrets Manager
- Per-job tokens (OIDC)

## Logging

- Per-job
- Loki / ELK
- Long retention (compliance)

## Observability

- Per-team metrics
- Failure rate
- Duration trends

## Multi-Tenant

- Per-team isolation
- Quotas
- Per-team artifacts

## Scaling

- Many runners
- Distributed control plane (Tekton, etc.)
- Sharded

## HA

- Multi-AZ runners
- Replicated state (etcd)
- LB front

## Cost

- Spot: 70% off
- Right-size runners
- Idle scale down

## Real Examples

- GitHub Actions
- GitLab CI
- CircleCI
- Buildkite

## Trade-Offs

- K8s native: complex; flexible
- SaaS: managed; less control
- Self-host: cost vs ops

## Best Practices

- Self-service
- Spot runners
- Distributed cache
- OIDC for auth
- Observability

## Common Mistakes

- Single runner pool
- No quotas (one team starves)
- No cache (slow)
- Static credentials

## Quick Refs

```
Triggers → Queue → Runners → Artifacts/Logs

Components:
- Controller
- Queue
- Runners (K8s + Karpenter + Spot)
- Storage
- Logging
- UI
```

## Interview Prep

**Senior**: "Design CI/CD."

**Staff**: "Scale to 10k builds/day."

## Next Topic

→ [T02 — Design a Multi-Region Kubernetes Platform](T02-Design-Multi-Region-K8s.md)
