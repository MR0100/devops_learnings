# L06/C01 — Why DevOps Engineers Must Code

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Tools-Operators-Glue.md) | Tools, Operators, Glue Code | 0.5 hr |
| [T02](T02-When-Bash-Stops.md) | When Bash Isn't Enough | 0.5 hr |

## The Coding Reality of Senior+ DevOps

You will be asked to:

| Task | Likely Language |
|---|---|
| Write a Kubernetes operator | Go |
| Build a CI plugin / GitHub Action | TypeScript / Go |
| Write an infra automation script | Python or Go |
| Build a Terraform provider | Go |
| Write a Prometheus exporter | Go |
| Build an internal CLI | Go (Cobra) or Python (Click/Typer) |
| Process logs / data | Python (pandas/polars) |
| Wrap an API for self-service | Python or TypeScript |
| Implement a custom controller | Go (controller-runtime) |
| Write tests for the above | Same language |

## Tools You'll Build

- Internal CLIs that wrap kubectl/aws-cli/terraform
- GitOps controllers / Kubernetes operators
- Slackbots / ChatOps
- Custom Prometheus exporters
- Webhooks for admission control
- Log enrichment pipelines
- Cost analysis scripts
- Capacity planning models
- Compliance reporting jobs

## When Bash Stops Being Enough

Signs:
- > 300 lines and growing
- Needs proper data structures (lists of records, trees)
- Multiple input formats (JSON, YAML, CSV)
- Multi-threaded I/O (parallel HTTP)
- Cross-platform requirement (Windows)
- Needs unit tests
- Other team members will maintain it
- Performance-critical
- Reusable as a library

## Languages of Cloud-Native

```
Go    — Kubernetes, etcd, Prometheus, Terraform, Docker, containerd, runc,
        Vault, Consul, ArgoCD, Flux, Istio, Cilium, Loki, Cortex, Thanos,
        Linkerd, Velero, CrossPlane, OPA, Helm, kubectl, etc.

Rust  — Envoy alternatives, Linkerd2-proxy, Bottlerocket, parts of K8s scheduler,
        eBPF tools, Vector, security tooling

Python — Ansible, OpenStack, Airflow, data/ML, many internal tools,
         glue scripting

C/C++ — Envoy, Nginx, HAProxy, kernel/userspace tools

TypeScript — Backstage, CDK, Pulumi, GitHub Actions, Cloudflare Workers
```

> If you only learn one language for cloud-native: **Go**. If you only learn two: Go + Python.

## Building Production-Grade Tools

A production tool has:

- Strong CLI with --help, --version, flags
- Sensible defaults
- Logging (structured, levels)
- Error handling
- Configuration (env vars, files, flags)
- Observability (metrics, traces)
- Tests
- Documentation
- Versioned releases
- Distribution (Homebrew, apt, Docker, GoReleaser)

This is what L06 teaches.

## Interview Themes

- "Have you built tools at work? Walk me through one."
- "Why do DevOps engineers need to code?"
- "When would you choose Go over Python?"
- "Show me a real script/tool you've shipped"
