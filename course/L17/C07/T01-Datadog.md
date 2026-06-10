# L17/C07/T01 — Datadog

## Learning Objectives

- Use Datadog
- Compare to OSS

## Datadog

Commercial APM:
- Metrics, logs, traces, RUM, synthetics
- Massive ecosystem
- Strong UI
- Expensive

## Install Agent

```bash
DD_API_KEY=KEY DD_SITE=datadoghq.com \
  bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script.sh)"
```

Or K8s:
```bash
helm install datadog datadog/datadog \
  --set datadog.apiKey=KEY \
  --set datadog.site=datadoghq.com
```

## Features

### APM
- Auto-instrumented
- Service maps
- Distributed tracing
- Profiling

### Infrastructure
- Host metrics
- Container metrics
- Network maps

### Logs
- Live tail
- LogQL-like search
- Patterns

### RUM
- Browser performance
- User journeys
- Errors

### Synthetics
- API tests
- Browser tests
- Scheduled

### Security
- CloudSIEM
- App security

## Cost

Per host / per GB ingested:
- Infra: $15+/host/mo
- APM: $31+/host/mo
- Logs: $0.10+/GB ingested
- More for retention

For: significant at scale.

## Custom Metrics

Limit per host. Overage charges.

## Integration

500+ integrations:
- AWS (CloudWatch)
- Azure
- GCP
- K8s
- Postgres, MySQL, etc.

Click to enable.

## Tags

```python
@datadog.statsd.timed("my.metric")
def func():
    ...
```

Tags applied automatically.

## Dashboards

- Drag-and-drop
- Widgets
- Templates
- Notebook (analysis)

## Monitors

= Alerts:
- Threshold
- Anomaly
- Outlier
- Composite

Sent to:
- PagerDuty
- Slack
- Email
- Webhook

## Service Map

Auto-generated from traces:
- Services
- Dependencies
- Health per service

## Trace Search

- By trace_id
- By tag
- By duration
- By error

## Profile

Continuous profiling:
- CPU
- Allocation
- Lock

Per service; flame graphs.

## Watchdog

ML-driven anomaly detection:
- Sudden change
- Unusual pattern

Auto-incidents.

## Notebooks

Investigation:
- Multi-panel
- Cross-source (metric + log + trace)
- Shareable

For: incident investigations.

## API

```bash
curl -X POST "https://api.datadoghq.com/api/v1/series" \
  -H "DD-API-KEY: $KEY" \
  -d '{
    "series": [{
      "metric": "my.app.metric",
      "points": [[1700000000, 42]],
      "tags": ["env:prod"]
    }]
  }'
```

## Terraform

```hcl
resource "datadog_monitor" "high_cpu" {
  name = "High CPU"
  type = "metric alert"
  query = "avg(last_5m):avg:system.cpu.user > 80"
  message = "CPU high; @pagerduty"
}
```

For: monitors as code.

## OTel Compatibility

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp.us3.datadoghq.com
```

Datadog accepts OTLP.

For: vendor-neutral SDK + Datadog backend.

## Pros

- Unified platform
- Great UI
- Rich features
- Easy onboarding
- Strong support

## Cons

- Cost
- Vendor lock-in (if using DD SDK)
- Cardinality limits
- Complex pricing

## When Datadog

- Want hands-off
- Budget allows
- Polyglot
- Speed > cost

## When Not

- Cost-sensitive
- Strong OSS team
- Compliance requires self-host
- High-volume metrics

## Reduce Cost

- Sample logs (1-10%)
- Don't index unnecessary
- Custom metrics limited
- Use traces, not logs for everything

## Compared to OSS

| | Datadog | OSS LGTM |
|---|---|---|
| Setup | minutes | weeks |
| Cost | $$$ | infra + ops |
| Features | broad | growing |
| UI | polished | functional |
| Ops | none | full |

## Best Practices

- Use OTel (portable)
- Tag standardization
- Service catalog
- Sample / drop unused
- Custom metric budget
- Cost monitor (DD usage)

## Common Mistakes

- All logs indexed (expensive)
- Custom metrics sprawl
- Long retention everywhere
- No cost monitoring

## Real Use

- Most cloud-native companies use DD or similar
- Tradeoff per company

## Quick Refs

```bash
# Agent install
bash <(curl install_script.sh)

# K8s
helm install datadog datadog/datadog

# Send metric
echo "my.metric:1|c|#env:prod" | nc -u -w0 datadog-agent 8125

# API
DD_API_KEY + endpoint
```

## Interview Prep

**Junior**: "What's Datadog."

**Mid**: "DD vs OSS."

**Senior**: "DD cost."

**Staff**: "Observability vendor choice."

## Next Topic

→ [T02 — New Relic](T02-New-Relic.md)
