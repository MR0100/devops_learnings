# L11/C06/T01 — Master/Minion, Salt SSH

## Learning Objectives

- Understand Salt
- Use minion or SSH mode

## SaltStack

Event-driven config management:
- Master/Minion
- ZeroMQ messaging
- Push (master) or Pull (minion)
- Faster than alternatives at scale

## Architecture

```
Salt Master
   ↕ (ZeroMQ, pub-sub)
Minions (agents on nodes)
```

Master broadcasts; minions listen.

For: real-time, large scale.

## Install Master

```bash
sudo dnf install -y salt-master
sudo systemctl enable salt-master --now
```

Listens on 4505/4506.

## Install Minion

```bash
sudo dnf install -y salt-minion
echo "master: salt.example.com" >> /etc/salt/minion
sudo systemctl enable salt-minion --now
```

## Key Acceptance

```bash
# On master
sudo salt-key -L
# accepted, unaccepted, rejected

sudo salt-key -a web01.example.com
```

Mutual TLS.

## Ad-hoc Commands

```bash
sudo salt '*' test.ping
sudo salt 'web*' cmd.run 'uptime'
sudo salt 'web01' pkg.install nginx
sudo salt 'web*' service.restart nginx
```

Targets:
- Glob: `web*`
- List: `-L 'web01,web02'`
- Regex: `-E 'web.*'`
- Grain: `-G 'os:Ubuntu'`
- Pillar: `-I 'env:prod'`

## States

YAML config files:
```yaml
# /srv/salt/nginx/init.sls
nginx:
  pkg.installed: []
  service.running:
    - enable: True
    - require:
      - pkg: nginx

/etc/nginx/nginx.conf:
  file.managed:
    - source: salt://nginx/files/nginx.conf
    - template: jinja
    - require:
      - pkg: nginx
    - watch_in:
      - service: nginx
```

## Apply State

```bash
sudo salt 'web*' state.apply nginx
sudo salt 'web*' state.highstate
```

## Top File

```yaml
# /srv/salt/top.sls
base:
  'web*':
    - nginx
    - common
  'db*':
    - postgres
    - common
```

`state.highstate`: applies matched states.

## Pillar

Variables, secrets:
```yaml
# /srv/pillar/top.sls
base:
  'web*':
    - nginx
  'db*':
    - postgres
```

```yaml
# /srv/pillar/nginx.sls
nginx:
  port: 80
  workers: 4
```

```bash
sudo salt 'web01' pillar.items
```

## Use Pillar in State

```yaml
nginx:
  pkg.installed: []
  service.running:
    - enable: True
```

Template:
```jinja2
{# nginx.conf jinja #}
worker_processes {{ salt['pillar.get']('nginx:workers', 4) }};
listen {{ salt['pillar.get']('nginx:port', 80) }};
```

## Grains

Static facts:
```bash
sudo salt 'web01' grains.items
```

Like Facter / Ohai.

Examples:
- os
- osmajorrelease
- ipv4
- num_cpus

Set custom:
```yaml
# /etc/salt/grains
roles:
  - webserver
env: prod
```

## Grain Targeting

```bash
sudo salt -G 'roles:webserver' state.highstate
sudo salt -G 'env:prod' pkg.install nginx
```

## Reactor / Event

Event-driven:
```yaml
# /etc/salt/master.d/reactor.conf
reactor:
  - 'salt/minion/*/start':
    - /srv/reactor/start.sls
```

When minion starts: trigger state.

For: auto-provisioning.

## Salt SSH

No agent; SSH-only:
```bash
# /etc/salt/roster
web01:
  host: 10.0.0.1
  user: ubuntu
  sudo: true
```

```bash
sudo salt-ssh '*' test.ping
sudo salt-ssh 'web01' state.apply nginx
```

Like Ansible. For:
- No agent allowed
- One-off
- Bootstrap

## Comparison

| | Master/Minion | Salt SSH |
|---|---|---|
| Agent | Yes | No |
| Speed | Fast (ZeroMQ) | Slower (SSH) |
| Scale | Massive | Hundreds |
| Use | Long-lived fleet | Ad-hoc, bootstrap |

## Multi-Master

For HA:
- Multiple Salt Masters
- Minions failover

For: scale + reliability.

## Syndic

Hierarchical:
```
Master of Masters
   ↓
Syndic (intermediate)
   ↓
Minions
```

For: huge scale (10k+ minions).

## Returners

Send command output to:
- DB
- Elasticsearch
- Slack

```bash
sudo salt 'web*' cmd.run 'uptime' --return elasticsearch
```

For: logging, audit.

## Mine

Minion facts shared:
```yaml
# /etc/salt/minion.d/mine.conf
mine_functions:
  network.ip_addrs: []
```

```bash
sudo salt '*' mine.get '*' network.ip_addrs
```

For: cross-minion data (e.g. cluster discovery).

## Beacons

Minion sends events on conditions:
```yaml
beacons:
  inotify:
    - files:
        /etc/passwd: {}
        /etc/shadow: {}
```

File change → event → master reacts.

For: monitoring + response.

## Modules

Salt commands:
- `pkg.install`
- `service.start`
- `file.managed`
- `cmd.run`
- `user.present`
- `network.ip_addrs`

Hundreds. Modular.

## Custom Modules

Python:
```python
# /srv/salt/_modules/my_module.py
def hello(name):
    return f"Hello, {name}!"
```

Sync:
```bash
sudo salt '*' saltutil.sync_modules
sudo salt 'web01' my_module.hello world
```

## Jinja in States

Powerful templating in YAML:
```yaml
{% for site in pillar.get('sites', []) %}
/etc/nginx/sites/{{ site.name }}:
  file.managed:
    - source: salt://nginx/files/vhost.j2
    - template: jinja
    - context:
        port: {{ site.port }}
{% endfor %}
```

## Tests

Beacons. Salt-formulas.

```bash
kitchen-salt   # test kitchen for Salt
```

For: TDD.

## Vault Integration

```yaml
db_password: {{ salt['vault'].read_secret('secret/db', 'password') }}
```

For: secrets in HashiCorp Vault.

## Use Cases

- Real-time event response (Reactor)
- Massive scale (10k+ minions)
- Mixed agent + agentless (SSH)
- Compliance scanning

## Vs Ansible

| | Salt | Ansible |
|---|---|---|
| Agent | Yes (default) | No |
| Speed | Very fast | Slower SSH |
| Scale | Tens of thousands | Thousands |
| DSL | YAML + Jinja | YAML + Jinja |
| Event | Yes (Reactor) | Limited |
| Learning | Medium | Low |

## When Salt

- Massive fleet
- Event-driven
- Real-time
- Mixed envs

## When Not

- Small fleet (Ansible easier)
- Simple needs
- Team unfamiliar

## Best Practices

- Grains for targeting
- Pillar for data (secrets)
- States for config
- Reactor for automation
- Multi-master for HA
- Versioning Salt states (Git)

## Common Mistakes

- All cmd.run (use modules)
- No Pillar (secrets in states)
- Single master (no HA)
- Unused features (Mine, Beacons) — start simple

## Quick Refs

```bash
# Ad-hoc
salt '*' test.ping
salt -G 'os:Ubuntu' pkg.install nginx

# State
salt '*' state.apply NAME
salt '*' state.highstate

# Pillar
salt '*' pillar.items
salt '*' pillar.get nginx:port

# Grains
salt '*' grains.items
salt '*' grains.get os

# Salt SSH
salt-ssh '*' test.ping

# Key mgmt
salt-key -L / -a / -r / -d
```

## Interview Prep

**Mid**: "Salt vs Ansible."

**Senior**: "Reactor pattern."

**Staff**: "Salt at scale."

## Next Topic

→ [T02 — Pillars, Grains, States](T02-Pillars-Grains-States.md)
