# L17/C02/T02 — Service Discovery

## Learning Objectives

- Configure SD for Prometheus
- Dynamic targets

## Why SD

Cloud: dynamic targets.
- VMs scale
- K8s pods churn
- IPs change

Static config: stale.

## K8s SD

```yaml
scrape_configs:
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
```

Roles:
- pod
- service
- endpoints
- node
- ingress

## Relabel for K8s

```yaml
relabel_configs:
  # Only scrape pods with annotation
  - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
    action: keep
    regex: true

  # Read port from annotation
  - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_port]
    action: replace
    target_label: __address__
    regex: (.+)
    replacement: $1

  # Set namespace label
  - source_labels: [__meta_kubernetes_namespace]
    action: replace
    target_label: namespace
```

For: app opts-in via annotation.

## Pod Annotation

```yaml
metadata:
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
    prometheus.io/path: "/metrics"
```

## ServiceMonitor (Prometheus Operator)

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: my-app
spec:
  selector:
    matchLabels:
      app: my-app
  endpoints:
    - port: metrics
      interval: 30s
```

Operator auto-configs Prometheus.

For: K8s native.

## PodMonitor

Pods without Service:
```yaml
kind: PodMonitor
spec:
  selector:
    matchLabels: ...
  podMetricsEndpoints:
    - port: metrics
```

## Consul SD

```yaml
scrape_configs:
  - job_name: 'consul'
    consul_sd_configs:
      - server: 'consul:8500'
        services: ['api', 'worker']
```

For: VM environments.

## EC2 SD

```yaml
- job_name: 'ec2'
  ec2_sd_configs:
    - region: us-east-1
      filters:
        - name: tag:Monitoring
          values: ['true']
  relabel_configs:
    - source_labels: [__meta_ec2_tag_Name]
      target_label: instance_name
```

## GCE SD

```yaml
- job_name: 'gce'
  gce_sd_configs:
    - project: my-project
      zone: us-central1-a
```

## Azure SD

```yaml
- job_name: 'azure'
  azure_sd_configs:
    - subscription_id: ...
```

## DNS SD

```yaml
- job_name: 'dns'
  dns_sd_configs:
    - names: ['_prometheus._tcp.example.com']
      type: 'SRV'
```

For: SRV records.

## File SD

```yaml
- job_name: 'file'
  file_sd_configs:
    - files: ['/etc/prometheus/targets/*.json']
      refresh_interval: 30s
```

```json
[
  {"targets": ["10.0.0.1:9100", "10.0.0.2:9100"], "labels": {"env": "prod"}}
]
```

For: external script generates list.

## HTTP SD

```yaml
- job_name: 'http'
  http_sd_configs:
    - url: 'https://my-discovery/api/v1/targets'
```

For: API-driven discovery.

## Multi-SD

```yaml
- job_name: 'mixed'
  kubernetes_sd_configs: [...]
  consul_sd_configs: [...]
```

Combines.

## Relabel Actions

- `keep`: only matching
- `drop`: drop matching
- `replace`: set label
- `labelmap`: map by regex
- `hashmod`: shard by hash

## Sharding

```yaml
relabel_configs:
  - source_labels: [__address__]
    modulus: 4
    target_label: __tmp_hash
    action: hashmod
  - source_labels: [__tmp_hash]
    regex: ^0$    # this Prom = shard 0
    action: keep
```

4 Proms, each scrapes 1/4.

For: scale via sharding.

## Honor Labels

```yaml
honor_labels: true
```

Target's labels win over Prom's.

For: federation.

## Job Names

```yaml
- job_name: 'api'
```

Default `job` label.

Override via relabel:
```yaml
- target_label: job
  replacement: my-job
```

## Best Practices

- K8s: ServiceMonitor / PodMonitor (Operator)
- Cloud: native SD
- Multi-SD when needed
- Sharding for scale
- Tag with cluster/env/team

## Common Mistakes

- Static targets in cloud
- No relabel (wrong labels)
- Scrape too often (load)
- No keep filter (everything scraped)

## Operator vs Manual

Prometheus Operator:
- ServiceMonitor / PodMonitor
- Auto-generated config
- K8s-native

Manual:
- Full control
- Direct prometheus.yml
- Less abstraction

For K8s: Operator usually.

## Quick Refs

```yaml
# K8s SD
kubernetes_sd_configs:
  - role: pod | service | endpoints | node

# EC2
ec2_sd_configs:

# Consul
consul_sd_configs:

# Operator (ServiceMonitor)
spec:
  selector: {...}
  endpoints: [...]
```

## Interview Prep

**Mid**: "Service discovery."

**Senior**: "K8s SD."

**Staff**: "Discovery at scale."

## Next Topic

→ [T03 — Scrape Configs & Relabeling](T03-Scrape-Relabeling.md)
