# L11/C02/T04 — Templates (Jinja2)

## Learning Objectives

- Use Jinja2 in Ansible
- Avoid common pitfalls

## Template Module

```yaml
- name: Render config
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    owner: root
    group: root
    mode: '0644'
  notify: Restart nginx
```

Src: roles/X/templates/nginx.conf.j2.

## Jinja2 Basics

### Variables
```jinja2
server_name {{ inventory_hostname }};
listen {{ nginx_port }};
```

### Filters
```jinja2
{{ name | upper }}
{{ name | default('unknown') }}
{{ ip | regex_replace('^([\\d\\.]+).*', '\\1') }}
{{ list | join(', ') }}
{{ list | length }}
```

### Conditionals
```jinja2
{% if env == 'prod' %}
ssl_certificate /etc/ssl/cert.pem;
{% endif %}

{% if nginx_port == 443 %}
ssl on;
{% else %}
ssl off;
{% endif %}
```

### Loops
```jinja2
{% for backend in backends %}
server {{ backend.host }}:{{ backend.port }};
{% endfor %}

{% for host in groups['webservers'] %}
upstream {{ hostvars[host]['ansible_default_ipv4']['address'] }};
{% endfor %}
```

## Complete Example

```jinja2
# nginx.conf.j2
worker_processes {{ nginx_workers | default(4) }};

events {
    worker_connections {{ nginx_connections | default(1024) }};
}

http {
    {% for vhost in vhosts %}
    server {
        listen {{ vhost.port }};
        server_name {{ vhost.name }};

        {% if vhost.ssl %}
        ssl_certificate {{ vhost.ssl_cert }};
        ssl_certificate_key {{ vhost.ssl_key }};
        {% endif %}

        location / {
            proxy_pass {{ vhost.backend }};
            {% for header in vhost.headers | default([]) %}
            proxy_set_header {{ header.name }} {{ header.value }};
            {% endfor %}
        }
    }
    {% endfor %}
}
```

## Whitespace Control

```jinja2
{%- for item in list %}      # Strip leading whitespace
{{ item }}
{% endfor -%}                # Strip trailing
```

For: clean output.

## Filters Reference

### String
```jinja2
{{ s | upper }}
{{ s | lower }}
{{ s | title }}
{{ s | replace('old', 'new') }}
{{ s | trim }}
{{ s | length }}
```

### List
```jinja2
{{ list | first }}
{{ list | last }}
{{ list | min }}
{{ list | max }}
{{ list | unique }}
{{ list | sort }}
{{ list | flatten }}
{{ list | union(other) }}
{{ list | difference(other) }}
{{ list | intersect(other) }}
```

### Dict
```jinja2
{{ dict | dict2items }}
{{ list | items2dict }}
{{ dict.keys() | list }}
```

### Default
```jinja2
{{ var | default('fallback') }}
{{ var | default('fallback', true) }}  # treat empty as missing
```

### JSON / YAML
```jinja2
{{ obj | to_json }}
{{ obj | to_nice_json }}
{{ obj | to_yaml }}
{{ str | from_json }}
{{ str | from_yaml }}
```

### Regex
```jinja2
{{ s | regex_search('pattern') }}
{{ s | regex_findall('pattern') }}
{{ s | regex_replace('old', 'new') }}
```

### Hash
```jinja2
{{ password | password_hash('sha512') }}
{{ s | hash('sha256') }}
```

### Encoding
```jinja2
{{ s | b64encode }}
{{ s | b64decode }}
{{ s | urlencode }}
```

### Path
```jinja2
{{ path | basename }}
{{ path | dirname }}
{{ path | splitext }}
{{ path | realpath }}
```

## Tests

```jinja2
{% if var is defined %}
{% if var is none %}
{% if var is string %}
{% if list is iterable %}
{% if path is file %}
```

## Macros

```jinja2
{% macro render_backend(backend) %}
server {{ backend.host }}:{{ backend.port }} weight={{ backend.weight | default(1) }};
{% endmacro %}

upstream backend {
    {% for b in backends %}
    {{ render_backend(b) }}
    {% endfor %}
}
```

For: DRY.

## Include / Import

```jinja2
{% include 'partial.j2' %}
{% import 'macros.j2' as m %}
{{ m.render_backend(b) }}
```

For: composition.

## Lookups

```yaml
- template:
    src: config.j2
    dest: /etc/app/config
  vars:
    secret: "{{ lookup('hashi_vault', 'secret=secret/app:key') }}"
```

Inside template:
```jinja2
{{ lookup('env', 'HOME') }}
{{ lookup('file', '/etc/somefile') }}
```

## Iterating Inventory

```jinja2
{% for host in groups['webservers'] %}
server {{ hostvars[host].ansible_default_ipv4.address }};
{% endfor %}
```

For: cluster config from inventory.

## Conditional Includes

```jinja2
{% if env == 'prod' %}
  {% include 'prod_settings.j2' %}
{% else %}
  {% include 'dev_settings.j2' %}
{% endif %}
```

## Newlines

```yaml
- template:
    src: file.j2
    dest: /etc/file
    trim_blocks: true
    lstrip_blocks: true
```

Defaults: trim_blocks=true (strips newline after `{% %}`).

## Common Pitfalls

### Undefined var
```jinja2
{{ var }}
# Error if var undefined
```

Solution:
```jinja2
{{ var | default('') }}
```

### YAML in Template
```yaml
- template:
    src: app.yaml.j2
    dest: /etc/app/config.yaml
```

Template can have YAML in it; render with vars.

### Quoting
```jinja2
{{ '"' + name + '"' }}
```

Or:
```jinja2
"{{ name }}"
```

## Backup

```yaml
- template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    backup: true
```

Keeps previous version with timestamp.

## Validate

```yaml
- template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    validate: 'nginx -t -c %s'
```

Runs validation before installing. If fails, file not changed.

For: prevent broken config.

## Diff

Template + --diff shows file changes.

## Best Practices

- `.j2` extension convention
- Comments in Jinja2
- Macros for DRY
- Defaults on vars
- Validate before deploy
- Backup critical configs
- Test rendered output

## Common Mistakes

- Undefined vars (no default)
- Wrong filter (e.g. | default vs `or`)
- Forgetting handler (config doesn't reload)
- Hardcoded values
- No backup
- Whitespace nightmares

## Quick Refs

```jinja2
{{ var }}                         # render
{{ var | filter }}                # filter
{% if x %} ... {% endif %}        # conditional
{% for x in list %} ... {% endfor %}  # loop
{{ hostvars[host].fact }}         # cross-host
{{ lookup('file', '/path') }}     # lookup
```

## Interview Prep

**Junior**: "What's Jinja2."

**Mid**: "Common filters."

**Senior**: "Templating best practices."

**Staff**: "Complex config generation."

## Next Topic

→ [T05 — Handlers & Notifications](T05-Handlers-Notifications.md)
