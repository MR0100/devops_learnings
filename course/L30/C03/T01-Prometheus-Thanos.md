# L30/C03/T01 — Prometheus + Thanos

## Learning Objectives

- Build long-term metrics
- Thanos setup

## Architecture

```
Per-cluster:
- Prometheus + Thanos Sidecar
       ↓
       S3

Global:
- Thanos Store (reads S3)
- Thanos Querier (federates Sidecars + Store)
- Thanos Compactor (downsampling)
```

## Install Prometheus

```bash
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack
```

## Thanos Sidecar

```yaml
prometheus:
  prometheusSpec:
    thanos:
      objectStorageConfig:
        existingSecret:
          name: thanos-secret
          key: thanos.yaml
```

```yaml
# thanos.yaml
type: S3
config:
  bucket: thanos-metrics
  endpoint: s3.amazonaws.com
  region: us-east-1
```

## Thanos Components

```bash
helm install thanos bitnami/thanos
```

Configure:
- Store
- Querier
- Compactor

## Federation

Querier addresses Sidecars + Store:
```yaml
query:
  stores:
    - thanos-sidecar.cluster-1:10901
    - thanos-sidecar.cluster-2:10901
    - thanos-store-gateway:10901
```

## Retention

```yaml
compactor:
  retention:
    raw: 30d
    5m: 90d
    1h: 1y
```

Downsampling for long retention.

## Grafana

Datasource: Thanos Querier.

Queries: PromQL same.

## Multi-Cluster

Each cluster: Prometheus + Sidecar.
Central: Querier + Store.

For: global view.

## Best Practices

- S3 backed
- Compaction
- Multi-region S3 replication
- HA Querier

## Common Mistakes

- No object storage
- No compaction
- Single Querier (SPOF)

## Quick Refs

```bash
helm install kube-prometheus-stack ...
helm install thanos ...

# Sidecar to S3
# Querier + Store + Compactor
```

## Next Topic

→ [T02 — Loki + Grafana](T02-Loki-Grafana.md)
