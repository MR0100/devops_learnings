# L25/C02/T04 — Gremlin

## Learning Objectives

- Use Gremlin for managed, multi-platform chaos
- Know its fault catalog, targeting, and safety model
- Decide when Gremlin beats OSS (Chaos Mesh / Litmus / FIS)

## Gremlin

Commercial chaos-as-a-service. Agent + control plane + UI/API.

- UI- and API-driven (less YAML than CRD tools)
- Broad fault catalog across Resource / State / Network / Time
- Targets hosts, containers, Kubernetes, and cloud resources from one console
- Built-in safety: blast-radius caps, auto-halt, Status Checks
- Reliability scoring and scheduled, recurring experiments

Positioning: a polished, supported alternative to stitching together Chaos
Mesh + tc + custom scripts. You pay for the UI, the curated attack library,
the safety rails, and the audit/compliance reporting.

## Architecture

```
┌──────────────┐   outbound TLS    ┌─────────────────────┐
│ Gremlin agent│ ◀───────────────▶ │ Gremlin control      │
│ (host/daemon │   (no inbound     │ plane (SaaS)         │
│  or k8s pod) │    port needed)   │  UI · API · scoring  │
└──────┬───────┘                   └─────────────────────┘
       │ executes faults locally
       ▼
   target process / netns / cgroup
```

The agent dials *out* to Gremlin, so you don't open inbound ports. It runs as
a Linux service, a container, or a Kubernetes DaemonSet (`gremlin/chao`).

## Fault Catalog

| Category  | Faults                                                      |
|-----------|-------------------------------------------------------------|
| Resource  | CPU, Memory, Disk (fill), IO                                |
| State     | Process Killer, Shutdown (reboot/halt), Time Travel         |
| Network   | Latency, Packet Loss, Blackhole, DNS, Bandwidth limit       |
| Time      | Clock skew (forward/back) — TLS, TOTP, scheduler tests      |
| Requests  | Application-Level Fault Injection (ALFI) — fail by request  |

ALFI is the differentiator: inject faults scoped to a single user, request
header, or code path via SDK, instead of whole-host blast.

## Setup

```bash
# Linux host agent (needs GREMLIN_TEAM_ID + GREMLIN_TEAM_SECRET)
curl -s https://rpm.gremlin.com/install.sh | sh
gremlin init     # registers agent with the team

# Kubernetes (Helm) — runs the agent as a DaemonSet
helm repo add gremlin https://helm.gremlin.com
helm install gremlin gremlin/gremlin \
  --namespace gremlin --create-namespace \
  --set gremlin.secret.managed=true \
  --set gremlin.secret.teamID=$TEAM_ID \
  --set gremlin.secret.clusterID=prod-use1
```

## Running an Attack

UI flow: pick **target** → **attack type** → **magnitude** → **duration** → Run.
CLI/API equivalent:

```bash
# 100ms latency on eth0 to a host's egress, 5% blast, 60s
gremlin attack-container <id> latency \
  --length 60 --delay 100 --providers aws

# Or via API
curl -X POST https://api.gremlin.com/v1/attacks/new \
  -H "Authorization: Bearer $GREMLIN_API_KEY" \
  -d '{"target":{"type":"Random","percent":5,"tags":{"env":["staging"]}},
       "command":{"type":"latency","args":["-l","60","-m","100"]}}'
```

`gremlin halt` (or the big red **Halt All** button) kills every running attack
immediately — the universal abort.

## Safety: Status Checks & Blast Radius

Gremlin's auto-abort hooks an external signal (Datadog monitor, Prometheus
query, HTTP health endpoint). If it trips during an attack, Gremlin halts.

```
Blast radius = % of targets × magnitude × duration
Start: 1 host, low magnitude, short duration → widen only after green.
```

This maps directly to the steady-state / blast-radius discipline from L25/C01.

## Templates & Scenarios

Pre-built **Scenarios** chain attacks into a realistic failure story:

- "Region failover" — blackhole one region's egress, watch DNS/LB shift
- "DB primary down" — kill the primary process, measure failover RTO
- "Cache evict / Redis down" — stop cache, watch DB miss-storm + degradation
- "Noisy neighbor" — CPU + IO hog, verify cgroup limits isolate tenants

Scenarios run on a schedule and feed the Reliability Score over time.

## Reliability Score

Gremlin runs recurring suites and grades services 0–100 across Scalability,
Redundancy, and (D)ependency resilience. Use it to **track improvement
quarter-over-quarter**, not as an absolute truth — the score only reflects the
experiments you actually ran.

## Gremlin vs OSS

| Dimension       | Gremlin                    | Chaos Mesh / Litmus / FIS      |
|-----------------|----------------------------|--------------------------------|
| Cost            | Per-host/agent subscription| Free (OSS) / pay-per-use (FIS) |
| Onboarding      | Fast, UI-guided            | YAML/CRD or AWS template       |
| Platforms       | Linux, Win, K8s, cloud     | Mostly K8s (Mesh/Litmus); AWS (FIS) |
| Flexibility     | Curated catalog            | Anything you can script        |
| Safety rails    | Built-in (Status Checks)   | Roll your own stop conditions  |
| Lock-in         | Vendor                     | Portable manifests             |
| Compliance docs | First-class                | DIY                            |

### Choose Gremlin when
- You want a managed product with support and audit/compliance reporting
- You run **mixed estates** (bare metal + VMs + multiple K8s + clouds)
- Budget is available and you'd rather not maintain chaos tooling

### Choose OSS when
- Cost-sensitive, or Kubernetes-only (Chaos Mesh / Litmus fit natively)
- You need deep custom faults (KernelChaos, bespoke HTTP rewriting)
- You want experiments versioned as portable YAML in Git

## Common Mistakes

- Skipping Status Checks — the attack can't auto-halt on a bad signal
- Running blind: no steady-state baseline, so you can't read the result
- First experiment at high magnitude on prod instead of 1 host in staging
- Treating the Reliability Score as gospel without checking which experiments ran
- Forgetting agents need outbound egress allowed (attacks silently never start)

## Best Practices

- Tag every target (`env`, `service`, `team`) and target by tag, never by ID
- Wire auto-halt to a real SLO monitor before any prod attack
- Start with curated Scenarios; graduate to custom + ALFI for code-path faults
- Schedule recurring suites so regressions surface, then trend the score
- Keep `gremlin halt` muscle memory — everyone in the war room knows the kill switch

## Quick Refs

```bash
gremlin init                      # register agent
gremlin attack-container <id> ... # run an attack
gremlin halt                      # abort all running attacks
helm install gremlin gremlin/gremlin   # k8s DaemonSet
# API: POST /v1/attacks/new ; Status Checks → auto-halt
```

## Interview Prep

**Junior**: "What is Gremlin?" — A commercial chaos-as-a-service platform with an agent, a UI/API, a broad fault catalog, and built-in safety.

**Mid**: "How does Gremlin abort safely?" — Status Checks poll an external SLO signal (e.g. a Datadog/Prometheus monitor) and auto-halt the attack if it trips; `gremlin halt` is the manual kill switch.

**Senior**: "Gremlin vs OSS chaos tools?" — Gremlin buys you UI, multi-platform reach, curated faults, and safety rails at the cost of money and lock-in; Chaos Mesh/Litmus are free and K8s-native, FIS is AWS-native pay-per-use, and all three need you to build your own safety.

**Staff**: "Justify Gremlin in a platform strategy." — Pick it when chaos is a managed capability across a heterogeneous estate with compliance needs; reach for OSS where workloads are K8s-homogeneous, custom faults dominate, or experiments must live as portable Git-versioned manifests.

## Next Topic

→ [T05 — AWS Fault Injection Simulator (FIS)](T05-AWS-FIS.md)
