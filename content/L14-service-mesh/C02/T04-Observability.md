# L14/C02/T04 — Observability (Istio)

## Learning Objectives

- Get metrics, traces, logs from Istio
- Build dashboards

## What Istio Emits

### Metrics
- Request count
- Latency p50/p95/p99
- Error rate
- Per-service, per-version

### Logs
- Access logs (per request)
- Source / dest / status / bytes

### Traces
- Distributed trace headers propagated
- Spans emitted by sidecars

## Prometheus

```bash
istioctl install --set profile=demo
# Includes Prometheus by default in demo profile
```

Or:
```bash
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.x/samples/addons/prometheus.yaml
```

Sidecar exposes `/stats/prometheus`.

## Metrics

Standard:
```
istio_requests_total
istio_request_duration_milliseconds_bucket
istio_request_bytes_bucket
istio_response_bytes_bucket
```

Labels:
- `source_workload`
- `destination_workload`
- `response_code`
- `request_protocol`

## Sample Queries

```promql
# Total requests
sum(rate(istio_requests_total[5m])) by (destination_workload)

# Error rate
sum(rate(istio_requests_total{response_code=~"5.."}[5m])) / sum(rate(istio_requests_total[5m]))

# p99 latency
histogram_quantile(0.99, sum(rate(istio_request_duration_milliseconds_bucket[5m])) by (le, destination_workload))
```

## Grafana

```bash
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.x/samples/addons/grafana.yaml
```

Default dashboards:
- Mesh
- Service
- Workload
- Performance
- Control Plane

## Kiali

```bash
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.x/samples/addons/kiali.yaml
```

UI:
- Service graph
- Health
- Config validation
- Distributed traces (Jaeger embedded)

For: visualize mesh.

```bash
istioctl dashboard kiali
```

## Tracing

```bash
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.x/samples/addons/jaeger.yaml
```

Configure providers:
```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: mesh-default
  namespace: istio-system
spec:
  tracing:
  - providers:
    - name: jaeger
    randomSamplingPercentage: 100   # 100% for dev
```

For prod: 1-5%.

## Trace Propagation

Sidecar injects headers:
- `x-request-id`
- `x-b3-traceid`
- `x-b3-spanid`
- `x-b3-parentspanid`

App must forward (Istio can't transparently).

For: end-to-end traces.

## Access Logs

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: access-logs
  namespace: istio-system
spec:
  accessLogging:
  - providers:
    - name: envoy
```

Per-request stdout.

For: forensics.

## Custom Access Log Format

```yaml
spec:
  meshConfig:
    accessLogFormat: |
      [%START_TIME%] "%REQ(:METHOD)% %REQ(X-ENVOY-ORIGINAL-PATH?:PATH)%" %RESPONSE_CODE% %BYTES_SENT% %DURATION%
```

## Custom Metrics

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: namespace-metrics
spec:
  metrics:
  - providers:
    - name: prometheus
    overrides:
    - match:
        metric: REQUEST_COUNT
      tagOverrides:
        custom_tag:
          value: "request.headers['x-custom']"
```

For: custom labels.

## Disable Telemetry

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: disable-metrics
spec:
  selector:
    matchLabels:
      app: noisy-app
  metrics:
  - providers:
    - name: prometheus
      disabled: true
```

For: high-traffic services.

## Sampling

For traces:
```yaml
randomSamplingPercentage: 1.0   # 1%
```

Lower in prod. Targeted on specific apps higher.

## Workload Metrics

```yaml
istio_request_duration_milliseconds_bucket{
  source_workload="frontend",
  destination_workload="backend",
  response_code="200"
}
```

For: per-source/dest tracking.

## TCP Metrics

Beyond HTTP:
```
istio_tcp_received_bytes_total
istio_tcp_sent_bytes_total
istio_tcp_connections_opened_total
```

For: TCP services.

## Service Graph

Kiali derives from metrics:
- Service A → Service B (req/sec)
- Color = error rate
- Edge label = latency

For: visualize topology.

## Alerts

```yaml
- alert: HighErrorRate
  expr: |
    sum(rate(istio_requests_total{response_code=~"5.."}[5m])) by (destination_workload)
    /
    sum(rate(istio_requests_total[5m])) by (destination_workload)
    > 0.05
  for: 5m
  labels:
    severity: critical
```

## SLOs

For service A's SLO 99.9%:
```promql
1 - sum(rate(istio_requests_total{destination_workload="a", response_code=~"5.."}[28d])) / sum(rate(istio_requests_total{destination_workload="a"}[28d]))
```

For: SLO dashboards.

## Costs

Telemetry:
- Prometheus storage
- Jaeger storage
- Network (logs / traces)

For: tune sampling + retention.

## Best Practices

- Standard providers (Prometheus, Jaeger, Kiali)
- Sample traces (1-5% prod)
- Custom metrics sparingly
- Access logs targeted (not all)
- Alerts on RED metrics (Rate, Errors, Duration)
- Per-service dashboards
- SLO dashboards

## Common Mistakes

- 100% trace sampling (cost)
- Access logs on everything (cost)
- No alerts (blind)
- Default dashboards only (no insights)
- Don't forward trace headers (broken traces)

## Quick Refs

```bash
# Dashboards
istioctl dashboard kiali
istioctl dashboard grafana
istioctl dashboard jaeger

# Metrics endpoint
kubectl exec POD -c istio-proxy -- curl localhost:15020/stats/prometheus

# Sidecar status
istioctl proxy-status
```

## Interview Prep

**Mid**: "What Istio emits."

**Senior**: "Sampling strategy."

**Staff**: "Observability at scale."

## Next Topic

→ [T05 — Ambient Mode](T05-Ambient-Mode.md)
