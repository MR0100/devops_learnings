# L11/C02/T03 — Roles & Collections

## Learning Objectives

- Structure roles
- Use Collections from Galaxy

## Role

Reusable, structured unit:
```
roles/
  nginx/
    defaults/main.yml      # default vars
    vars/main.yml          # high-priority vars
    tasks/main.yml         # entry tasks
    handlers/main.yml      # handlers
    templates/             # j2 files
    files/                 # static
    meta/main.yml          # role metadata
    README.md
    tests/
```

## Create Role

```bash
ansible-galaxy init nginx
```

Generates skeleton.

## Use Role

```yaml
- hosts: webservers
  roles:
    - nginx
    - { role: app, version: "1.0" }
```

Roles run in order; before tasks.

## Role with Vars

```yaml
- hosts: webservers
  roles:
    - role: nginx
      vars:
        nginx_port: 8080
```

## tasks/main.yml

```yaml
- name: Install nginx
  apt:
    name: nginx
    state: present

- name: Configure
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
  notify: Restart nginx
```

## defaults/main.yml

```yaml
nginx_port: 80
nginx_workers: 4
nginx_user: www-data
```

Lowest precedence; override in group_vars.

## meta/main.yml

```yaml
galaxy_info:
  author: alice
  description: Nginx role
  license: MIT
  min_ansible_version: 2.14
  platforms:
    - name: Ubuntu
      versions:
        - jammy
dependencies:
  - role: common
```

Dependencies run first.

## handlers/main.yml

```yaml
- name: Restart nginx
  service:
    name: nginx
    state: restarted
```

## templates/

Jinja2 files:
```
templates/nginx.conf.j2
```

Used:
```yaml
- template:
    src: nginx.conf.j2  # relative to templates/
    dest: /etc/nginx/nginx.conf
```

## Role Structure Benefits

- Reusable across projects
- Testable in isolation
- Encapsulates concerns
- Versioned

## Galaxy

Public repo of roles + collections:
```bash
ansible-galaxy install geerlingguy.nginx
```

Installs to ~/.ansible/roles or roles/.

## requirements.yml

```yaml
roles:
  - name: geerlingguy.nginx
    version: 3.1.4
  - src: git+https://github.com/me/myrole.git
    name: myrole
    version: main

collections:
  - name: community.general
    version: ">=10.0.0"
  - name: ansible.posix
```

```bash
ansible-galaxy install -r requirements.yml
```

## Collections

Bundle of:
- Modules
- Roles
- Plugins
- Playbooks

Namespace: `namespace.collection`.

```bash
ansible-galaxy collection install community.general
```

Use:
```yaml
- community.general.ufw:
    rule: allow
    port: 22
```

## Built-in Collections

- `ansible.builtin` (always)
- `ansible.posix` (Linux utilities)
- `community.general` (huge)
- `community.crypto`
- `amazon.aws`
- `google.cloud`
- `azure.azcollection`
- `kubernetes.core`

## FQCN Importance

```yaml
# Old (still works but discouraged)
- apt: name=nginx

# New
- ansible.builtin.apt:
    name: nginx
```

For: clarity, future compat.

## Role Variables Best Practice

```
defaults/main.yml: safe defaults
vars/main.yml: rarely overridden (high precedence)
```

Most config: defaults.
Override: group_vars / play.

## Role Composition

```yaml
- hosts: web
  roles:
    - common      # base packages
    - hardening   # CIS benchmarks
    - nginx       # web server
    - app         # application
    - monitoring  # agents
```

Layered approach.

## Role Dependencies

```yaml
# roles/app/meta/main.yml
dependencies:
  - role: nginx
  - role: postgres-client
```

Auto-applied before role.

For: implicit deps.

## Argument Spec

```yaml
# meta/argument_specs.yml
argument_specs:
  main:
    short_description: Configure nginx
    options:
      nginx_port:
        type: int
        default: 80
      nginx_workers:
        type: int
        required: false
```

Validates inputs.

## Testing

### Molecule
```bash
pip install molecule molecule-docker
cd roles/nginx
molecule init scenario
molecule test
```

Runs role in container; verifies.

## Versioning

- Tag releases (semver)
- Pin in requirements.yml
- Test before upgrade

## Ansible Galaxy Hub

Galaxy → public.
Automation Hub → Red Hat curated (paid).

## Role Search

```bash
ansible-galaxy search nginx
ansible-galaxy info geerlingguy.nginx
```

## Private Galaxy

Self-host:
- Pulp
- Galaxy NG

For: enterprise roles internal.

## Best Practices

- One role per concern
- Defaults sane
- Document required vars
- Test (Molecule)
- Pin versions
- Public Galaxy for community roles (review first)
- FQCN everywhere

## Common Mistakes

- Monolithic role (untestable)
- Hardcoded values
- No README
- No tests
- Unpinned versions
- Magic side effects

## Real Examples

- geerlingguy.docker
- geerlingguy.nginx
- ansible-collections/community.general
- ansible/collection-template

## Quick Refs

```bash
# Galaxy
ansible-galaxy install geerlingguy.nginx
ansible-galaxy collection install community.general
ansible-galaxy install -r requirements.yml

# Init
ansible-galaxy init my-role

# List
ansible-galaxy list
```

## Interview Prep

**Junior**: "What's a role."

**Mid**: "Role structure."

**Senior**: "Collections vs roles."

**Staff**: "Role library at scale."

## Next Topic

→ [T04 — Templates (Jinja2)](T04-Templates-Jinja2.md)
