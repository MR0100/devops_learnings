# L15/C01/T03 — The Deployment Pipeline (Humble & Farley)

## Learning Objectives

- Understand the canonical pipeline
- Apply principles

## Source

Jez Humble + David Farley, "Continuous Delivery" (2010). Defining text.

## Deployment Pipeline

Path from commit to prod:
```
Commit → Build → Test → Stage → Prod
```

Each step: more confidence, more cost.

## Principles

### Build Binaries Once
Build artifact once; promote through stages.
Same binary tested in dev → staging → prod.

Don't rebuild per stage (drift risk).

### Use Same Process Everywhere
Deploy to dev same way as prod (script, infra).
Differences = surprise risk.

### Smoke Test Deploys
Verify after deploy:
- Health endpoint
- Basic flow

### Deploy to Production Copy
Staging = prod-like.
Schema, config, data shape similar.

### If Anything Fails, Stop the Line
Broken main → team fixes.

### Done Means Released
"Done" = in prod.
Not "feature branch merged."

### Everyone Responsible
Devs + SRE + QA share pipeline ownership.

## The Pipeline Stages

```
1. Commit Stage     (< 5 min)
   - Compile
   - Unit tests
   - Static analysis
   - Build artifact

2. Auto Accept Stage (< 30 min)
   - Integration tests
   - Acceptance tests
   - Deploy to test env

3. Manual Test Stage (variable)
   - UAT
   - Exploratory
   - (only if needed)

4. Auto Release Stage
   - Deploy to staging
   - Smoke test
   - Promote to prod

5. Production
   - Canary
   - Monitor
   - Rollback or promote
```

## Commit Stage

Fast feedback:
- Compile
- Lint
- Unit tests (fast)
- Static security checks

If fail: notify quickly; team blocked.

Goal: < 5 min.

## Acceptance Stage

Slower; integration:
- Deploy to ephemeral test env
- API tests
- E2E (some)
- Performance smoke

Goal: < 30 min.

## Manual Stage

For:
- Exploratory testing
- UAT
- Compliance review

Skip if not needed.

## Release Stage

To staging / prod:
- Smoke tests
- Performance tests
- Canary

## Pipeline as Code

```yaml
# .github/workflows/pipeline.yml
name: Pipeline

on:
  push:
    branches: [main]

jobs:
  commit:
    runs-on: ubuntu-latest
    steps:
      - run: make test
      - run: make build
  acceptance:
    needs: commit
    runs-on: ubuntu-latest
    steps:
      - run: make integration-test
  release:
    needs: acceptance
    runs-on: ubuntu-latest
    steps:
      - run: make deploy-staging
      - run: make smoke
      - run: make deploy-prod
```

## Artifacts Promoted

```
[Build]
   ↓ artifact:v1.2.3-abc
[Test stage uses artifact]
   ↓
[Stage stage uses artifact]
   ↓
[Prod uses artifact]
```

Tag once; reference everywhere.

## Configuration Per Env

```
Same binary
├─ Dev config
├─ Staging config
└─ Prod config
```

Externalize config (env vars, ConfigMap).

## Quality Gates

```
Stage          Gate
-----          ----
Commit         Tests pass; lint clean
Acceptance     Integration tests pass; coverage threshold
Release        Approval (if not CDeploy); SLO baseline
```

## Fast Failures Earlier

```
Commit stage: cheap checks (lint, unit)
Acceptance:    expensive (integration)
Release:       slowest (E2E, perf)
```

Catch issues at cheapest stage.

## Visibility

Dashboard:
- Pipeline status per commit
- Stage-by-stage
- Failure reasons

For: shared understanding.

## Failure Recovery

```
Stage X fails →
  - Notify
  - Auto-revert (if release stage)
  - Block downstream
```

Forward fixes preferred.

## Parallelism

```yaml
acceptance:
  strategy:
    matrix:
      suite: [api, ui, integration]
```

Run suites in parallel. Total = max(suites).

## Pipeline Templates

```yaml
# In team repo
uses: org/.github/.github/workflows/standard-pipeline.yml@main
```

Standard pipeline across teams.

## Idempotent Deploys

Deploy command: same result each run.
- Replay-safe
- Recover from partial failures

For: declarative IaC, K8s.

## Environment Parity

```
Dev:     same OS, same DB engine, scaled down
Staging: prod-shaped, near-prod data volume
Prod:    actual
```

Diff = surprise risk.

## Database in Pipeline

Migrations:
- Run before app deploy
- Compatible with old + new app (rolling)
- Migration in pipeline (not manual)

Tools: Flyway, Liquibase, Alembic.

## Infrastructure in Pipeline

```yaml
- name: Terraform plan
  run: terraform plan
- name: Terraform apply
  run: terraform apply -auto-approve
  if: github.ref == 'refs/heads/main'
```

For: IaC pipeline.

## Pipeline for Pipeline

CI for CI configs.
Validate pipeline YAML before merging.

## Common Pipeline Anti-Patterns

### Rebuild per Stage
Drift between artifacts.

### Manual Steps
Hidden / undocumented.

### Long Pipelines
Slow feedback.

### Stage-Specific Code
"Special case for prod" — leaks risk.

### Skip Tests in Prod Deploy
"It's an emergency!" — increases risk.

## Metrics

- Pipeline duration (target trends down)
- Failure rate per stage
- Lead time
- Deploy frequency
- MTTR

## Real Examples

### Etsy
Continuous Deployment pipeline; 50+ deploys/day.

### Facebook
Pipeline + canary; thousands of changes/day.

### Spotify
Per-team pipelines; central platform.

## Modern Variations

### GitOps
Pipeline → push to Git → ArgoCD applies.

### Progressive Delivery
Pipeline → canary % → auto promote / rollback.

### Multi-Cloud Deploy
Pipeline → parallel deploys per cloud.

## Build vs Deploy Pipelines

Often split:
- Build pipeline: per commit; produces artifact
- Deploy pipeline: promotes artifact through envs

For: clean separation.

## Triggers

- Push (build)
- Schedule (nightly)
- Manual (deploy to prod)
- Webhook (downstream events)

## Best Practices

- Build once
- Test in prod-like
- Manual gates only where required
- Fast commit stage
- Parallel where possible
- Visible status
- Easy rollback
- Pipeline as code

## Common Mistakes

- Rebuild per stage
- Manual deploys
- No staging
- Skip tests
- Pipeline drift between repos

## Quick Refs

```
Commit stage:    < 5 min (lint, unit, build)
Acceptance:      < 30 min (integration)
Release:         deploy + smoke
Production:      canary + monitor
```

## Interview Prep

**Mid**: "Deployment pipeline."

**Senior**: "Pipeline design principles."

**Staff**: "Pipeline at scale."

## Next Topic

→ Move to [L15/C02 — Pipeline Design](../C02/README.md)
