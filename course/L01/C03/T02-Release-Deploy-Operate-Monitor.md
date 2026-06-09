# L01/C03/T02 — Release, Deploy, Operate, Monitor

## Learning Objectives

- Distinguish "release" from "deploy" (these are not synonyms)
- Identify operate and monitor activities and tooling
- Connect each phase to a DORA metric

## Release

**Activities**: artifact promotion through environments, approval gates, compliance evidence
**Artifacts**: release notes, change records, tagged versions
**Tools**: ArgoCD, Spinnaker, Octopus Deploy, internal release platforms
**SLOs**: time from "approved" to "ready to deploy"
**Failure modes**: manual approval bottlenecks; release notes lag actual changes

## Deploy

**Activities**: rolling out the artifact to a target environment, performing canary/blue-green
**Artifacts**: deployment records, deployment dashboards
**Tools**: Kubernetes (Deployments, Rollouts), AWS CodeDeploy, ArgoCD, Flagger
**SLOs**: deploy duration, rollback time, deploy success rate
**Failure modes**: lack of rollback rehearsal; missing health checks; "deploy = pray"

> **Release vs Deploy**: A release is the business decision that users get the change. A deploy is the technical act of placing code on machines. Feature flags decouple them.

## Operate

**Activities**: capacity management, incident response, on-call, backups, certificates, patching
**Artifacts**: runbooks, postmortems, capacity plans, SLO dashboards
**Tools**: PagerDuty, Opsgenie, Slack ChatOps, runbook frameworks
**SLOs**: MTTR, on-call page volume, error budget burn rate
**Failure modes**: tribal knowledge; runbooks rot; on-call as punishment

## Monitor

**Activities**: instrumentation, alerting, dashboards, log search, distributed tracing
**Artifacts**: metrics, logs, traces, alerts, SLOs
**Tools**: Prometheus, Grafana, Datadog, New Relic, OpenTelemetry, Loki, Jaeger
**SLOs**: alert noise ratio, false-positive rate, time to detect (TTD)
**Failure modes**: alert fatigue; dashboards no one reads; SLIs that don't match user experience

## How These Phases Connect to DORA

| Phase | DORA Influence |
|---|---|
| Release | Lead Time (delays after merge) |
| Deploy | Deploy Frequency, Change Failure Rate |
| Operate | MTTR (how fast can you fix) |
| Monitor | MTTR (how fast can you see) |

## Worked Example: A Deploy Going Bad

```
0:00  Deploy v2.4 to canary (1% traffic)
0:02  Error rate alert fires (Monitor)
0:03  On-call paged (Operate)
0:04  Auto-rollback triggered (Deploy / Release decoupled by flag)
0:06  Canary back to v2.3
0:08  Incident channel opened
0:10  Root cause identified: a config schema change
0:30  Fix merged; redeploy v2.4.1
```

MTTR: 6 minutes. CFR for this deploy: 100% (it failed). DF unaffected (the next deploy still happens).

## Interview Prep

**Mid**: "What's the difference between release and deploy?"

**Senior**: "Your team has 20-minute deploys and 6-hour MTTR. Where do you invest?"
- MTTR. Faster deploys without faster recovery means longer pain when things break. Improve canary, monitoring, runbooks.

**Staff**: "Design a deployment pipeline that ships 10x/day with < 5min MTTR for a 30-service architecture."

## Next Topic

→ [T03 — Feedback Loops at Every Stage](T03-Feedback-Loops.md)
