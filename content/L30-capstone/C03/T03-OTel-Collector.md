# L30/C03/T03 — OTel Collector Fleet

## Learning Objectives

- Deploy OTel
- Unified pipeline

## Why the Agent + Gateway Pattern

The OTel Collector is the **vendor-neutral seam** of the whole stack: apps speak
OTLP to the Collector, and the Collector decides where signals go. Swap Loki for
Elastic, or Tempo for Jaeger, by editing collector config — the apps never
change. That decoupling is the senior selling point of this capstone.

The two tiers exist because they do different jobs:

- **Agent (DaemonSet, per node)** — local, cheap collection: receive OTLP from
  apps on the same node, scrape node logs, add k8s attributes, batch. Being
  node-local keeps the network hop short and adds pod/node metadata only the
  node knows.
- **Gateway (Deployment, cluster tier)** — the place for *stateful, whole-trace*
  processing: **tail sampling** (needs all spans of a trace, so it can't live on
  per-node agents), enrichment, and fan-out to the backends. Centralizing it
  also means one place to manage backend credentials and routing.

### Trade-offs

- **Agent+Gateway vs app-direct-to-backend** — the extra tier costs latency and
  resources but buys buffering (apps don't block on backend outages), a single
  control point, and tail sampling. Direct-to-backend is simpler but couples
  every app to every backend's availability and address.
- **`memory_limiter` is mandatory** — without it a backend slowdown backs up
  data in the Collector and OOM-kills it, dropping everything.

## Topology

```
Apps → OTel Agent (DaemonSet) → OTel Gateway (Deployment)
                                       ↓
                          Mimir / Loki / Tempo
```

## Agent

Per-node:
```yaml
receivers:
  otlp:
    protocols:
      grpc:
      http:
  filelog:
    include: [/var/log/containers/*.log]

processors:
  batch:
  memory_limiter:
  k8sattributes:

exporters:
  otlp:
    endpoint: otel-gateway:4317

service:
  pipelines:
    traces: { receivers: [otlp], processors: [batch], exporters: [otlp] }
    metrics: { receivers: [otlp], processors: [batch], exporters: [otlp] }
    logs: { receivers: [filelog], processors: [batch], exporters: [otlp] }
```

## Gateway

Central:
```yaml
receivers:
  otlp: ...

processors:
  batch:
  tail_sampling:
    policies:
      - name: errors
        type: status_code
        status_code: { status_codes: [ERROR] }
      - name: sample
        type: probabilistic
        probabilistic: { sampling_percentage: 10 }

exporters:
  prometheus: { endpoint: 0.0.0.0:8889 }
  loki: { endpoint: http://loki:3100/loki/api/v1/push }
  otlp/tempo: { endpoint: tempo:4317 }
```

## App Instrumentation

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-agent:4317
OTEL_SERVICE_NAME=my-app
```

## Auto-Instrumentation

```bash
opentelemetry-instrument python app.py
```

## Multi-Cluster

Per cluster: agent + gateway.
Central observability: receive from all gateways.

## Best Practices

- Agent + Gateway pattern
- Tail sampling
- Resource attributes
- Multi-backend exporters

## Common Mistakes

- Direct to backend (no buffer)
- 100% sample (cost)
- No memory limiter (OOM)

## Acceptance Criteria

- Apps send OTLP to the node-local agent; agent forwards to the gateway
- Tail sampling in the gateway keeps all error and slow traces plus a baseline
  sample of the rest
- `memory_limiter` is set on both tiers (kill a backend, confirm the Collector
  back-pressures instead of OOMing)
- Switching a backend (e.g. Loki endpoint) requires only collector config, no
  app change — demonstrates the vendor-neutral seam

## Quick Refs

```yaml
receivers / processors / exporters / service   # the 4 config blocks
```
```
Agent (DaemonSet): collect + k8sattributes + batch, node-local
Gateway (Deployment): tail_sampling (needs whole trace) + fan-out
memory_limiter always on. Tail-sample in the gateway, not the agent.
```

## Interview Prep

**Junior**: "What does the OTel Collector do?" — It receives telemetry (metrics,
logs, traces) from applications in a standard format (OTLP), processes it, and
exports it to backends like Prometheus, Loki, and Tempo. Apps only need to know
about the Collector, not each backend.

**Mid**: "Why run an agent and a gateway tier instead of sending straight to the
backend?" — The agent runs per node for cheap local collection and adds
Kubernetes metadata. The gateway is a central tier that buffers data (so apps
don't fail when a backend is down), gives one place to manage routing and
credentials, and does tail sampling — which has to be centralized because it
needs all spans of a trace to decide whether to keep it. Sending apps directly
to backends couples every app to every backend's address and uptime.

**Senior**: "Why must tail sampling live in the gateway, and what breaks if you
get it wrong?" — Tail sampling decides keep/drop *after* seeing the whole trace,
so it can preserve every error and high-latency trace and only drop the boring
happy path. That requires all spans of a trace to land on the same collector
instance — so it goes in the centralized gateway, often with a load-balancing
exporter in front to route spans of a trace to the same gateway replica. If you
sampled on the per-node agents, each node only sees its slice of the trace and
you'd get broken, half-sampled traces. And without `memory_limiter`, a backend
slowdown backs data up until the Collector OOMs and drops everything — so you
lose telemetry exactly when you need it most, during an incident.

**Staff**: "How does the Collector fit a platform strategy across many teams and
maybe multiple clusters/clouds?" — The Collector is the abstraction layer that
lets the platform own *where telemetry goes* while teams own *what they emit*.
Standardizing on OTLP in the golden-path service template means every new
service is correlated-by-default and the platform can re-route, re-sample, or
swap a backend fleet-wide without touching app code — that's a migration
(Jaeger→Tempo, self-hosted→vendor) that becomes a config change instead of a
hundred PRs. Across clusters/clouds you run the agent+gateway per cluster and
have gateways forward to a central tier, keeping egress and sampling decisions in
one controllable place. The strategic value is optionality: you're never locked
to a backend vendor, and cost levers (sampling rates, what you drop) are
centralized policy rather than scattered per team.

## Next Topic

→ [T04 — Tempo + Trace Correlation](T04-Tempo-Trace-Correlation.md)
