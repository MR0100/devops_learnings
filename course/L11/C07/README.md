# L11/C07 — Comparison & Selection

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Comparison.md) | Ansible vs Puppet vs Chef vs Salt | 0.5 hr |
| [T02](T02-IaC-Containers-Replacement.md) | When to Replace with IaC + Containers | 0.5 hr |

## Side-by-Side

| | Ansible | Puppet | Chef | SaltStack |
|---|---|---|---|---|
| Language | YAML + Jinja2 | Puppet DSL | Ruby DSL | YAML + Jinja2 (or Python) |
| Model | Push (SSH) | Pull (agent) | Pull (agent) | Push/pull (event-driven) |
| Agentless | Yes | No | No | Optional (Salt SSH) |
| Master required | No | Yes | Yes | Yes (or standalone) |
| Learning curve | Low | High | High | Medium |
| Self-healing | No (runs once) | Yes (every cycle) | Yes | Yes |
| Speed at scale | Medium | Slow per-node | Slow per-node | Fast |
| Order semantic | Sequential within play | DAG resolved | Sequential | DAG resolved |
| Community | Largest | Mature, declining | Declining | Niche |
| Best for | Most use cases today | Convergence-critical fleets | Heritage Chef shops | Event-driven, very large fleets |

## Choose By Use Case

| Need | Pick |
|---|---|
| Bootstrap cloud VMs | Ansible or cloud-init |
| Bake images (Packer) | Ansible |
| Network gear | Ansible (rich modules) |
| Long-lived fleet, convergence | Puppet (or Salt) |
| Massive scale (10K+) | Salt |
| Real-time event response | Salt |
| Existing Chef investment | Chef |
| Greenfield non-K8s server | Ansible |

## When to Replace CM Entirely

Many traditional CM use cases are better solved by:

### Immutable Infrastructure
Bake server config into images. New version = new image. Replace, don't patch.

Tools: Packer + Ansible for image build; ASG / VMSS / MIG for rollouts.

### Containers + Kubernetes
For applications: don't manage servers; manage containers. K8s + Helm replace CM for application workloads entirely.

### IaC for Infrastructure
Terraform/CDK/Pulumi for cloud resources. CM was the only way to provision before IaC existed.

### Serverless
Lambda et al. eliminate the server. No CM needed.

## What CM Still Owns (in 2025+)

- **Bare-metal provisioning** — PXE + Ansible bootstrap
- **Network gear** — switches, routers, load balancers
- **Hybrid on-prem** — Windows/Linux legacy
- **Day-2 ops on long-lived hosts** — patch, cert rotation, log rotation
- **Inside image build** — Ansible runs inside Packer
- **Compliance-driven mutable** — regulated industries with mandatory drift correction

## Architecture That Combines

```
Terraform → provision infra (VPC, EC2, RDS)
Packer + Ansible → bake AMIs
ASG → rolling deploys
Kubernetes → app workloads
Ansible → network gear, day-2 ops
```

## Migration Stories

### From Puppet to Containers
1. Containerize each service
2. Move to K8s
3. Retire Puppet for application servers
4. Keep Puppet for any remaining bare metal (typically gone in 1-2 years)

### From Chef to Terraform + Ansible
1. Move infra provisioning from Chef to Terraform
2. Move host config from Chef recipes to Ansible playbooks
3. Bake AMIs with Packer + Ansible
4. Retire Chef

## Interview Themes

- "Pick a CM tool for X scenario"
- "Why is Ansible most popular today?"
- "When would you NOT use CM?"
- "Migrating from Puppet to containers — strategy"
- "What does CM still own in 2025?"
