# L08/C11/T04 — Managed Prometheus & Grafana

## Learning Objectives

- Use AMP / AMG
- Decide vs self-host

## AMP (Amazon Managed Prometheus)

Managed Prometheus-compatible metrics:
- Workspace (per region)
- Remote-write endpoint for ingestion
- PromQL query
- Auto-scale; no servers

## Setup

```bash
aws amp create-workspace --alias my-prom
```

Returns endpoint:
```
https://aps-workspaces.us-east-1.amazonaws.com/workspaces/ws-xxx
```

## Send Metrics

Configure remote_write in Prometheus / OTel collector:
```yaml
remote_write:
  - url: https://aps-workspaces.../api/v1/remote_write
    sigv4:
      region: us-east-1
```

SigV4 auth via IAM role.

## EKS Integration

Prometheus scrapes pods; remote_write to AMP:
- Run Prometheus in cluster (lightweight; just scrape + forward)
- Or use ADOT collector

## Query

PromQL via AMP query endpoint:
```
http_requests_total{service="api"}
rate(http_requests_total[5m])
```

Through Grafana / AMG (next).

## AMG (Amazon Managed Grafana)

Managed Grafana:
- Workspace per account
- IAM Identity Center / SAML auth
- Pre-configured AMP / CloudWatch data sources
- Alerts via Grafana

```bash
aws grafana create-workspace --workspace-name myGrafana --account-access-type CURRENT_ACCOUNT --authentication-providers AWS_SSO
```

## Data Sources

AMG supports:
- AMP
- CloudWatch
- X-Ray
- Athena
- Redshift
- Timestream
- OpenSearch
- External (Prometheus, InfluxDB, etc.)

Unified dashboards across.

## Pricing

AMP:
- $0.90 per 10M samples ingested
- $0.10 per GB-mo stored
- $0.10 per million queries

For 10M metrics × 60 samples/hour × 24 × 30 = 432M samples/mo → $38.

AMG:
- $9/user/mo (admin)
- $5/user/mo (editor)
- $0/user/mo (viewer; up to 5)

For 10-person team: $50-90/mo.

## When AMP/AMG

- Use Prometheus / Grafana ecosystem
- Don't want to operate
- AWS-first observability

## When Self-Host

- Cost-sensitive at huge scale
- Customizations not in managed
- Existing on-prem stack

For most: managed.

## When CloudWatch

- AWS-only
- Native AWS integration
- Logs + metrics together
- Don't need PromQL

CloudWatch + native dashboards: simpler. AMP/AMG: standard Prometheus stack.

## ADOT (AWS Distro for OTel)

Collector compatible with Prometheus:
- Scrape via Prometheus receiver
- Send to AMP
- Plus traces to X-Ray

Single collector; many backends.

## Alerts

Grafana alerting (built-in) or Prometheus Alertmanager.

For AMP: separate Alertmanager pod or AWS Managed Service for Prometheus alerting (newer).

Or use AMG → alert → SNS → on-call.

## Migration

From self-hosted Prometheus to AMP:
1. Set up AMP workspace
2. Add remote_write in Prometheus config
3. Verify metrics arriving
4. Migrate Grafana to AMG
5. Decommission self-host

## EKS Specific

eksctl can install Prometheus + Grafana:
```bash
helm install prometheus prometheus-community/kube-prometheus-stack
```

For managed: just install Prometheus to scrape; remote_write to AMP.

## Retention

AMP: 150 days default.

For longer: export to S3 / data warehouse.

## Limits

- Workspaces per region
- Concurrent queries
- API rate limits

Standard AWS quotas; raisable.

## Performance

PromQL on huge data: can be slow. Use:
- Recording rules (pre-aggregate)
- Avoid range queries on millions
- Index labels carefully

## Cardinality

High-cardinality labels (user_id) → many series → cost.

Limit labels to bounded dimensions.

## Common Mistakes

- Self-hosting Prometheus when AMP cheaper
- High cardinality labels (cost / perf)
- No alerts (passive observation)
- AMG without SSO (security)

## Best Practices

- AMP for new K8s workloads
- AMG over installing Grafana
- ADOT collector for OTel
- SSO auth for AMG
- Recording rules
- Bounded labels

## Dashboards

Grafana JSON dashboards; versioned in Git.

Public dashboards (Grafana.com) for common services.

## Anti-Patterns

- One dashboard per team (siloed); use folders + tags
- No alerts on dashboards (passive)
- High-cardinality labels everywhere

## Integration with X-Ray

Grafana panels can show X-Ray traces.

For: end-to-end observability (metrics, logs, traces).

## OTel Stack

Full open-source observability:
- Metrics: Prometheus / AMP
- Logs: Loki
- Traces: Tempo / X-Ray
- Frontend: Grafana / AMG

Standard 2025+.

## Quick Refs

```bash
# AMP
aws amp create-workspace --alias my-prom
aws amp describe-workspace --workspace-id ws-xxx

# AMG
aws grafana create-workspace --workspace-name myGrafana ...
```

## Interview Prep

**Mid**: "When use Prometheus."

**Senior**: "AMP vs CloudWatch."

**Staff**: "Observability stack design."

## Next Topic

→ [T05 — CloudTrail for Audit](T05-CloudTrail.md)
