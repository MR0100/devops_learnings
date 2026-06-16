# L06 — Programming for DevOps (Python & Go)

## Overview

The line between DevOps engineer and "Senior DevOps engineer" is usually drawn at code: can you build tools, not just configure them. Python and Go dominate this space.

**5 chapters, 22 topics.**

## Chapter Map

### [C01](C01/) — Why DevOps Engineers Must Code
- T01 Tools, Operators, Glue Code
- T02 When Bash Isn't Enough

### [C02](C02/) — Python for DevOps
- T01 Idiomatic Python (PEP 8, Typing, Black, Ruff)
- T02 Virtual Environments, Poetry, uv
- T03 Standard Library Highlights (subprocess, pathlib, argparse)
- T04 requests, httpx for HTTP
- T05 Boto3 for AWS, the Kubernetes Python Client
- T06 Writing CLIs with Click / Typer
- T07 Testing with pytest

### [C03](C03/) — Go for DevOps
- T01 Why Go for DevOps Tooling
- T02 Modules, Structs, Interfaces, Errors
- T03 Concurrency (Goroutines & Channels)
- T04 Cobra for CLIs
- T05 client-go for Kubernetes
- T06 controller-runtime & kubebuilder
- T07 Testing Go Code

### [C04](C04/) — API Design
- T01 REST Design Principles
- T02 OpenAPI / Swagger
- T03 gRPC and Protocol Buffers
- T04 Webhooks and Async APIs

### [C05](C05/) — Building Production Tools
- T01 Anatomy of a Production Tool
- T02 Idempotency, Dry-run, Confirmations
- T03 Logging, Tracing, Metrics in Tools
- T04 Configuration: Env, Files, Flags

## Why Python AND Go

| | Python | Go |
|---|---|---|
| Type | Dynamic | Static |
| Distribution | Interpreter required (pyinstaller helps) | Single static binary |
| Concurrency | GIL limits true parallelism | First-class goroutines/channels |
| Ecosystem | Massive (data, ML, scripting) | Cloud-native, infra tooling |
| Best for | Glue scripts, automation, ML/DS | CLIs, controllers, operators, daemons |
| Used by | Ansible, OpenStack, many internal tools | K8s, Terraform, Docker, etcd, Prometheus |

## Minimal Production CLI Template (Go)

```go
package main

import (
    "context"
    "log/slog"
    "os"
    "os/signal"
    "syscall"
    "github.com/spf13/cobra"
)

func main() {
    ctx, cancel := signal.NotifyContext(context.Background(), syscall.SIGTERM, syscall.SIGINT)
    defer cancel()

    root := &cobra.Command{
        Use:   "mytool",
        Short: "Description",
        RunE: func(cmd *cobra.Command, args []string) error {
            slog.Info("starting")
            // ...
            return nil
        },
    }
    if err := root.ExecuteContext(ctx); err != nil {
        slog.Error("failed", "error", err)
        os.Exit(1)
    }
}
```

## Minimal Production CLI Template (Python)

```python
import argparse, logging, sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("input")
    args = parser.parse_args(argv)
    try:
        log.info("starting", extra={"input": args.input})
        # ...
    except Exception:
        log.exception("failed")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## Recommended Reading

- *Fluent Python* — Luciano Ramalho (Python)
- *The Go Programming Language* — Donovan & Kernighan
- *100 Go Mistakes* — Teiva Harsanyi
- Kubernetes source (client-go, controller-runtime) for real-world Go patterns

## Interview Relevance

- "Write a Python script that does X"
- "Build a small CLI that talks to AWS / K8s"
- "When would you choose Go over Python for a tool?"
- "Code a rate limiter / token bucket"

## Next

→ [L07 — Cloud Computing Fundamentals](../L07-cloud-foundations/README.md)
