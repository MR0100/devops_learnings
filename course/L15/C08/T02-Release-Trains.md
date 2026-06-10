# L15/C08/T02 — Release Trains

## Learning Objectives

- Understand release trains
- Apply where relevant

## Release Train

Periodic, scheduled releases:
- Weekly / bi-weekly / monthly
- Cut at scheduled time
- Train leaves; missed features wait

For: large orgs, mobile apps, OS releases.

## Why

- Predictability
- Coordination across teams
- QA cycles
- Marketing
- Customer expectations

## Vs Continuous Deployment

- CDeploy: every commit → prod
- Release Train: batch + scheduled

Different goals.

## Typical Cadence

### Mobile
- 2-week cycles (iOS / Android approve)
- iOS: requires App Store review

### Browser (Chrome / Firefox)
- 4-6 week stable releases

### Enterprise SaaS
- Monthly / quarterly releases
- Customer expectations

### Cloud SaaS
- Continuous (no train)

## Train Stages

```
Week 1: Development; commit to main
Week 2: Cut release branch; QA; stabilization
Week 3: Hotfixes only; deploy
```

Or:
- Dev: weeks 1-2
- Stabilize: week 3
- Deploy: week 4 (next train starts)

## Branch Strategy

```
main: ongoing dev
release/v1.0: cut from main
hotfix/v1.0.x: backports
```

## SAFe Release Train

Scaled Agile Framework:
- Agile Release Train (ART)
- Multiple teams sync
- PI (Program Increment): 10 weeks

For: enterprise process.

## Pros

- Predictable
- Sync across teams
- QA bandwidth managed
- Customer comms simple

## Cons

- Features wait if miss
- Big batch = bigger risk
- Long lead time
- Often combined with feature flags

## With Feature Flags

```
Code in main; flag off
Train leaves → prod
Toggle flag on at planned time
```

For: train cadence + feature timing decoupled.

## Stabilization

After cut:
- Bug fixes only
- No new features
- Backports from main if needed

For: stable release.

## Cherry-Pick

```bash
git checkout release/v1.0
git cherry-pick FIX_COMMIT
```

Backport fixes.

## Hotfix

After release; critical bug:
- Create hotfix/v1.0.1 from v1.0.0 tag
- Fix; tag v1.0.1
- Deploy
- Merge back to main

For: between-train fixes.

## When Release Train

- iOS / Android (forced by stores)
- OS (Windows, macOS)
- Enterprise software
- Hardware-coupled (firmware)
- Compliance heavy (PCI audit window)
- Marketing-driven

## When Not

- SaaS web
- Cloud-native
- Microservices

For: CDeploy preferred.

## Mobile Specifics

```
Sprint 1 (week 1-2): development
Sprint 2 (week 3-4): development
End of week 4: feature freeze; cut RC
Week 5: QA; bug fixes
Week 6: Submit to Apple/Google
Week 7-8: Reviews + staged rollout
```

iOS review: days. Plan for it.

## Beta Programs

```
v1.0.0-beta.1: TestFlight / Play beta
v1.0.0-rc.1: release candidate
v1.0.0: GA
```

User feedback before GA.

## Hotfix Decision Tree

```
Critical bug discovered:
- Severity?
  - P0 (data loss): hotfix immediately
  - P1: hotfix this train cycle
  - P2: next train
- Fixable in time?
  - Yes: cherry-pick
  - No: rollback (if possible) or wait
```

## Coordination

- Train dates published
- Release calendar
- Code freeze announcement
- QA assignments

For: predictable.

## Train Conductor

Role:
- Owns the train
- Decides what merges
- Coordinates hotfixes
- Communicates status

## Quality Bar

Pre-cut:
- All features merged
- Tests green
- Performance acceptable
- Security scan clean

For: train leaves only if quality met.

## "Missed the Train"

Feature not ready:
- Wait for next train (2 weeks)
- Keep working on main
- Don't rush bad code

For: discipline.

## Microservices Twist

Per-service train:
- Each service own cadence
- Mostly CDeploy
- Train pattern at app version level (mobile)

## Backend + Mobile

Mobile train; backend CDeploy:
- Mobile app v1.0: needs backend v2.5
- Backend deployed weeks ago; mobile catches up

For: backend backward compatible.

## Versioning

```
v1.0.0 (year + train number sometimes)
v25.10
2026.Q1
```

Convention varies.

## Documentation

Per-release:
- Release notes
- Breaking changes
- Migration guide

For: customer comms.

## Automated

CI:
```yaml
on:
  schedule:
    - cron: '0 0 * * MON'  # Weekly Monday
jobs:
  cut-release:
    steps:
      - run: ./cut-release.sh
```

For: scheduled automation.

## Best Practices

- Train calendar published
- Code freeze clear
- Stabilization stage
- Hotfix process documented
- Beta program
- Feature flags for risky

## Common Mistakes

- Skip stabilization (broken releases)
- No code freeze (last-minute features break)
- No hotfix process (panic when needed)
- Train delayed often (lose trust)

## Real Examples

### Chrome
6-week trains. Predictable.

### iOS / macOS
Yearly major; quarterly minor.

### Windows
Build train + feature update train.

### Salesforce
Three releases / year; predictable.

### Mobile games
Weekly content; monthly app train.

## Quick Refs

```
Cadence: weekly / monthly / quarterly
Branches: release/vN.M.x
Stabilization: post-cut
Hotfix: cherry-pick to release branch
```

## Interview Prep

**Mid**: "What's a release train."

**Senior**: "Train vs CDeploy."

**Staff**: "Coordination at scale."

## Next Topic

→ [T03 — Hotfix Workflows](T03-Hotfix-Workflows.md)
