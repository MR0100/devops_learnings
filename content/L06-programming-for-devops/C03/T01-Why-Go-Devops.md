# L06/C03/T01 — Why Go for DevOps Tooling

## Learning Objectives

- Understand Go's strengths for ops
- Choose Go vs Python

## Why Go

Go (Golang): created at Google 2007; designed for systems programming. Now lingua franca of cloud-native DevOps.

## Key Strengths

### 1. Static Binary
```bash
go build -o tool ./cmd/tool
# Output: single binary, ~10 MB, no Python runtime needed
```
Ship one file; runs on any matching OS/arch. No `pip install`, no venv, no dep hell.

### 2. Cross-Compilation
```bash
GOOS=linux GOARCH=amd64 go build
GOOS=darwin GOARCH=arm64 go build
GOOS=windows GOARCH=amd64 go build
```
Build for any target from any host.

### 3. Concurrency
Goroutines (lightweight threads): cheap; millions practical.
```go
go func() { ... }()    // spawn
```
Channels for synchronization. Better than Python's GIL.

### 4. Performance
Compiled; near-C speed. Important for tools handling huge data.

### 5. Standard Library
Heavy lifters built in: HTTP server, JSON, crypto, os, exec, etc.

### 6. Simple Language
~25 keywords. Easy to read. Strict formatter (`gofmt`); no style wars.

### 7. Ecosystem
Kubernetes, Docker, Terraform, Prometheus, etcd, Vault — all in Go. If you contribute to or extend cloud-native tools, you write Go.

## What's Built in Go

| Tool | What |
|---|---|
| Kubernetes | Container orchestrator |
| Docker | Containers |
| Terraform | IaC |
| Prometheus | Metrics |
| Grafana | Dashboards |
| etcd | Distributed KV |
| Vault | Secrets |
| Consul | Service discovery |
| containerd, runc | Container runtime |
| Helm | K8s package mgr |
| Cilium | eBPF networking |

## Go vs Python for DevOps

| | Python | Go |
|---|---|---|
| Speed of dev | Faster | Slower |
| Runtime perf | Slower | Faster |
| Deploy | Need Python + deps | Single binary |
| Concurrency | GIL pain | First-class |
| K8s integration | Decent | Native |
| CLI tools | Fine | Better (binary) |
| One-off scripts | Better | Overkill |
| Heavy systems | Painful | Natural |

### When Python
- Quick automation
- Glue scripts
- Data manipulation
- Existing Python infrastructure

### When Go
- Distributed (concurrent) tools
- CLIs for distribution (no runtime)
- K8s controllers / operators
- Long-running daemons
- Performance-critical

## Example: Same Tool in Both

Python tool that lists pods:
```python
from kubernetes import client, config
config.load_kube_config()
v1 = client.CoreV1Api()
for p in v1.list_pod_for_all_namespaces().items:
    print(p.metadata.namespace, p.metadata.name)
```
- 5 lines; pip install needed; runs in venv.

Go equivalent:
```go
package main

import (
    "context"
    "fmt"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/tools/clientcmd"
)

func main() {
    config, _ := clientcmd.BuildConfigFromFlags("", "/path/.kube/config")
    clientset, _ := kubernetes.NewForConfig(config)
    pods, _ := clientset.CoreV1().Pods("").List(context.Background(), metav1.ListOptions{})
    for _, p := range pods.Items {
        fmt.Println(p.Namespace, p.Name)
    }
}
```
- More code; but `go build -o kpods` → single binary you can `scp` anywhere.

## What You Won't Like (Coming from Python)

- Verbose (no list comprehensions, no decorators)
- Error handling: `if err != nil` everywhere
- No exceptions
- Generics late (Go 1.18+); ecosystem still catching up
- Lots of boilerplate

## Strategy

You need both:
- **Go**: distributed tools, K8s operators, daemons, fast CLIs
- **Python**: glue, scripts, ad-hoc analysis, data manipulation

FAANGM DevOps engineers are expected to read Go fluently and write basic Go. Senior+ writes operators in Go.

## Learn Curve

If you know Python well, Go syntax takes 2-3 days. Idiomatic Go (channels, goroutines, interfaces) takes weeks. Production K8s controllers: months.

## Resources

- A Tour of Go: tour.golang.org
- Effective Go: golang.org/doc/effective_go
- Go by Example: gobyexample.com
- Kubernetes operator scaffolding: kubebuilder.io, operator-sdk

## Common Mistakes

- Reaching for Go on every script — for a 40-line glue task Python ships faster; Go's payoff is binaries, concurrency, and long-lived daemons.
- Forgetting `CGO_ENABLED=0` and then being surprised the "static" binary won't run in a scratch/distroless container.
- Fighting the language: writing Python-style code in Go (exceptions, dynamic dicts everywhere) instead of explicit errors and structs.
- Underestimating the K8s controller learning curve — informers, work queues, and reconcile semantics take weeks, not days.
- Assuming "compiles" means "correct" and skipping `go vet` and the race detector.

## Best Practices

- Choose Go when you need a single static binary, low memory, fast startup, true concurrency, or first-class Kubernetes libraries; choose Python for fast iteration and rich scripting.
- Build with `CGO_ENABLED=0 go build -ldflags="-s -w"` to get a small, dependency-free binary that runs in `scratch`/distroless.
- Cross-compile in CI (`GOOS`/`GOARCH`) to ship Linux/macOS, amd64/arm64 from one pipeline.
- Lean on the standard library and `gofmt`/`go vet`; the ecosystem favors small dependency trees.
- Embed version metadata via `-ldflags` so every binary reports its build.

## Quick Refs

```bash
# Static, stripped, dependency-free binary
CGO_ENABLED=0 go build -ldflags="-s -w" -o mytool .

# Cross-compile
GOOS=linux   GOARCH=arm64 go build -o mytool-linux-arm64 .
GOOS=darwin  GOARCH=arm64 go build -o mytool-darwin-arm64 .

# Embed version at build time
go build -ldflags="-X main.version=$(git describe --tags)" -o mytool .

go vet ./...        # static checks
go run .            # compile + run
```

```dockerfile
# Minimal image for a Go DevOps tool
FROM golang:1.22 AS build
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /mytool .

FROM gcr.io/distroless/static:nonroot
COPY --from=build /mytool /mytool
ENTRYPOINT ["/mytool"]
```

## Interview Prep

**Junior**: "Why might a DevOps engineer choose Go?"

**Mid**: "Static binary advantage in deploy?"

**Senior**: "Go vs Python tradeoffs for new CLI tool?"

## Next Topic

→ [T02 — Modules, Structs, Interfaces, Errors](T02-Go-Basics.md)
