# L15/C08/T03 — Hotfix Workflows

## Learning Objectives

- Run hotfix process
- Avoid common mistakes

## Hotfix

Emergency fix to production between regular releases.

For: critical bugs, security CVEs, data loss.

## When

P0 / SEV1 only:
- Outage
- Data corruption
- Security CVE (active exploit)
- Compliance violation

NOT for:
- Annoyances
- Cosmetic
- Wait-able issues

## Process

```
1. Detect (alert, customer report)
2. Triage (severity)
3. Identify (which commit caused)
4. Fix (smallest possible)
5. Test (minimal but critical)
6. Deploy (fast track)
7. Verify (monitor)
8. Backport (to main if from release branch)
9. Postmortem
```

## Branch Strategy

```
main: ongoing dev
release/v1.0: production
hotfix/v1.0.1: branched from v1.0.0 tag

After hotfix:
- Tag v1.0.1
- Deploy
- Merge hotfix → main
```

## Fast Track Pipeline

```yaml
on:
  push:
    tags:
      - 'hotfix-*'

jobs:
  hotfix-deploy:
    runs-on: ubuntu-latest
    steps:
      - run: ./deploy.sh --hotfix
```

Skip some quality gates? Tradeoff:
- Skip = fast but risky
- Don't skip = slow but safe

For: minimal skip; usually keep tests.

## Forward Fix vs Rollback

### Rollback
```bash
kubectl rollout undo deploy/myapp
```

Fast; safer.

### Forward Fix
Apply patch; deploy new version.

For: rollback impossible (data migration done) or breaks newer features.

For most: rollback first; fix second.

## Smallest Possible Diff

```diff
- response = api.call(timeout=10)
+ response = api.call(timeout=60)
```

One-line change. Minimal risk.

Don't add features. Don't refactor.

## Test Coverage

Even hotfix: test the fix:
- Unit test reproducing bug
- Verify fix
- Smoke test in pre-prod

Skip full E2E if time-critical; full suite post-deploy.

## Verification

After deploy:
- Watch error rate
- Monitor affected feature
- Check customer reports

For: confirm fix.

## Backport

Hotfix on release/v1.0:
```bash
git checkout main
git cherry-pick HOTFIX_COMMIT
git push
```

Or merge release back to main.

For: don't reintroduce bug.

## Postmortem

After:
- Why did this happen?
- Why wasn't it caught?
- How prevent next time?

(See L18/C05.)

## Communication

During incident:
- Status page update
- Customer comms
- Slack incident channel

For: visibility.

## Roles

- IC (Incident Commander): coordinates
- Subject matter expert: fixes
- Comms: external
- Scribe: notes

For: large incidents.

## Hotfix Anti-Patterns

### "Just SSH and Fix"
Bypass IaC; drift.

For: never. Always via pipeline.

### Skip Code Review
Reviewer catches issues. Don't skip.

Quick review (one approver) OK.

### Skip Tests
Test the fix at minimum.

### Big Hotfix
"While we're here..." adds risk.

For: stay focused.

## Database Hotfix

Risky:
- Schema migration in hotfix
- Backfill scripts
- Cleanup

Test heavily. Have backup.

## Config Hotfix

```yaml
# Quick config change via ConfigMap
kubectl edit configmap myapp-config
```

For: feature flag, threshold, timeout.

Often safer than code hotfix.

## Feature Flag for Hotfix

```javascript
if (flags.isEnabled('buggy-feature')) {
  // Buggy code
}
```

Toggle off. Instant fix.

For: code already deployed; flag-based.

## Rollback Limitations

Rollback fails if:
- DB migration done (forward only)
- Persistent state changed
- Newer deps incompatible

For: forward fix needed.

## Hotfix Schedule

- Always 24/7 (P0)
- Coordinate via on-call
- Don't hotfix Friday night unless P0

For: weekend on-call considers ops cost.

## Documentation

Each hotfix:
- Ticket
- Why
- What changed
- Test plan
- Deploy log
- Postmortem

For: future reference.

## CI Fast Path

```yaml
- name: Hotfix path
  if: contains(github.ref, 'hotfix')
  steps:
    - run: make test-critical   # subset
    - run: make deploy-prod
```

Subset test for speed.

## Cherry-Pick Workflow

```bash
git checkout release/v1.0
git cherry-pick -x FIX_COMMIT
# -x adds reference to original

git push origin release/v1.0
git tag v1.0.1
git push --tags
```

For: backport fix.

## Multiple Stable Branches

Enterprise: support v1.0, v1.1, v1.2:
- Hotfix needs cherry-pick to all
- Tools: backport-bot
- Or: forward-only newer; fix old separately

## Stale Branches

After release:
- Active branch: latest
- Stable: maintenance only
- Legacy: sunset announced

Cleanup branches after sunset.

## Best Practices

- P0 only
- Smallest diff
- Test the fix
- Deploy quickly via pipeline
- Verify after
- Backport to main
- Postmortem

## Common Mistakes

- SSH + fix manually
- Skip tests
- Add unrelated changes
- Forget backport (bug returns)
- No postmortem
- No comms

## Cost

Hotfix cost:
- Engineer focus (interrupts roadmap)
- On-call stress
- Postmortem time
- Customer trust hit

For: minimize. Push for engineering quality.

## Frequency

If many hotfixes:
- Quality gates failing
- Test coverage low
- Process broken

For: signal to invest in quality.

## Real Examples

### Cloudflare BGP Incident
Hotfix global network; minutes mattered.

### Apple OS hotfixes
Quick App Store push.

### Web SaaS
Multiple daily hotfixes for high-velocity teams.

## Quick Refs

```bash
# Hotfix branch
git checkout -b hotfix/v1.0.1 v1.0.0
# Fix...
git commit
git push

# Pipeline triggers
git tag v1.0.1
git push --tags

# Backport
git checkout main
git cherry-pick -x FIX_COMMIT
```

## Interview Prep

**Mid**: "Hotfix process."

**Senior**: "Hotfix tradeoffs."

**Staff**: "Reduce hotfix need."

## Next Topic

→ Move to [L16 — Observability](../../L16-cicd-tools/README.md)
