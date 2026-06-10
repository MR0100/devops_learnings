# L18/C07/T02 — Continuous Profiling Patterns

## Learning Objectives

- Apply profiling patterns
- Find bottlenecks

## Patterns

### Diff Compare
Before vs after change.

### Outlier Investigation
Slow endpoint: profile only those requests.

### Resource Saturation
Memory leak: profile heap over time.

### Cold Start
Lambda init phase.

### Lock Contention
Find waiting threads.

## Profile Per Endpoint

```python
pyroscope.tag_wrapper({"endpoint": "/api/users"})
# Profile this only attributed to /api/users
```

For: per-route flames.

## Tagged Profiling

Tag richly:
```python
pyroscope.tag_wrapper({
    "endpoint": "/api/users",
    "tenant": tenant_id,
    "version": "1.0.0"
})
```

Filter / group by tags.

## Diff Workflow

1. Baseline (stable version)
2. Deploy change
3. Diff in Pyroscope
4. See if hot paths shifted

For: performance regression detection.

## Per-Version

```python
pyroscope.configure(tags={"version": "1.0.0"})
```

```python
pyroscope.configure(tags={"version": "1.0.1"})
```

Compare.

## Memory Profiling

Heap allocations:
```go
runtime.SetMutexProfileFraction(1)
```

Find:
- Allocating functions
- Memory growth
- GC pressure

## Optimization Loop

```
1. Profile → identify hot path
2. Optimize that
3. Measure improvement
4. Repeat
```

For: data-driven optimization.

## Don't Premature Optimize

Without profile: guesswork.
With profile: known target.

## Latency Profiling

For slow endpoint:
- Profile during slow
- Find blocking calls
- Optimize

Tools:
- Pyroscope by tag
- pprof on demand
- async-profiler (Java)

## Cold Start (Lambda)

Lambda init expensive:
- Profile cold start
- Identify slow init
- Lazy load
- SnapStart (Lambda)

For: cold start <100ms goal.

## eBPF Cross-Process

eBPF profiling:
- All processes
- Single view
- No app changes

```bash
sudo parca-agent
```

Or Pyroscope eBPF mode.

For: system-wide.

## Lock Contention

Go:
```go
import _ "net/http/pprof"
go func() {
    runtime.SetBlockProfileRate(1)
    runtime.SetMutexProfileFraction(1)
}()
```

`/debug/pprof/mutex` shows contention.

## Comparing Profiles

Pyroscope diff:
- Red: faster (less time)
- Green: slower (more time)

Quickly find what changed.

## Differential Flame Graph

Each box: difference between two profiles.

For: highlight differences.

## Profile on Anomaly

Auto-trigger:
- Alert fires
- Profile recorded
- Attached to incident

Tools: integrate Pyroscope with alerts.

## Profile in CI

Baseline in CI:
```yaml
- name: Performance test
  run: |
    pyroscope-cli connect &
    ./perf-test
- name: Compare
  run: pyroscope-cli diff baseline current
```

Fail if regression.

For: prevent regression.

## Cardinality

Profile data ≠ metric:
- Less cardinality concern
- Tag freely

For: rich profiles.

## Storage

S3-backed:
- Cheap
- Long retention
- Compare months apart

## Profile Specific Spans

Link profile to trace:
- Span: db_query
- Profile during span: shows DB driver work

For: targeted.

## Memory Leak Pattern

```
Heap over time:
  100 MB → 150 MB → 200 MB → 250 MB

Pattern: continuous growth = leak
```

Profile heap; find retainer.

## CPU Hot Path

```
Function:
  parse_url: 30%
  serialize_json: 20%
  db_call: 50%
```

Optimize top.

## Anti-Patterns

### Over-Profiling
Sample too often → overhead.

### No Tags
All in one bucket; can't filter.

### Profile Without Action
View; never optimize.

### Profile Test Env
Different from prod.

## Tools per Language

- Go: pprof + Pyroscope SDK
- Java: async-profiler, JFR
- Python: py-spy, Pyroscope
- Node: clinic.js, Pyroscope
- Rust: cargo flamegraph
- Ruby: rbspy

## Production-Safe

100 Hz sampling:
- ~1% overhead
- Safe in prod

Higher rates: only when needed.

## Distributed Profiling

Across pods:
- Aggregate flame graph
- Per-deployment view

For: fleet-wide.

## Best Practices

- Continuous (always-on)
- Tag richly
- Diff for regressions
- Combine with metrics/traces
- Periodic review

## Common Mistakes

- One-off profiling (miss trends)
- No tags
- Wrong env
- No follow-through

## Quick Refs

```
Diff:        before vs after
Tagged:      per endpoint / tenant / version
Memory:      heap allocations
Lock:        contention
eBPF:        kernel-level
```

## Interview Prep

**Mid**: "Profiling patterns."

**Senior**: "Find bottlenecks."

**Staff**: "Profiling strategy."

## Next Topic

→ Move to [L18/C08 — Correlating Logs, Metrics, Traces](../C08/README.md)
