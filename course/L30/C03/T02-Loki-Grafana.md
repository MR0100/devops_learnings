# L30/C03/T02 — Loki + Grafana

## Learning Objectives

- Build log pipeline
- Cost-effective

## Architecture

```
Pods → Promtail (DaemonSet) → Loki
                                ↓
                                S3
                                ↑
                              Grafana
```

## Install Loki

```bash
helm install loki grafana/loki-stack \
  --set loki.persistence.enabled=true \
  --set promtail.enabled=true
```

## Loki Config

```yaml
loki:
  storage:
    type: s3
    s3:
      endpoint: s3.amazonaws.com
      bucketName: loki-logs
      region: us-east-1
```

## Promtail

DaemonSet:
```yaml
clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: kubernetes-pods
    kubernetes_sd_configs:
      - role: pod
    relabel_configs: ...
```

## Grafana

Datasource: Loki.

LogQL:
```
{app="api"} |= "error"
{app="api", level="error"} | json | duration > 1000
```

## Multi-Tenant

```yaml
loki:
  config:
    auth_enabled: true
```

Headers:
```
X-Scope-OrgID: team-a
```

## Retention

```yaml
limits_config:
  retention_period: 30d
```

## Best Practices

- S3 backed
- Promtail auto-discovery
- Low cardinality labels
- Retention tuned

## Common Mistakes

- High cardinality labels
- No retention
- Local storage prod

## Quick Refs

```bash
helm install loki grafana/loki-stack
```

```
LogQL: {labels} |= "filter"
```

## Next Topic

→ [T03 — OTel Collector Fleet](T03-OTel-Collector.md)
