# L15/C01/T02 — Continuous Delivery vs Continuous Deployment

## Learning Objectives

- Distinguish CD types
- Pick model

## Definitions

### Continuous Delivery
Code always in releasable state. Deploy is button-press.

### Continuous Deployment
Every commit auto-deploys to prod (after passing).

Subtle difference: deployment is automated; delivery is enabled.

## Spectrum

```
CI only:
   Commit → Test → Stop

Continuous Delivery:
   Commit → Test → Stage → Manual gate → Prod

Continuous Deployment:
   Commit → Test → Stage → Auto → Prod
```

## Why Each

### Continuous Delivery
- Always shippable
- Human approval (compliance, business decision)
- Lower risk
- Slower releases

### Continuous Deployment
- Fastest feedback
- Smallest changes
- Highest deploy frequency
- Requires strong CI + monitoring

## Maturity

```
Manual deploy (slow, risky)
   ↓
Scripted deploy (faster)
   ↓
Continuous Delivery (button)
   ↓
Continuous Deployment (auto)
```

Progression.

## Continuous Deployment Requirements

- Automated tests (high confidence)
- Feature flags (decouple deploy from release)
- Monitoring (catch regressions)
- Rollback fast (or auto)
- Small commits
- Low blast radius (canary)

## Examples

### Etsy
Deploys 50+ times/day. CD.

### Amazon
Thousands of deploys/day across services.

### Banks / Healthcare
Continuous Delivery (manual approval for compliance).

## Approval Gates

```yaml
- stage: deploy-prod
  needs: deploy-staging
  approval: required  # human
  jobs: ...
```

For: CD without CDeploy.

## Auto Promotion

```yaml
- stage: deploy-staging
  jobs: ...
- stage: smoke-test-staging
  jobs: ...
- stage: deploy-prod
  if: smoke-test-staging.success
  jobs: ...
```

For: Continuous Deployment.

## Deploy ≠ Release

With feature flags:
- Deploy: code in prod, flag off
- Release: flag on for users

Decouples ops from product.

For CDeploy: deploy often, release deliberately.

## Trunk + Flags = CDeploy Friendly

Patterns:
- Small commits
- Flag everything risky
- Deploy on green
- Toggle when ready

## Rollback Strategy

### Forward
Fix bug in new commit. Deploy.

For: fast iteration.

### Backward
Revert to previous version.

For: emergency.

Modern: forward preferred (with strong CI).

## Risk Mitigation

### Canary
1% → 10% → 50% → 100%.

If errors at 1%: rollback. Limited blast.

### Feature Flag
Disable feature; investigate.

### Auto-Rollback
Trigger on error spike.

Combined: low-risk CDeploy.

## Org Patterns

### Decentralized (FAANGM)
Each team deploys independently. CDeploy.

### Centralized
Release manager coordinates. Continuous Delivery.

## Regulated

### CDeploy possible
- SOC 2 compatible (logs + change records)
- HIPAA compatible (controls in place)
- PCI compatible (testing + monitoring)

Not legally prohibited; need controls.

### Continuous Delivery
Manual approval audit trail. Easier for regulated.

## Cost

CDeploy: requires investment:
- Testing automation
- Monitoring
- Rollback tooling
- Culture

Continuous Delivery: lower cost; manual gate.

## Failure Modes

### CDeploy
- Bug in prod fast
- Mitigation: canary + flags + rollback

### Continuous Delivery
- Releases lag
- Slow feedback
- Big batches when finally release

## Metrics (DORA)

- Deploy frequency: hours / days / weeks
- Lead time: commit → prod
- Failure rate: % deploys with issues
- MTTR: time to restore

CDeploy: best on first two; needs care on last two.

## Tools

- GitHub Actions + ArgoCD (GitOps)
- Spinnaker (Netflix)
- Harness
- LaunchDarkly (feature flags)
- Argo Rollouts (progressive)

## GitOps + CDeploy

```
Code push → CI → Build image → Push to registry
   ↓
Update Git manifest (image tag)
   ↓
ArgoCD syncs cluster → New image deployed
```

Auto, declarative.

## Progressive Delivery

Combines CDeploy + canary + flags + auto-rollback:
- Deploy every commit
- 1% traffic
- Monitor SLI
- Promote or rollback auto

For: safest CDeploy.

## Choose

### Pick CD (Delivery)
- Regulated heavy
- Lower frequency OK
- Risk-averse
- Smaller team

### Pick CDeploy
- High velocity
- Trust automation
- Strong monitoring
- Microservices culture

## Hybrid

Common:
- Staging: CDeploy
- Prod: Continuous Delivery (button)

For: friction at prod only.

Or:
- Web: CDeploy
- DB migrations: manual
- Infra: PR-approval

## Best Practices

- Small commits
- Feature flags
- Strong monitoring
- Auto-rollback
- Canary
- Audit trail (DORA, change logs)
- Practice rollbacks

## Common Mistakes

- CDeploy without monitoring (blind)
- Manual approval that's rubber-stamp
- No feature flags (any deploy = release)
- Big releases (no CD culture)

## Quick Refs

```
CI:                Build + test on commit
Continuous Delivery: Releasable state; manual promote
Continuous Deployment: Auto promote on green

Required for CDeploy:
- Tests
- Monitoring
- Rollback
- Flags
- Canary
```

## Interview Prep

**Junior**: "CD definitions."

**Mid**: "Delivery vs Deployment."

**Senior**: "When CDeploy."

**Staff**: "CD maturity at org."

## Next Topic

→ [T03 — The Deployment Pipeline (Humble & Farley)](T03-Deployment-Pipeline.md)
