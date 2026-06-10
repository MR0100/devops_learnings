# L18/C07/T01 — Pyroscope / Grafana Profiles

## Learning Objectives

- Use Pyroscope
- Continuous profile

## Pyroscope

Continuous profiling (Grafana):
- CPU, memory, lock
- Flame graphs
- Diff comparisons

## Install

```bash
helm install pyroscope grafana/pyroscope
```

## App SDK

### Python
```python
import pyroscope
pyroscope.configure(
    application_name="my-app",
    server_address="http://pyroscope:4040",
    sample_rate=100,
    tags={"env": "prod"}
)
```

### Go
```go
import "github.com/grafana/pyroscope-go"

pyroscope.Start(pyroscope.Config{
    ApplicationName: "my-app",
    ServerAddress:   "http://pyroscope:4040",
})
```

### Java
Java agent injection.

### .NET, Ruby, Node, Rust
Similar SDKs.

## eBPF

```bash
helm install pyroscope grafana/pyroscope --set profiles.ebpf.enabled=true
```

Kernel-level profiling without app changes.

For: language-agnostic; minimal overhead.

## UI

http://pyroscope:4040

- Flame graphs
- Time series
- Diff views

## Flame Graph

```
Total CPU (100%)
├─ main (5%)
├─ handle_request (60%)
│  ├─ parse (10%)
│  ├─ db_query (40%) ← hot
│  └─ response (10%)
└─ background (35%)
```

Wide = hot. Optimize there.

## Sampling

Default ~100 Hz:
- 100 stack samples/sec
- Low overhead (~1%)

## Continuous

Always-on:
- Aggregate over time
- Per-service
- Compare versions

## Profile Types

- CPU
- Memory (allocations)
- Goroutines (Go)
- Lock contention
- I/O wait

## Diff

Compare two periods:
- Before vs after deploy
- Stable vs canary
- Healthy vs slow

Shows what changed.

## Tags

```python
pyroscope.tag_wrapper({"endpoint": "/api/users"})
```

Per-tag flame graphs.

For: per-context analysis.

## Grafana Integration

Datasource: Pyroscope.

Panel: Flame graph.

Plus: correlate with traces/logs.

## Architecture

```
App → Pyroscope SDK → Pyroscope Server → Storage (S3 / local)
        ↑
        eBPF agent
```

## Storage

S3 / object storage:
- Cheap
- Long retention

## Cost

Low:
- Cheap storage
- Low compute
- ~1% app overhead

## Use Cases

### Optimization
Find hot paths.

### Memory Leak
Allocations growing.

### Lock Contention
Threads waiting.

### Cold Start
Lambda; reduce.

### Regression
Compare deploys.

## Polar Signals / Parca

Similar; pure eBPF.

```bash
helm install parca parca/parca
```

For: kernel-level only.

## Datadog Profiler

Datadog's commercial:
- Java, Python, etc.
- Continuous
- Integrated with APM

## Alternatives

- Pyroscope (Grafana; OSS)
- Parca (Polar Signals)
- Datadog Continuous Profiler
- New Relic CodeStream
- Google Cloud Profiler

## When Continuous Profiling

- Production
- Performance critical
- Always-on debug

## When Spot Profiling

- Ad-hoc (`go tool pprof`)
- One-off issues

For: best is continuous.

## Adopt Gradually

1. Install Pyroscope
2. Add SDK to one service
3. View flame graphs
4. Identify wins
5. Expand

## Best Practices

- Always-on (low overhead)
- Tag richly
- Compare versions
- Combine with metrics + traces
- Set retention

## Common Mistakes

- High sample rate (overhead)
- Profile in test (different)
- Ignore flame graphs (no action)

## Quick Refs

```python
# Python
pyroscope.configure(
    application_name="X",
    server_address="...",
    sample_rate=100
)

pyroscope.tag_wrapper({"k": "v"})
```

```go
pyroscope.Start(pyroscope.Config{...})
```

## Interview Prep

**Mid**: "Continuous profiling."

**Senior**: "Pyroscope workflow."

**Staff**: "Profiling at scale."

## Next Topic

→ [T02 — Continuous Profiling Patterns](T02-Profiling-Patterns.md)
