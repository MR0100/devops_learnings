# L11/C01/T02 — Pull vs Push Models

## Learning Objectives

- Understand pull and push
- Pick by use case

## Push Model

Control machine pushes config to nodes:
```
Ansible control → SSH → target servers (apply now)
```

- Ad-hoc
- No agent
- Centralized state of "what's applied"
- Failure if node unreachable

Examples: Ansible (default).

## Pull Model

Nodes pull config from central server:
```
Node → poll → Puppet/Chef server → fetch latest catalog → apply
```

- Agent on each node
- Continuous reconciliation
- Scales (server doesn't push to thousands)
- Resilient (node retries)

Examples: Puppet, Chef, Salt (default).

## Push: Pros

- Simple model
- Ad-hoc actions
- No agent install
- Immediate

## Push: Cons

- Doesn't scale beyond ~1000 nodes simply
- Needs reachable from control
- Node not on at run-time: missed
- Need orchestrator

## Pull: Pros

- Scales (server passive)
- Resilient (node retries)
- Continuous reconciliation
- Each node knows when to check

## Pull: Cons

- Agent install + maintenance
- Slower for immediate change
- Server is single point (HA needed)
- Push doesn't exist (need separate channel for "run now")

## Hybrid

Most tools support both modes:
- Ansible: push (default) or pull (ansible-pull on cron)
- Salt: master/minion (push from master) or salt-ssh (no minion)
- Chef: pull (default) or push via knife ssh

## Pull Implementation

### Puppet
```
Agent runs every 30 min
   → Server compiles catalog
   → Agent applies
   → Reports back
```

### Chef
```
Chef Client runs (cron or interval)
   → Pulls from Chef Server
   → Applies
   → Reports
```

### Ansible Pull
```bash
# On each node
ansible-pull -U git@repo:playbooks.git playbook.yml
# In cron: every 30 min
```

For: push tool but pull mode.

## Push at Scale

### Ansible
- Forks: parallel SSH (default 5; tune up)
- Mitogen plugin (faster execution)
- Async tasks
- Strategies (free, linear)

Practical limit: ~1000 nodes per playbook run.

For more: split, parallel.

### Tower / AWX
Workflow orchestration; scheduled runs.

## Pull at Scale

Puppet / Chef: 10,000+ nodes routine.

Server handles polling load. Caching.

## Push for K8s

K8s = control loop = "pull" model conceptually.

API server: source of truth.
Kubelet: pulls desired state.

For: containers, similar to pull.

## Salt Specific

Salt: ZeroMQ-based; very fast push.
Minion subscribes; master pushes events.

For high-scale event-driven: Salt.

## When Push (Ansible)

- Ad-hoc tasks
- Few nodes
- Simple
- No agent allowed
- Day-2 ops

## When Pull (Puppet/Chef)

- Many nodes
- Continuous reconciliation
- Auto-scaling (new nodes pull on boot)
- Survive control plane issues

## Auto-Scaling

For ASG:
- New VM boots
- Pulls config (cloud-init runs Puppet/Chef agent)
- Self-configures

Push: must orchestrate "new node up, send config."

Pull: natural fit.

## SSH vs Agent

| | Push (SSH) | Pull (Agent) |
|---|---|---|
| Install | Nothing (SSH-only) | Agent + cert |
| Comms | Outbound SSH | Outbound HTTPS |
| Firewall | SSH ingress | HTTPS egress (easier) |
| Auth | SSH key | Cert |
| State | Control side | Server side |

For egress-only firewalls: pull easier.

## SaltStack Push

Salt master pushes events:
- Reactor: event-driven
- Beacon: minion sends events

For: real-time reaction.

## Comparison

| | Push (Ansible) | Pull (Puppet) |
|---|---|---|
| Default model | Push | Pull |
| Agent | No | Yes |
| Scale | Hundreds easy | Thousands easy |
| Speed | Fast for small | Polling delay |
| Drift fix | Manual re-run | Auto |
| Reporting | Limited (per-run) | Built-in |

## Cloud-Native View

Modern thinking:
- Containers + K8s: declarative; controller loops = pull-like
- GitOps: ArgoCD pulls from Git
- Image-based: less config management needed

Trend: less in-place config; more rebuild.

## Best Practices

- Push for ad-hoc + simple
- Pull for fleet + auto-scaling
- Either: declarative
- Test in lower env
- Idempotent
- Continuous reconciliation (where possible)

## Common Mistakes

- Push at large scale (slow, fragile)
- Pull for ad-hoc (slow feedback)
- No idempotency (rerun breaks)
- Forget node boot config (manual touch)

## Quick Refs

```
Push: Ansible (SSH)
Pull: Puppet (agent), Chef (agent)
Hybrid: Ansible-pull (cron); Salt (both)
GitOps: ArgoCD/Flux (K8s pull from Git)
```

## Interview Prep

**Junior**: "Push vs pull."

**Mid**: "When each."

**Senior**: "Scaling config management."

**Staff**: "Configuration strategy for fleet."

## Next Topic

→ Move to [L11/C02 — Ansible Fundamentals](../C02/README.md)
