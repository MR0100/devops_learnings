# L17/C01/T02 — Profiles as the 4th Pillar

## Learning Objectives

- Use continuous profiling
- Find performance bottlenecks

## Profiling

Sample call stacks; understand what code does:
- CPU profiling: what consumed CPU
- Memory: allocations
- Lock: contention
- I/O: wait time

## Why 4th Pillar

Metrics: aggregate.
Logs: events.
Traces: cross-service.
Profiles: in-code detail.

For: pinpoint code lines.

## Continuous Profiling

Always-on; low overhead:
- 100s of samples/sec
- Per-process
- Aggregated

Tools:
- Pyroscope (Grafana)
- Datadog Continuous Profiler
- Polar Signals
- Cloud Profiler (GCP)

## Pyroscope

```yaml
# K8s daemon
helm install pyroscope pyroscope-io/pyroscope
```

App:
```python
import pyroscope

pyroscope.configure(
    application_name="my-app",
    server_address="http://pyroscope:4040",
)
```

UI shows flame graphs.

## Flame Graph

```
Total CPU
├─ main (10%)
├─ handle_request (40%)
│  ├─ parse (5%)
│  ├─ db_query (30%)  ← bottleneck
│  └─ render (5%)
└─ background (50%)
```

Visual: width = time.

## Differential Profile

Compare:
- Before deploy vs after
- Slow vs fast endpoints
- Production vs canary

Shows what changed.

## eBPF Profiling

Kernel-level; no app changes:
```bash
parca   # eBPF profiler
```

Profile any process; system-wide.

For: language-agnostic; minimal overhead.

## Use Cases

### Find Bottleneck
40% CPU in regex parse? Replace.

### Memory Leak
Allocations growing in function X.

### Lock Contention
Threads waiting on mutex.

### Optimization Validation
Optimization changed hot path?

## Sampling

100 Hz typical:
- Captures most hot paths
- Low overhead (~1%)

## Tools

### pprof (Go)
```go
import _ "net/http/pprof"
http.ListenAndServe("localhost:6060", nil)

// Get profile:
go tool pprof http://localhost:6060/debug/pprof/profile
```

### py-spy (Python)
```bash
py-spy record --output profile.svg -- python myapp.py
py-spy top --pid 1234
```

### perf (Linux)
```bash
perf record -F 99 -g -p PID -- sleep 30
perf script | flamegraph > flame.svg
```

### Java
Java Flight Recorder, async-profiler.

### Node.js
```bash
node --prof app.js
node --prof-process isolate-*.log
```

### Rust
- perf
- flamegraph crate

## Cloud Profiler (GCP)

```python
import googlecloudprofiler

googlecloudprofiler.start(
    service='my-service',
    service_version='1.0.0',
)
```

For: hands-off, GCP.

## Datadog Profiler

```python
from ddtrace.profiling import Profiler

Profiler().start()
```

Integrated with APM.

## Polar Signals (Parca)

eBPF-based; open source:
- Linux
- No app instrumentation
- Continuous

## Read Flame Graph

- Wide = expensive
- Bottom = main / runtime
- Top = leaves (where time spent)
- Color: random / by language

Tools render interactive.

## Aggregate Profiles

Sum over time / fleet:
- All hosts, last 1 hr
- Compare: stable vs canary

For: trends.

## Best Practices

- Continuous (not on-demand)
- Sample low rate (1-100 Hz)
- Differential comparisons
- Per-service rollups
- Combine with metrics
- Don't profile prod high-load without test

## Common Mistakes

- Profile in test (different)
- High sample rate (overhead)
- Single profile (no comparison)
- Skip metrics (no overall context)

## Combined with Traces

Trace shows slow span:
- Click → flame graph for that span
- See exactly what code

For: deep dive.

## Memory Profiling

```bash
go tool pprof -alloc_space http://localhost:6060/debug/pprof/heap
```

For: allocation patterns, leaks.

## Lock Profiling

```go
import "runtime"
runtime.SetBlockProfileRate(1)
```

Find contention.

## Wire-Level Tools

### tcpdump
Capture; analyze with Wireshark.

For: protocol issues.

## When Profiling Helps Vs Tracing

Profiling: where time spent in code.
Tracing: where time spent across services.

For different problems.

## Real Examples

### Twitter
Massive profiling infra.

### Cloudflare
eBPF profiling at edge.

### Many companies
Cloud Profiler / Datadog.

## Best Practices Recap

- Continuous in prod (low overhead)
- Differential vs baseline
- Combine with metrics + traces
- Per-service per-version

## Quick Refs

```
Pyroscope: pyroscope-io/pyroscope
Parca:     parca-dev/parca
pprof:     go tool pprof URL
py-spy:    py-spy record
perf:      perf record -F 99
```

## Interview Prep

**Mid**: "What's continuous profiling."

**Senior**: "Profiling workflow."

**Staff**: "Profiling at scale."

## Next Topic

→ [T03 — Continuous Observability](T03-Continuous-Observability.md)
