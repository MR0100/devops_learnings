# L15 — CI/CD Fundamentals & Pipeline Design

## Overview

CI/CD is where code becomes product. Pipeline design is an engineering discipline. This lecture covers principles; L16 covers specific tools.

**8 chapters, 28 topics.**

## Chapter Map

### [C01](C01/) — CI/CD Concepts
- T01 Continuous Integration
- T02 Continuous Delivery vs Continuous Deployment
- T03 The Deployment Pipeline (Humble & Farley)

### [C02](C02/) — Pipeline Design
- T01 Build → Test → Package → Deploy Phases
- T02 Pipeline as Code
- T03 Fan-Out / Fan-In Patterns
- T04 Parallelism & Caching

### [C03](C03/) — Build Systems
- T01 Make, Bazel, Buck2
- T02 Reproducible Builds
- T03 Hermetic Builds

### [C04](C04/) — Testing in Pipelines
- T01 Test Pyramid Revisited
- T02 Unit, Integration, E2E
- T03 Contract Testing (Pact)
- T04 Performance, Load, Soak Tests
- T05 Security Tests in CI
- T06 Flaky Test Management

### [C05](C05/) — Artifact Management
- T01 Artifact Repositories (Artifactory, Nexus, ECR, GAR)
- T02 Immutable Tags & Digests
- T03 SBOM Generation

### [C06](C06/) — Deployment Strategies
- T01 Recreate
- T02 Rolling Update
- T03 Blue/Green
- T04 Canary
- T05 Shadow Deployments
- T06 A/B Testing

### [C07](C07/) — Progressive Delivery
- T01 Feature Flags (LaunchDarkly, Unleash, OpenFeature)
- T02 Flagger, Argo Rollouts
- T03 Automated Rollback Triggers

### [C08](C08/) — Release Engineering
- T01 Semantic Versioning
- T02 Release Trains
- T03 Hotfix Workflows

## The Reference Pipeline

```
[Commit] ─► [Static Analysis + Lint]
            │ (< 30 sec)
            ▼
         [Unit Tests]
            │ (< 2 min)
            ▼
         [Build Artifact]
            │ (< 5 min)
            ▼
         [Security Scan + SBOM]
            │ (< 2 min)
            ▼
         [Integration Tests]
            │ (< 5 min)
            ▼
         [Push to Registry]
            │
            ▼
         [Deploy to Staging]
            │
            ▼
         [Smoke + E2E Tests]
            │
            ▼
         [Canary to Prod (1% → 10% → 50% → 100%)]
            │
            ▼
         [Monitor SLOs; auto-rollback on burn]
```

Total goal: < 30 minutes from commit to production for an experienced team.

## Deployment Strategy Comparison

| | Recreate | Rolling | Blue/Green | Canary | Shadow |
|---|---|---|---|---|---|
| Downtime | Yes | No | No | No | No |
| Cost (env) | 1× | 1× | 2× | 1× + a bit | 2× |
| Rollback speed | Slow | Slow | Instant | Fast | N/A |
| Verify in prod | After | During | After cutover | Per-cohort | Yes (no traffic) |
| Best for | Schema-incompat | Default | Critical | Risky changes | New service |

## Progressive Delivery Stack

```
Code ─► Feature Flag (off)
         │
         ▼
       Deploy (release decoupled from rollout)
         │
         ▼
       Toggle flag for 1% of users
         │
         ▼
       Monitor SLOs / errors / latency
         │
         ▼
       Expand to 10%, 50%, 100% — or rollback
```

Tools: Flagger, Argo Rollouts (automated); LaunchDarkly, Unleash, OpenFeature (flags).

## Recommended Reading

- *Continuous Delivery* — Jez Humble, David Farley (the bible)
- *Accelerate* — Forsgren, Humble, Kim
- *Release It!* — Michael Nygard

## Interview Themes

- "Design a CI/CD pipeline"
- "Compare deployment strategies"
- "What's progressive delivery?"
- "Flaky tests — how do you handle them?"
- "Decouple release from deploy — what does that mean?"

## Next

→ [L16 — CI/CD Tools](../L16-cicd-tools/README.md)
