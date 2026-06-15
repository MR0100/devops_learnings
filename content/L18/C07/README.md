# L18/C07 — Profiling

## Topics

- **T01 Pyroscope / Grafana Profiles** — Continuous profiling tools
- **T02 Continuous Profiling Patterns** — How to use in production

## What Continuous Profiling Is

Sample CPU / memory / goroutines / locks of every process, continuously, in production. Generate flame graphs over time.

Traditional profiling: turn on locally, find hot spot, turn off.
Continuous profiling: always on, low overhead (~1-5%), profile what's actually running in prod.

## Flame Graph

Width = time spent. Reading: width of stack frame = how much time. Tall = deep call stack.

```
└── main                                 (100%)
    └── HandleRequest                   (100%)
        ├── ParseJSON                    (5%)
        ├── ValidateInput                (3%)
        ├── DBQuery                     (70%)  ← bottleneck
        │   ├── PoolGetConn              (2%)
        │   └── PgxQueryRow             (68%) ← here
        └── EncodeResponse              (22%)
            └── jsonMarshal             (18%)
```

Tells you: 70% of CPU was in DB query handling; optimize there.

## Pyroscope

OSS continuous profiler. Now part of Grafana.

```bash
helm install pyroscope grafana/pyroscope
```

### Modes
- **Pull**: scrapes `/debug/pprof` endpoints (Go, etc.)
- **Push**: SDK in app
- **eBPF**: kernel-level sampling (works for any binary, no SDK)

### Pyroscope Go SDK
```go
import "github.com/grafana/pyroscope-go"

pyroscope.Start(pyroscope.Config{
    ApplicationName: "myapp",
    ServerAddress:   "http://pyroscope:4040",
    Logger:          pyroscope.StandardLogger,
    ProfileTypes: []pyroscope.ProfileType{
        pyroscope.ProfileCPU,
        pyroscope.ProfileAllocObjects,
        pyroscope.ProfileAllocSpace,
        pyroscope.ProfileInuseObjects,
        pyroscope.ProfileInuseSpace,
    },
})
```

### eBPF (Linux)
```bash
helm install pyroscope grafana/pyroscope --set ebpf.enabled=true
```

No app changes. Profiles all processes.

## What to Profile

### CPU
- Where is the program spending CPU?
- Find hot functions, inefficient loops, missing indexes

### Memory (Heap)
- Where is allocation happening?
- Find leaks (alloc grows; in-use grows)

### Goroutines (Go)
- How many goroutines? Where are they parked?
- Find goroutine leaks

### Locks / Mutex (Go)
- Where is contention?

### Block (Go)
- Where are goroutines blocking on I/O?

## Use Cases

### Performance Investigation
- "p99 latency degraded after deploy"
- Compare flame graph before/after
- Find regression

### Cost Reduction
- "Why is this service 4 cores busy?"
- Find inefficient code paths
- Optimize → reduce instance count

### Memory Leak
- Show heap profile over time
- Find continuously growing allocations
- Fix the leak

### Tail Latency
- Profile p99 slow traces only (via OTel correlation)
- Why are slow ones slow?

## Continuous Profiling Patterns

### Always-On Sampling
~99% of pods, ~1% CPU overhead. Always have data.

### Trace-Linked Profiling
Profile only when a trace is slow. Get the actual stack of slow traces.

### Diff Profiling
Compare two time windows (before/after deploy, between regions). Highlight differences.

### Custom Annotations
Annotate flame graph with deploy versions; see when regression started.

## Storage

Profiles are huge. Pyroscope compresses heavily:
- Symbols deduplicated
- Sampling reduces volume
- S3 / GCS storage

## Tools

- **Pyroscope / Grafana Profiles** — OSS
- **Parca** — Polar Signals, eBPF-based
- **Polar Signals Cloud** — commercial
- **Datadog Continuous Profiler** — commercial
- **Granulate gMaster** — Intel/AMD optimization
- **Profefe** — older tool

## Reading Flame Graphs

- Wide = expensive
- Tall isn't necessarily bad (deep stacks can be cheap per frame)
- Look for "plateaus" (wide flat sections — single function spending time)
- Sort by call depth or alphabetical (interactively)

## Integration

```
Trace UI (Tempo)
   "view profile for this trace's slow span"
        ↓
Pyroscope UI
   shows flame graph
   for that pod, during that time window
```

Some products integrate cross-pillar (Honeycomb, Datadog, Grafana).

## Interview Themes

- "Continuous profiling — why?"
- "Flame graph — how to read"
- "eBPF profiling vs SDK"
- "Find a memory leak — what tool?"
- "Use case where profiling found something"
