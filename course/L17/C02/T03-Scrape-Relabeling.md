# L17/C02/T03 — Scrape Configs & Relabeling

## Learning Objectives

- Configure scrapes
- Use relabel rules

## Scrape Config

```yaml
scrape_configs:
  - job_name: 'api'
    scrape_interval: 15s
    scrape_timeout: 10s
    metrics_path: /metrics
    scheme: http
    basic_auth:
      username: prom
      password: pass
    bearer_token: TOKEN
    static_configs:
      - targets: ['api:8080']
        labels:
          env: prod
```

## Override Defaults

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'noisy'
    scrape_interval: 60s   # less often for this job
```

## Honor Labels

```yaml
honor_labels: true
honor_timestamps: true
```

For: federation.

## Bearer Token

```yaml
bearer_token_file: /var/run/secrets/.../token
```

For: K8s SA.

## TLS

```yaml
tls_config:
  ca_file: /etc/prometheus/ca.crt
  cert_file: /etc/prometheus/cert.crt
  key_file: /etc/prometheus/cert.key
  insecure_skip_verify: false
```

## Relabel Configs

Two types:
- `relabel_configs`: before scrape (target labels)
- `metric_relabel_configs`: after scrape (per-metric)

## Relabel Actions

### keep
```yaml
- source_labels: [__meta_kubernetes_pod_annotation_prom_scrape]
  regex: 'true'
  action: keep
```

Drop if no match.

### drop
```yaml
- source_labels: [__meta_kubernetes_namespace]
  regex: kube-system
  action: drop
```

Drop kube-system pods.

### replace
```yaml
- source_labels: [__meta_kubernetes_pod_name]
  target_label: pod
```

Set pod label.

### labelmap
```yaml
- regex: __meta_kubernetes_pod_label_(.+)
  action: labelmap
```

Copy pod labels as series labels.

### hashmod
```yaml
- source_labels: [__address__]
  modulus: 4
  target_label: __tmp_shard
  action: hashmod
- source_labels: [__tmp_shard]
  regex: '^0$'
  action: keep
```

Shard targets.

### labelkeep / labeldrop
```yaml
- regex: 'instance_.*'
  action: labeldrop
```

Drop labels matching pattern.

## metric_relabel_configs

After scrape:
```yaml
metric_relabel_configs:
  - source_labels: [__name__]
    regex: 'go_.*'
    action: drop
```

Drop go runtime metrics.

```yaml
- source_labels: [route]
  regex: '/api/.*'
  target_label: route
  replacement: '/api/...'
```

Rewrite high-cardinality.

## Cardinality Control

```yaml
metric_relabel_configs:
  - source_labels: [user_id]
    action: labeldrop
```

Strip user_id from metrics (high cardinality).

## Address Munging

```yaml
- source_labels: [__address__]
  regex: '([^:]+):.*'
  replacement: '${1}:9100'
  target_label: __address__
```

Force port to 9100.

## Common K8s Relabel

```yaml
relabel_configs:
  # Only annotated pods
  - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
    regex: true
    action: keep

  # Use annotation for path
  - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
    regex: (.+)
    target_label: __metrics_path__
    replacement: $1

  # Use annotation for port
  - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
    regex: '([^:]+)(?::\d+)?;(\d+)'
    target_label: __address__
    replacement: ${1}:${2}

  # Labels from pod metadata
  - source_labels: [__meta_kubernetes_namespace]
    target_label: namespace
  - source_labels: [__meta_kubernetes_pod_name]
    target_label: pod
```

## Filter by Label

```yaml
- source_labels: [environment]
  regex: 'prod|staging'
  action: keep
```

Scrape only prod/staging.

## Debugging

```bash
# Targets
GET /api/v1/targets

# Active config
GET /api/v1/status/config

# Reload
POST /-/reload
```

## Common Patterns

### Add cluster label
```yaml
- target_label: cluster
  replacement: 'us-east-1'
```

### Sanitize labels
```yaml
- source_labels: [__address__]
  regex: '(.+):.*'
  target_label: instance
  replacement: '$1'
```

### Drop sensitive
```yaml
- regex: '(password|secret|token)'
  action: labeldrop
```

## metric_relabel for Cardinality

```yaml
metric_relabel_configs:
  # Drop noisy metrics
  - source_labels: [__name__]
    regex: 'noisy_metric_.*'
    action: drop

  # Drop high cardinality labels
  - regex: '(user_id|session_id|request_id)'
    action: labeldrop

  # Bucket by status code class
  - source_labels: [status_code]
    regex: '(2..)'
    target_label: status_class
    replacement: '2xx'
```

## Best Practices

- Drop unused metrics (cardinality)
- Add cluster/env labels
- Use labelmap for K8s
- Filter by annotation (opt-in)
- Sample where unavoidable

## Common Mistakes

- No filter (scrape everything)
- High-cardinality labels kept
- Wrong regex syntax
- No reload after change

## Quick Refs

```yaml
relabel_configs:
  - source_labels: [LABEL]
    regex: PATTERN
    action: keep | drop | replace | labelmap | labelkeep | labeldrop | hashmod
    target_label: NEW_LABEL
    replacement: VALUE

metric_relabel_configs:
  # After scrape
```

## Interview Prep

**Mid**: "Relabel configs."

**Senior**: "Cardinality control."

**Staff**: "Prometheus optimization."

## Next Topic

→ [T04 — Storage (TSDB, WAL)](T04-Storage.md)
