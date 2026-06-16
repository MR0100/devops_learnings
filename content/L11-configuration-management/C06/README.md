# L11/C06 — SaltStack

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Master-Minion.md) | Master/Minion, Salt SSH | 0.5 hr |
| [T02](T02-Pillars-Grains-States.md) | Pillars, Grains, States | 1 hr |

## Architecture

```
[Salt Master]
     │ ZeroMQ (or RAET)
     │ persistent pub/sub
     │
┌────┼────┬────────┬────────┐
▼    ▼    ▼        ▼        ▼
Minion Minion Minion Minion ... Minion
```

- Master pushes commands; minions subscribe and execute
- Event bus is bidirectional (minions report)
- Scales to 10K+ nodes

### Modes
- **Master/Minion**: standard, agent installed
- **Salt SSH**: no agent, runs via SSH (slower)
- **Standalone (salt-call --local)**: no master, local apply

## Concepts

### Grains
Facts about a minion (similar to Ansible facts):
- `os`, `os_family`, `osmajorrelease`
- `mem_total`, `num_cpus`
- `ipv4`, `ipv6`
- Custom grains (set in config)

```bash
salt '*' grains.items
salt '*' grains.get os
```

### Pillars
Configuration data assigned to minions. Server-controlled.

```yaml
# /srv/pillar/top.sls
base:
  '*':
    - common
  'web*':
    - web
```

```yaml
# /srv/pillar/web.sls
nginx:
  workers: 8
  user: www-data
```

```bash
salt 'web*' pillar.items
```

### States
What you want the system to look like. YAML + Jinja.

```yaml
# /srv/salt/nginx/init.sls
nginx_package:
  pkg.installed:
    - name: nginx

nginx_config:
  file.managed:
    - name: /etc/nginx/nginx.conf
    - source: salt://nginx/nginx.conf.j2
    - template: jinja
    - require:
      - pkg: nginx_package
    - watch_in:
      - service: nginx_service

nginx_service:
  service.running:
    - name: nginx
    - enable: True
    - require:
      - file: nginx_config
```

### Top File
Maps minions to states:
```yaml
# /srv/salt/top.sls
base:
  '*':
    - common
  'web*':
    - nginx
  'db*':
    - postgres
```

## Common Commands

```bash
# Test minion connectivity
salt '*' test.ping

# Ad-hoc command
salt '*' cmd.run 'uname -a'
salt -G 'os:Ubuntu' cmd.run 'apt update'
salt -E 'web[0-9]+' cmd.run 'uptime'

# Apply states (highstate = run top file)
salt '*' state.apply
salt '*' state.apply nginx          # specific state
salt '*' state.apply test=True      # dry-run

# Show pillar
salt 'web1' pillar.items
salt 'web1' pillar.get nginx:workers
```

## Targeting

```bash
salt '*'                 # all
salt 'web*'              # glob
salt -E 'web[0-9]+'      # regex
salt -G 'os:Ubuntu'      # grain
salt -L 'web1,web2'      # list
salt -I 'env:prod'       # pillar
salt -C 'G@os:Ubuntu and not L@web1'  # compound
```

## Event-Driven Automation

Salt reactor: listen for events, trigger states.

```yaml
# /etc/salt/master.d/reactor.conf
reactor:
  - 'salt/minion/*/start':
    - /srv/reactor/start.sls
  - 'app/error/critical':
    - /srv/reactor/page_oncall.sls
```

This is unique among CM tools — Salt naturally supports event-driven workflows.

## When Salt

- Very large fleets (10K+ minions)
- Need event-driven response
- Want speed (faster than Ansible at large scale)
- Comfortable with Python (Salt is Python)

## Salt SSH vs Ansible

Both are agentless and similar. Salt SSH is less feature-rich than master/minion. Ansible has more ecosystem.

## Interview Themes

- "Salt vs Ansible — when each?"
- "Pillars vs grains"
- "Salt event bus — what does it enable?"
- "Reactor — explain"
