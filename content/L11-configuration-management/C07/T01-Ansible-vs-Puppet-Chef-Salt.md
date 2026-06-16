# L11/C07/T01 — Ansible vs Puppet vs Chef vs Salt

## Learning Objectives

- Compare tools
- Pick by use case

## Quick Matrix

| | Ansible | Puppet | Chef | Salt |
|---|---|---|---|---|
| Language | YAML | Puppet DSL | Ruby DSL | YAML + Jinja |
| Model | Push (default) | Pull | Pull | Push or Pull |
| Architecture | Agentless | Master/Agent | Server/Client | Master/Minion |
| Communication | SSH | HTTPS to server | HTTPS to server | ZeroMQ |
| Learning Curve | Low | Medium | High | Medium |
| Speed (small) | Fast | Slower (poll) | Slower (poll) | Very fast |
| Speed (large) | Slows | Scales well | Scales well | Scales massively |
| Event-driven | Limited | No | No | Yes (Reactor) |
| Trend | Most popular | Declining | Declining | Niche |

## Ansible

### Pros
- No agent (just SSH)
- YAML (readable)
- Most adopted today
- Huge collection ecosystem
- Idiomatic for cloud automation
- Easy onboarding

### Cons
- Slow at huge scale (SSH overhead)
- Push model = not continuous reconciliation
- Limited reporting

### Best For
- < 1000 nodes
- Mixed environments
- Day-2 ops
- Ad-hoc tasks
- CI/CD integration
- Cloud automation

## Puppet

### Pros
- Mature; strong at scale
- Declarative DSL
- Reporting via PuppetDB
- Continuous reconciliation
- Strong typing
- r10k workflow

### Cons
- Puppet DSL learning curve
- Agent required
- Slower iteration
- Declining mindshare

### Best For
- Large fleets (1000+)
- Compliance / continuous reconcile
- Mixed OS at scale
- Long-term ops

## Chef

### Pros
- Powerful (Ruby underneath)
- Custom resources
- Test Kitchen + InSpec
- Cookbook ecosystem

### Cons
- Ruby DSL
- Server complexity
- Hosted Chef shutdown (self-host)
- Steepest learning curve
- Declining

### Best For
- Existing Chef shops
- Complex policy
- Programmable infra

## Salt

### Pros
- Very fast (ZeroMQ)
- Event-driven (Reactor)
- Scales massively
- YAML + Jinja
- Push or Pull

### Cons
- Smaller community
- Some complexity (Grains/Pillars/States)
- Niche

### Best For
- 10,000+ nodes
- Event-driven (auto-scale, auto-respond)
- Real-time orchestration

## Performance

### Ansible
- Forks: 5 default; tune to 100s
- Mitogen plugin: faster
- Practical: ~1000 nodes/playbook

### Puppet
- Server compiles per minute (limited by JRuby)
- 10k minions: ~3-4 compile servers
- Scales horizontally

### Chef
- Similar to Puppet
- chef-zero for local

### Salt
- ZeroMQ: sub-second to thousands
- Highstate on 10k: minutes
- Fastest at scale

## Language Comparison

### Ansible
```yaml
- name: Install nginx
  apt:
    name: nginx
    state: present
```

### Puppet
```puppet
package { 'nginx':
  ensure => installed,
}
```

### Chef
```ruby
package 'nginx' do
  action :install
end
```

### Salt
```yaml
nginx:
  pkg.installed: []
```

Similar concepts; different syntax.

## State Management

### Ansible
Push: state on control box.

### Puppet
Pull: state on server (catalogs).

### Chef
Pull: state on server.

### Salt
Both. Master holds states; minions pull.

## Reporting

### Ansible
Limited; AWX/AAP for reports.

### Puppet
PuppetDB; rich reports.

### Chef
Chef Automate.

### Salt
Returners (Elasticsearch, etc.).

## Cloud-Native Era

Trends:
- Containers + K8s reduce config mgmt scope
- Immutable infra (Packer + AMI)
- Cloud-Init for bootstrap
- IaC (Terraform) for infra; minimal config mgmt for OS

Result:
- Ansible: still used (day-2)
- Puppet/Chef: legacy maintenance
- Salt: niche

## Adoption (2025-ish)

```
Ansible:  60%+ of greenfield
Puppet:   long tail
Chef:     long tail
Salt:     specialty
None (immutable + containers): growing fast
```

## Specific Choice Reasons

### Pick Ansible If
- Small-medium fleet
- Already use SSH
- Quick learning
- Mixed cloud
- Hybrid

### Pick Puppet If
- Large fleet (1000+)
- Compliance focus
- Long-term ops
- Already invested

### Pick Chef If
- Already use Chef
- Ruby team
- Complex policy

### Pick Salt If
- 10k+ nodes
- Event-driven
- Real-time

### Pick None If
- Cloud-native
- Containers + K8s
- Immutable infra
- Cloud-Init enough

## Migration Paths

### Puppet → Ansible
Common path. Reasons:
- Simpler
- No agent
- Cloud-friendly

Approach:
1. Parallel run
2. Migrate role by role
3. Decommission Puppet

### Chef → Ansible / Containers
Common.

### Anything → Immutable
Big trend. Convert config mgmt → AMI / image build.

## Hybrid

Often coexist:
- Ansible for ad-hoc + day-2
- Puppet for continuous compliance
- Packer + Ansible for image build (config mgmt within IaC)

## Cost / Operational

| | Setup | Maintenance | Talent |
|---|---|---|---|
| Ansible | Low | Low | Easy hire |
| Puppet | Medium | Medium-High | Harder |
| Chef | Medium | High | Hardest |
| Salt | Medium | Medium | Niche |

## Combination

```
Cloud-Init: bootstrap (universal)
Packer + Ansible: image build (immutable infra)
Ansible: day-2 ops (mutable touch)
Terraform: infrastructure
K8s: orchestration
```

Modern stack.

## FAANGM Style

Most FAANGM:
- Internal tools (custom config mgmt)
- Heavy K8s + immutable
- Less traditional CM
- Some Puppet legacy

But interview prep: know all 4.

## Best Practices

- Pick one primary
- Document why
- Avoid mixing extensively
- Train team
- Plan migration if legacy

## Common Mistakes

- Multiple CM tools in same env (chaos)
- Wrong tool for scale
- No idempotency check
- Skipping testing
- Live without IaC backing

## Quick Refs

```
Quick + simple + small? → Ansible
Large + compliance? → Puppet
Already Chef? → Stay (migration cost) or migrate
Massive event-driven? → Salt
Cloud-native? → Skip CM; use containers + Cloud-Init
```

## Interview Prep

**Junior**: "Name CM tools."

**Mid**: "Differences."

**Senior**: "Choose for scenario."

**Staff**: "CM strategy in cloud-native era."

## Next Topic

→ [T02 — When to Replace with IaC + Containers](T02-Replace-IaC-Containers.md)
