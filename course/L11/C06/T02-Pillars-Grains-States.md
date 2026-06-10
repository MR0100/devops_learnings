# L11/C06/T02 — Pillars, Grains, States

## Learning Objectives

- Use Pillars / Grains / States together
- Build idiomatic Salt

## Three Core Concepts

- **Grains**: facts (static; from minion)
- **Pillars**: secret/sensitive data (from master)
- **States**: desired config (YAML files)

## Grains

```bash
sudo salt 'web01' grains.items
```

Output:
```yaml
os: Ubuntu
osmajorrelease: 22
ipv4: [10.0.0.1, 127.0.0.1]
num_cpus: 4
memory_total: 8192
```

For: targeting, conditional logic.

## Custom Grains

```yaml
# /etc/salt/grains
roles:
  - webserver
env: prod
```

Or via module:
```python
# _grains/myapp.py
def myapp_version():
    return {'myapp_version': '1.2.3'}
```

Sync:
```bash
sudo salt '*' saltutil.sync_grains
```

## Pillar

```yaml
# /srv/pillar/top.sls
base:
  'web*':
    - nginx
    - common

# /srv/pillar/nginx.sls
nginx:
  port: 80
  workers: 4
  ssl_cert: |
    -----BEGIN CERTIFICATE-----
    ...
```

```bash
sudo salt 'web01' pillar.items
```

## Targeting via Pillar

```bash
sudo salt -I 'nginx:port:80' state.apply nginx
```

For: data-driven targeting.

## Pillar Security

Pillars per-minion (only visible to that minion).

```yaml
# /srv/pillar/top.sls
base:
  'web*':
    - webonly  # only web minions see this pillar
```

For: secret isolation.

## States

```yaml
# /srv/salt/nginx/init.sls

include:
  - nginx.install
  - nginx.config
  - nginx.service
```

```yaml
# /srv/salt/nginx/install.sls
nginx:
  pkg.installed: []
```

```yaml
# /srv/salt/nginx/config.sls
/etc/nginx/nginx.conf:
  file.managed:
    - source: salt://nginx/files/nginx.conf.j2
    - template: jinja
    - context:
        port: {{ pillar['nginx']['port'] }}
        workers: {{ pillar['nginx']['workers'] }}
    - require:
      - pkg: nginx
    - watch_in:
      - service: nginx
```

```yaml
# /srv/salt/nginx/service.sls
nginx:
  service.running:
    - enable: True
    - require:
      - pkg: nginx
```

## Top File

```yaml
# /srv/salt/top.sls
base:
  '*':
    - common
  'web*':
    - nginx
  'db*':
    - postgres
  '-G os:RedHat':   # compound matching
    - epel
```

`state.highstate`: applies all matched.

## State Requisites

```yaml
require:        # Must be applied first
  - pkg: nginx
require_in:     # This must be applied before X
  - service: nginx

watch:          # Restart if changes
  - file: /etc/nginx/nginx.conf
watch_in:       # Trigger restart elsewhere

onchanges:      # Run if X changed
  - file: /etc/nginx/nginx.conf

onfail:         # Run if X failed
  - pkg: nginx

prereq:         # Like require but special
  - file: /etc/nginx/nginx.conf
```

For: ordering and reactions.

## Salt Modules in States

```yaml
mymodule.myfunction:
  - param1: value1
```

For: invoking modules from states.

## Includes

```yaml
include:
  - common.base
  - common.users
```

For: composition.

## extend

```yaml
extend:
  /etc/nginx/nginx.conf:
    file.managed:
      - context:
          extra: value
```

For: modify existing state.

## Templates

Jinja in states + files:
```jinja2
{% set workers = pillar.get('nginx:workers', 4) %}
worker_processes {{ workers }};
```

Salt-specific:
- `salt['pkg.version']('nginx')`
- `pillar['key']`
- `grains['os']`

## Conditional States

```yaml
{% if grains['os'] == 'Ubuntu' %}
nginx:
  pkg.installed: []
{% elif grains['os'] == 'CentOS' %}
nginx:
  pkg.installed:
    - name: nginx-stable
{% endif %}
```

## Loops

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

## Macros

```yaml
{% macro vhost(name, port) %}
/etc/nginx/sites/{{ name }}:
  file.managed:
    - contents: "server { listen {{ port }}; ... }"
{% endmacro %}

{{ vhost('site1', 80) }}
{{ vhost('site2', 8080) }}
```

For: DRY.

## State Outputs

```yaml
test_state:
  cmd.run:
    - name: ls /tmp
    - unless: test -f /tmp/exists
```

`unless`: skip if cmd returns 0.
`onlyif`: run only if cmd returns 0.

## Compound Matching

```bash
salt -C 'web* and G@os:Ubuntu and not E@web03' cmd.run 'uptime'
```

- `web*`: glob
- `G@`: grain
- `E@`: regex
- `I@`: pillar

Operators: `and`, `or`, `not`.

## Pillar Inheritance

```yaml
# /srv/pillar/common.sls
ntp_servers:
  - 0.pool.ntp.org

# /srv/pillar/prod.sls
include:
  - common

# Override
log_level: warn
```

For: layered config.

## Salt Vault Module

```yaml
db_password: {{ salt['vault'].read_secret('secret/db', 'password') }}
```

For: secrets from HashiCorp Vault.

## State Apply vs Highstate

- `state.apply nginx`: specific state
- `state.highstate`: all matched in top.sls

## Best Practices

- Pillar for data, secrets
- Grains for targeting (custom roles)
- States minimal logic
- Macros for DRY
- Includes for composition
- Versioning states (Git)
- pre-commit hooks (yamllint, salt-lint)

## Common Mistakes

- Secrets in states (use Pillar)
- All cmd.run (use modules)
- No requisites (random apply order)
- Pillar leaks (wrong targeting)
- No state.show_highstate (debug)

## state.show

```bash
# Show what would run on minion
sudo salt 'web01' state.show_highstate

# Show specific state
sudo salt 'web01' state.show_sls nginx

# Show lowstate (compiled form)
sudo salt 'web01' state.show_lowstate
```

For: debugging.

## Test Mode

```bash
sudo salt 'web01' state.apply nginx test=True
```

Like noop. Shows what would change.

## Quick Refs

```bash
# Grains
salt '*' grains.items / grains.get KEY / grains.setval KEY VAL

# Pillar
salt '*' pillar.items / pillar.get KEY / saltutil.refresh_pillar

# State
salt '*' state.apply NAME
salt '*' state.highstate
salt '*' state.apply test=True
salt '*' state.show_highstate

# Targeting
salt 'GLOB' / -G 'GRAIN:VALUE' / -I 'PILLAR:VALUE' / -E 'REGEX' / -C 'COMPOUND'
```

## Interview Prep

**Mid**: "Pillar vs Grain."

**Senior**: "State requisites."

**Staff**: "Salt state architecture."

## Next Topic

→ Move to [L11/C07 — Comparison & Selection](../C07/README.md)
