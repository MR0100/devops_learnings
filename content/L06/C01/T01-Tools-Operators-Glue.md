# L06/C01/T01 — Tools, Operators, Glue Code

## Learning Objectives

- Recognize types of code DevOps engineers write
- Plan code investments

## Three Categories of DevOps Code

### 1. Glue Scripts
- Connect existing tools
- One-off automation
- Common: bash, Python
- Examples: backup script, deploy wrapper, log analyzer

### 2. Internal Tools
- CLIs for self-service
- Daemons, exporters
- Common: Python (Click/Typer), Go (Cobra)
- Examples: internal `myco deploy`, custom Prometheus exporter

### 3. Kubernetes Operators
- Manage K8s resources at scale
- Go primarily (controller-runtime)
- Examples: PostgreSQL operator, custom CRD controllers

## What You'll Build Over Career

| Task | Language |
|---|---|
| Backup automation | Bash → Python |
| Slack bot | Python / Go |
| Internal CLI | Go (Cobra) or Python (Typer) |
| Custom Prometheus exporter | Go (client_golang) |
| K8s operator | Go (controller-runtime) |
| Terraform provider | Go (Plugin Framework) |
| GitHub Action | TypeScript or Go composite |
| Webhook receiver | Python / Go / any |
| Log shipper | Go / Rust (perf) |
| Config templating | Python (Jinja2) / Go (text/template) |

## Why DevOps Engineers Code

- Operators (K8s extension model demands Go)
- Glue (CLIs handle ticket avoidance)
- Force-multiplication (one tool benefits many teams)
- Investigation (data analysis ad-hoc)
- Reporting (custom dashboards / alerts)
- Self-service (no platform team bottleneck)

## What You'll NOT Write Much

Compared to backend engineers:
- Less business logic
- Less customer-facing apps
- Less databases / data layer

You write tools FOR engineers more than apps for users.

## Coding Investment

For a senior+ DevOps engineer:
- Daily: ad-hoc Python / bash
- Weekly: refine tools
- Quarterly: build new tool of significance
- Yearly: contribute to OSS

## Open Source Contribution

Strong DevOps engineers contribute back:
- Kubernetes-related projects
- Terraform providers
- CLI plugins (kubectl plugins, GH CLI extensions)
- Custom Helm charts

Sign of seniority.

## Tools You'll Use Daily

- **Code editor**: VS Code, JetBrains
- **Language runtimes**: Python, Go
- **Linters**: ruff, golangci-lint, shellcheck
- **Test frameworks**: pytest, go test
- **Local dev**: Docker, kind, minikube
- **Debug**: pdb, dlv

## When to Build vs Buy vs OSS

- **Buy**: Datadog, GitHub Enterprise (mature, supported)
- **OSS**: Prometheus, Grafana, Loki (mature, free)
- **Build**: company-specific internal tools, glue

For 90% of needs: existing solutions. The 10% custom is your value-add.

## Career Pattern

Junior: scripts.
Mid: tools, small CLIs.
Senior: operators, large CLIs, OSS contribs.
Staff: shape platform; write specs; review others' code.
Principal: rare deep work; architecture.

## Don't Write

- Mega-bash 1000+ lines (use Python)
- Custom data structures Python provides
- Custom CI runner (use existing)
- Yet another secret manager (use Vault / cloud-native)

## Do Write

- Domain-specific CLI for your team
- Custom Prometheus metrics for your infra
- Specific operators for company resources
- Wrappers reducing footguns

## Common Mistakes

- Rebuilding something off-the-shelf (Terraform, ArgoCD, External Secrets) because writing it "looks easy" — you own the maintenance forever.
- Letting a glue script silently grow into a 1500-line untested monolith instead of promoting it to a real package with tests.
- Writing tools only you can run (hardcoded paths, your laptop's creds) — operators and platform code must run unattended in CI/clusters.
- Treating "code" as the deliverable. The deliverable is the outcome (less toil, fewer incidents); code is liability you carry.
- Skipping the README/`--help` so nobody else on the team can adopt the tool, guaranteeing it dies when you leave.

## Best Practices

- Apply build vs buy vs OSS deliberately: buy/adopt for commodity, build only for company-specific glue and domain CLIs.
- Optimize for deletion — the best glue code is the script you delete after the upstream tool ships the feature.
- Ship a `--help`, a README, and at least smoke tests so a teammate can take it over cold.
- Contribute the fix upstream when you patch an OSS tool you depend on; carrying a private fork is recurring toil.
- Measure impact in toil/incidents reduced, not lines written; retire tools that no longer earn their maintenance cost.

## Quick Refs

```text
DECISION CHEAT-SHEET — build vs buy vs OSS
  Commodity, well-solved (CI, secrets, IaC) ........ BUY / ADOPT OSS
  Company-specific glue / domain CLI ............... BUILD (small, tested)
  Generic infra need, active OSS exists ............ ADOPT, contribute back
  One-off, run < 5 times ........................... BASH SCRIPT (throwaway)
  Long-lived, run unattended in CI/cluster ......... PYTHON / GO PACKAGE

THREE CATEGORIES OF DEVOPS CODE
  Glue ........ wire existing tools together (most of your time)
  Operators ... reconcile desired vs actual state (Go + controller-runtime)
  Platform .... internal tools your org's engineers depend on

WRITE vs DON'T
  Write: team CLIs, custom metrics, company operators, footgun wrappers
  Don't: mega-bash, custom CI runners, another secret manager, re-implement stdlib
```

## Interview Prep

**Mid**: "What DevOps tools have you written?"

**Senior**: "Recent OSS contribution."

**Staff**: "Build vs buy decision for X."

## Next Topic

→ [T02 — When Bash Isn't Enough](T02-When-Bash-Stops.md)
