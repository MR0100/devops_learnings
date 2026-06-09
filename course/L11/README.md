# L11 — Configuration Management

## Overview

Configuration management (Ansible, Chef, Puppet, Salt) was central to DevOps' first decade. In the cloud-native era, immutable infrastructure and IaC have displaced much of its scope, but it remains essential for day-2 ops, hybrid environments, and bootstrap.

**7 chapters, 18 topics.**

## Chapter Map

### [C01](C01/) — When Do You Need Config Management
- T01 Mutable vs Immutable Patterns
- T02 Pull vs Push Models

### [C02](C02/) — Ansible Fundamentals
- T01 Inventory, Variables, Facts
- T02 Playbooks, Plays, Tasks
- T03 Roles & Collections
- T04 Templates (Jinja2)
- T05 Handlers & Notifications

### [C03](C03/) — Advanced Ansible
- T01 Dynamic Inventory
- T02 AWX / Ansible Automation Platform
- T03 Custom Modules & Plugins
- T04 Idempotency Patterns

### [C04](C04/) — Puppet
- T01 Architecture (Master/Agent)
- T02 Manifests, Modules, Hiera
- T03 Catalog Compilation

### [C05](C05/) — Chef
- T01 Cookbooks, Recipes, Resources
- T02 Chef Infra & Workstation

### [C06](C06/) — SaltStack
- T01 Master/Minion, Salt SSH
- T02 Pillars, Grains, States

### [C07](C07/) — Comparison & Selection
- T01 Ansible vs Puppet vs Chef vs Salt
- T02 When to Replace with IaC + Containers

## Tool Comparison

| | Ansible | Puppet | Chef | Salt |
|---|---|---|---|---|
| Language | YAML | Puppet DSL | Ruby DSL | YAML + Python |
| Model | Push (SSH) | Pull (agent) | Pull (agent) | Push or Pull |
| Architecture | Agentless | Master/agent | Server/client | Master/minion |
| Learning curve | Low | Medium | High | Medium |
| Best for | Ad-hoc + simple | Large fleets | Complex policy | High scale, event-driven |
| Trend | Most common today | Declining | Declining | Niche |

## Ansible Quick Reference

```yaml
# inventory.yml
all:
  hosts:
    web1:
      ansible_host: 10.0.0.1
      ansible_user: ubuntu
  vars:
    env: production
```

```yaml
# playbook.yml
- name: Configure web servers
  hosts: web1
  become: true
  tasks:
    - name: Install nginx
      apt:
        name: nginx
        state: present
    - name: Copy config
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
      notify: Restart nginx
  handlers:
    - name: Restart nginx
      service:
        name: nginx
        state: restarted
```

```bash
ansible-playbook -i inventory.yml playbook.yml --check  # dry-run
ansible-playbook -i inventory.yml playbook.yml --diff
ansible web1 -a "uname -r"                              # ad-hoc
```

## When to Use Config Management Today

| Scenario | Use |
|---|---|
| Bootstrap a server | Ansible / cloud-init |
| Manage long-lived servers | Yes (CM or Salt) |
| Manage containers | No — use Dockerfile + K8s manifests |
| Manage K8s | Helm/Kustomize/GitOps — not CM |
| Network gear | Yes — Ansible has rich modules |
| Hybrid cloud + on-prem | Yes |
| Disaster recovery runbooks | Yes |

## Pull vs Push

| | Push | Pull |
|---|---|---|
| Examples | Ansible | Puppet, Chef agents |
| Reach | Operator initiates | Each node initiates |
| Scale | Limited by control node | Scales to 10,000s |
| Latency | Immediate | At polling interval |
| Network | Outbound (ops → nodes) | Outbound (nodes → master) |

## Recommended Reading

- *Ansible: Up and Running* — Lorin Hochstein
- *Puppet: Up and Running* — Linda Tomich
- *Learning Chef* — Mischa Taylor

## Interview Relevance

- "When would you use Ansible vs IaC + containers?"
- "Compare push vs pull models"
- "Walk through a real Ansible role you've written"

## Next

→ [L12 — Docker & Container Internals](../L12/README.md)
