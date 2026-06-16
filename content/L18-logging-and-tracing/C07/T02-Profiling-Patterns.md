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

This attributes the enclosed work to a specific route, so you get a per-route flame graph instead of one blended profile for the whole service.

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

This workflow is how you detect a performance regression: if the diff shows a frame that grew after the change, the new code made that path hotter.

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

Iterating this loop keeps optimization data-driven: each pass targets the current hottest path and verifies the gain before moving on.

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

Profiling the init phase tells you which slow imports or eager work to defer, which is how you drive cold start under the ~100 ms goal.

## eBPF Cross-Process

eBPF profiling:
- All processes
- Single view
- No app changes

```bash
sudo parca-agent
```

Or Pyroscope eBPF mode.

Because eBPF profiles at the kernel level, you get a single system-wide view across every process on the host without instrumenting any of them.

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

Each box represents the difference between two profiles, so the graph highlights exactly which frames got hotter or colder between the two runs instead of making you compare them by eye.

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

Failing the build when the diff shows a regression prevents slow code from shipping in the first place, catching it in CI rather than in production.

## Cardinality

Profile data ≠ metric:
- Less cardinality concern
- Tag freely

Because profile storage doesn't suffer the cardinality blowup that metric labels do, you can tag profiles richly to get fine-grained, filterable views.

## Storage

S3-backed:
- Cheap
- Long retention
- Compare months apart

## Profile Specific Spans

Link profile to trace:
- Span: db_query
- Profile during span: shows DB driver work

Linking a profile to a specific span gives you targeted analysis: you see exactly which code ran during that slow database call rather than averaging across the whole service.

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

Aggregating profiles across pods gives a fleet-wide flame graph, so you can spot a hot path that's expensive in aggregate even if no single instance stands out.

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

**Junior**: "Why profile instead of guessing where to optimize?" — A profile shows you the actual hot path from real execution, so you optimize the code that dominates CPU or memory rather than spending effort on a function that turns out to be cheap.

**Mid**: "Name a few continuous-profiling patterns." — Diff-compare before vs after a deploy to catch regressions, tag profiles per endpoint/tenant/version to isolate a slow route, profile heap over time to spot memory leaks (continuous growth), and use block/mutex profiles to find lock contention.

**Senior**: "How do you find a bottleneck with profiling?" — Capture a CPU profile, read the flame graph for the widest frame, optimize that path, then re-profile and diff to confirm the improvement; for a slow endpoint, scope the profile by tag or span so you're looking only at the affected requests.

**Staff**: "How do you build profiling into the development lifecycle?" — Run continuous profiling in production at ~1% overhead, tag richly for filtering, baseline performance in CI and fail the build on regression via a profile diff, auto-capture a profile when an alert fires and attach it to the incident, and link profiles to traces so a slow span points directly at the responsible code.

## Next Topic

→ Move to [L18/C08 — Correlating Logs, Metrics, Traces](../C08/README.md)
