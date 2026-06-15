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

## Capacity (derived, not asserted)

Start from builds/day and derive concurrency — don't guess it:
```
builds_per_day   = 10,000
avg_build_min    = 5
seconds/day      = 86,400
avg_builds/sec   = 10,000 / 86,400 ≈ 0.12/s  → ~7/min average
```
Average understates what you must provision. Concurrency follows from **arrival rate × service time** (Little's Law: L = λ × W):
```
concurrent_avg = arrival_rate × build_duration
              = (10,000/86,400 per s) × (5×60 s) ≈ 35 builds in flight
```
But CI traffic is bursty — it clusters on weekday mornings and around merges, so peak ≈ 3–5× average:
```
peak_concurrent ≈ 35 × 5 ≈ 175  → provision ~200 concurrent slots
```
Two build classes change the sizing: most builds are short (~5 min) but a few are long (~1 hr). The long tail pins runners for 12× the duration, so reserve a separate pool/queue class for them or they starve the short queue. **Derived target: ~200 concurrent runners, with a long-build class carved out.**

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

## Deep Dive: Caching

Caching is the single biggest lever on build time and cost — a cold build re-downloads dependencies and rebuilds every layer.
- **Dependency cache** (Maven, npm, Go modules): keyed on a lockfile hash so a cache hit is provably correct. Restore before build, save after.
- **Docker layer cache**: BuildKit cache mounts or a registry-backed cache (`--cache-to`/`--cache-from`) so unchanged layers aren't rebuilt.
- **Distributed, not node-local**: runners are ephemeral and land on different nodes, so a node-local cache rarely hits. Back the cache with **S3** (or an OCI registry) so any runner in the fleet shares it.

Trade-off: a shared cache adds a network fetch (~hundreds of ms) but saves minutes — almost always worth it. The hazard is **cache poisoning**: scope cache keys per branch/lockfile so one bad build can't serve a corrupt artifact to others.

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

## Scaling & Bottlenecks

The risky parts of a CI/CD platform, in order:
- **Runner supply**: 0→200 spot nodes must come up in ~60s or queues back up. Karpenter provisions on pending pods; pre-warm a small warm pool to hide cold-start for the first builds of the day.
- **Scheduler throughput**: the webhook receiver + pipeline scheduler is the control-plane SPOF. Make it multi-AZ and stateless, with queue state in a replicated store (etcd / Postgres) — a distributed engine (Tekton, Argo Workflows) shards this.
- **Cache and artifact bandwidth**: 200 concurrent builds all pulling from S3 can saturate egress. Use a pull-through cache / regional mirror.
- **Noisy neighbor**: one team's 500 queued builds starve everyone. Per-team **concurrency quotas** + fair-share scheduling, not one global FIFO.
- **Spot reclamation**: a build on a reclaimed node dies mid-run. Handle the spot interruption signal → checkpoint or auto-retry on-demand, and keep long builds off spot.

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

**Mid**: "How do you make builds fast?" — Cache aggressively: dependency caches keyed on lockfile hashes and a registry-backed Docker layer cache, both S3-backed so ephemeral runners share them. Then parallelize independent stages and right-size runners so a cold build isn't the common case.

**Senior**: "Design a CI/CD platform for 1000 engineers at ~10k builds/day." — Webhook receiver → stateless scheduler → autoscaled per-job K8s runners (Karpenter + spot) → artifact/log storage → ArgoCD deploy. I'd derive concurrency with Little's Law (~35 avg, ~200 at peak), carve out a long-build class so 1-hour jobs don't starve 5-minute ones, give each team a concurrency quota, and use OIDC per-job tokens instead of static credentials.

**Staff**: "Builds are queuing for 20 minutes during the morning peak — diagnose and fix." — First localize the bottleneck: runner supply (slow scale-up), scheduler throughput, or a single team flooding the queue. Usually it's spot scale-up lag plus an unfair global FIFO. Fix with a warm pool to hide cold-start, per-team fair-share quotas so one repo can't monopolize slots, and a separate pool for long builds. I'd alarm on queue wait time (the SLA metric), not node count.

**Principal**: "Design CI/CD as a paved road that 50 teams actually adopt." — Pipelines as templated, versioned YAML owned by the platform team so security/SBOM/signing are wired in by default; self-service onboarding through the IDP; per-team isolation (quotas, artifacts, secrets) so a noisy tenant can't hurt others; OIDC workload identity end to end; and platform-level metrics (build success rate, p50/p95 duration, queue time) treated as an SLO. Opting off the paved road is allowed but the team then owns its own compliance.

## Next Topic

→ [T02 — Design a Multi-Region Kubernetes Platform](T02-Design-Multi-Region-K8s.md)
