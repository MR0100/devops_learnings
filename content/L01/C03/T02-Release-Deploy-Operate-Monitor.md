# L01/C03/T02 — Release, Deploy, Operate, Monitor

## Learning Objectives

- Distinguish "release" from "deploy" (these are not synonyms) and use feature flags to decouple them
- Identify the activities, artifacts, tooling, and SLOs of the operate and monitor phases
- Connect each phase to a DORA metric and reason about where to invest (deploy speed vs. recovery speed)
- Read a deploy-gone-bad timeline and name the loop that fired at each step

## The Right Half of the Loop

Release → Deploy → Operate → Monitor is where the artifact built in T01 meets reality. The critical mental shift from the left half: **here, failure is normal and planned-for.** The left half tries to *prevent* defects; the right half assumes some escape and optimizes to *detect and recover* fast. A team that treats production failure as an exception builds brittle systems; a team that treats it as routine builds rollback rehearsals, canaries, and error budgets.

## Release

**Activities**: artifact promotion through environments, approval gates, compliance evidence, version tagging
**Artifacts**: release notes, change records, tagged versions, promotion records
**Tools**: ArgoCD, Spinnaker, Octopus Deploy, internal release platforms; feature-flag systems (LaunchDarkly, Flagsmith, OpenFeature)
**SLOs**: time from "approved" to "ready to deploy"; % of releases with accurate, auto-generated notes
**Failure modes**: manual approval bottlenecks (the CAB that meets Thursdays); release notes that lag the actual diff; "release" conflated with "deploy" so every config flip needs a full ship

Release is a **business decision**: who gets the change, when, and under what approval. Mature orgs make most releases self-service and reserve heavyweight approval for genuinely high-risk changes — research (DORA) consistently shows that *external* change-approval boards correlate with *worse* delivery performance and no better stability. Replace the board with peer review plus automated policy checks.

## Deploy

**Activities**: rolling the artifact onto target infrastructure; canary, blue-green, or rolling strategies; health-gated progression
**Artifacts**: deployment records, deployment dashboards, rollout status
**Tools**: Kubernetes (Deployments, Argo Rollouts), AWS CodeDeploy, ArgoCD, Flagger
**SLOs**: deploy duration, rollback time (target: < 5 min), deploy success rate
**Failure modes**: no rollback rehearsal (the rollback path is itself untested); missing health checks → bad version takes 100% traffic; "deploy = pray" with no progressive exposure

| Strategy | How it works | Rollback | Best for |
|---|---|---|---|
| **Rolling** | Replace instances N at a time | Roll forward/back gradually | Stateless services, default |
| **Blue-green** | Stand up full v2, flip traffic | Flip back instantly | Fast rollback, costs 2× during cutover |
| **Canary** | 1% → 5% → 50% → 100%, gated on metrics | Halt and revert at any step | High-risk changes, large blast radius |

> **Release vs Deploy**: A *release* is the business decision that users get the change. A *deploy* is the technical act of placing code on machines. **Feature flags decouple them** — you deploy code dark (flag off), then release by flipping the flag, with no redeploy. This is what lets a team deploy 50×/day while releasing features on a product schedule.

## Operate

**Activities**: capacity management, incident response, on-call, backups, certificate rotation, patching, DR drills
**Artifacts**: runbooks, postmortems, capacity plans, SLO dashboards, error budgets
**Tools**: PagerDuty, Opsgenie, Slack/Teams ChatOps, runbook frameworks, Backstage
**SLOs**: MTTR, on-call page volume (target: actionable pages only), error budget burn rate
**Failure modes**: tribal knowledge (one person knows how to fix it); runbooks that rot until they're wrong; on-call treated as punishment → burnout → attrition → more tribal knowledge

Operate is where **error budgets** live (covered in the SRE material). The budget reframes reliability from "never fail" to "fail within an agreed allowance" — when you're under budget, ship faster; when you've burned it, freeze features and invest in reliability. This makes the dev/ops tension a shared, numeric decision rather than a political fight.

## Monitor

**Activities**: instrumentation, alerting, dashboards, log search, distributed tracing, SLO tracking
**Artifacts**: metrics, logs, traces, alerts, SLOs, the "three pillars" of observability
**Tools**: Prometheus, Grafana, Datadog, New Relic, OpenTelemetry, Loki, Jaeger, Tempo
**SLOs**: alert signal-to-noise ratio, false-positive rate, time to detect (TTD)
**Failure modes**: alert fatigue (so many pages that real ones are missed); dashboards no one reads; SLIs that measure CPU instead of user experience

The distinction that matters: **monitoring** answers known questions ("is CPU high?") with predefined dashboards; **observability** lets you ask *new* questions of a misbehaving system you've never seen fail this way before — which requires high-cardinality, structured telemetry (traces with rich attributes), not just counters. Alert on **symptoms users feel** (latency, error rate — the SLOs) rather than causes (CPU, memory); cause-based alerts page you for things that may not matter and miss things that do.

## How These Phases Connect to DORA

| Phase | DORA Influence | Why |
|---|---|---|
| Release | Lead Time | Approval delays after merge are pure waiting time |
| Deploy | Deploy Frequency, Change Failure Rate | How often and how safely you ship |
| Operate | MTTR | How fast you can fix once it breaks |
| Monitor | MTTR (Time to Detect) | You can't fix what you can't see; TTD is the front of MTTR |

MTTR decomposes as **detect → diagnose → repair**. Monitor owns detect, Operate owns diagnose and repair. A team with a 6-hour MTTR usually has a detect problem (no good SLO alerts) or a diagnose problem (no traces, no runbooks), not a "people type slow" problem.

## Worked Example: A Deploy Going Bad

```
0:00  Deploy v2.4 to canary (1% traffic)            [Deploy]
0:02  Error-rate SLO alert fires                    [Monitor — detect]
0:03  On-call paged                                 [Operate]
0:04  Auto-rollback triggered                       [Deploy / Release decoupled by flag]
0:06  Canary back to v2.3                           [Deploy]
0:08  Incident channel opened                       [Operate]
0:10  Root cause: a config schema change            [Operate — diagnose]
0:30  Fix merged; redeploy v2.4.1                   [back to Build/Test → Deploy]
```

MTTR: ~6 minutes (back to v2.3). CFR for this deploy: 100% (it failed) — but only 1% of users saw it because the canary contained the blast radius. Deploy Frequency is **unaffected**: the next deploy still happens, because the pipeline didn't freeze. This is the whole point of progressive delivery — a failed deploy becomes a non-event, not an incident.

## Common Mistakes

- **Conflating release and deploy** — every feature flip requires a full redeploy because there's no flag layer, capping how fast the team can release
- **Untested rollback** — assuming you can roll back without ever rehearsing it; you discover the rollback is broken during the one incident where you need it
- **Cause-based alerting** — paging on CPU and memory instead of user-facing latency/error SLOs, producing noise and missing real outages
- **Heroic on-call** — manually firefighting the same incident weekly instead of automating it away, which burns out the on-call and hides the systemic fix
- **Investing in deploy speed when MTTR is the constraint** — shaving deploy time from 20 to 10 minutes while recovery still takes hours
- **Rotting runbooks** — writing them once and never updating, so the on-call follows steps that no longer match reality

## Best Practices

- **Decouple release from deploy with feature flags** — deploy code dark, release by flag flip; this unlocks high deploy frequency with a product-paced release cadence
- **Make rollback a rehearsed, automated path** — health-gated auto-rollback on canary, tested regularly, with a target under 5 minutes
- **Alert on symptoms, not causes** — SLO-based alerts (latency, error rate, saturation that users feel), and delete alerts that have never led to action
- **Treat on-call as a first-class system** — sustainable rotations, actionable-only pages, every page either auto-resolved or producing a follow-up action
- **Keep MTTR honest by decomposing it** — measure detect, diagnose, and repair separately and invest in the slowest stage
- **Auto-generate release notes from the merged diff** — so the change record never lags reality and the audit trail is a byproduct

## Quick Refs

```bash
# Roll back a Kubernetes deployment fast
kubectl rollout undo deployment/api          # to previous revision
kubectl rollout history deployment/api       # see revisions first

# Argo Rollouts: promote or abort a canary
kubectl argo rollouts get rollout api --watch
kubectl argo rollouts abort api              # halt and revert to stable

# Symptom-based Prometheus alert (error-rate SLO burn)
# alert: HighErrorRate
# expr: sum(rate(http_requests_total{code=~"5.."}[5m]))
#     / sum(rate(http_requests_total[5m])) > 0.01
# for: 2m

# Toggle a release without a deploy (feature flag via API)
curl -X PATCH $FLAG_API/flags/new-checkout -d '{"enabled": false}'
```

Metrics to own here: **Deploy Frequency, Change Failure Rate, MTTR** (three of the DORA four), plus **Time to Detect** and **alert signal-to-noise**.

## Interview Prep

**Junior**: "What does the operate phase involve?"
- Keeping the running system healthy: on-call and incident response, capacity and backups, certificate and patch management, and the runbooks and dashboards the team uses to do it.

**Mid**: "What's the difference between release and deploy?"
- Deploy is the technical act of putting code on machines; release is the business decision that users actually get the change — feature flags decouple them so you can deploy code dark and release later by flipping a flag, with no redeploy.

**Senior**: "Your team has 20-minute deploys and 6-hour MTTR. Where do you invest?"
- MTTR, decisively — faster deploys without faster recovery just means longer pain when something breaks; I'd decompose MTTR into detect/diagnose/repair, find the slow stage (usually detect or diagnose), and invest in SLO alerting, tracing, rehearsed rollback, and runbooks.

**Staff**: "Design a deployment pipeline that ships 10×/day with < 5min MTTR for a 30-service architecture."
- Decouple release from deploy with feature flags so deploys are low-risk; standardize progressive delivery (canary with health-gated auto-rollback via Argo Rollouts/Flagger) as a paved road every service inherits; enforce symptom-based SLO alerts and distributed tracing so detect+diagnose is fast; and make rollback an automated, regularly rehearsed path so a failed deploy is a non-event rather than an incident.

## Next Topic

→ [T03 — Feedback Loops at Every Stage](T03-Feedback-Loops.md)
