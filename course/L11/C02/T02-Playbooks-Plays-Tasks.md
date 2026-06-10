# L11/C02/T02 — Playbooks, Plays, Tasks

## Learning Objectives

- Structure playbooks
- Write idempotent tasks

## Playbook

YAML file; collection of plays:
```yaml
# playbook.yml
- name: Configure web servers
  hosts: webservers
  become: true
  tasks:
    - name: Install nginx
      ansible.builtin.apt:
        name: nginx
        state: present

    - name: Start nginx
      ansible.builtin.service:
        name: nginx
        state: started
        enabled: true
```

## Run

```bash
ansible-playbook -i inventory.yml playbook.yml
ansible-playbook --check playbook.yml      # dry run
ansible-playbook --diff playbook.yml       # show changes
ansible-playbook --limit web1 playbook.yml # one host
ansible-playbook --tags install playbook.yml
ansible-playbook -e env=prod playbook.yml
```

## Play Structure

```yaml
- name: Play name (description)
  hosts: targets
  become: true|false   # sudo
  gather_facts: true|false
  vars: {...}
  vars_files:
    - secrets.yml
  pre_tasks: [...]
  roles: [...]
  tasks: [...]
  post_tasks: [...]
  handlers: [...]
```

## Tasks

```yaml
- name: Install package
  ansible.builtin.apt:
    name: nginx
    state: present
  become: true
  when: ansible_os_family == "Debian"
  tags: install
```

Each task: module + arguments + control.

## Module FQCN

Modern: `ansible.builtin.apt`.
Old: `apt`.

For collections: `community.general.X`.

For: forward compat, use FQCN.

## Idempotency

Modules check current state; act if different.

```yaml
- name: Ensure user
  ansible.builtin.user:
    name: appuser
    state: present
```

Run 100 times: same result.

For: rerun safely.

## State Parameter

Common pattern:
```yaml
state: present | absent | started | stopped | latest
```

For declarative behavior.

## When

```yaml
- name: Debian-only task
  apt: name=nginx
  when: ansible_os_family == "Debian"

- name: Complex condition
  debug: msg="High mem"
  when: ansible_memtotal_mb > 8000 and env == "prod"
```

## Loop

```yaml
- name: Install many
  apt:
    name: "{{ item }}"
  loop:
    - nginx
    - git
    - curl

- name: Loop with dict
  user:
    name: "{{ item.name }}"
    groups: "{{ item.groups }}"
  loop:
    - { name: alice, groups: 'admin' }
    - { name: bob, groups: 'users' }
```

## Block

```yaml
- block:
    - name: Task 1
      command: ...
    - name: Task 2
      command: ...
  rescue:
    - name: On failure
      debug: msg="failed!"
  always:
    - name: Cleanup
      command: ...
```

For: try/catch/finally semantics.

## Tags

```yaml
- name: Install
  apt: ...
  tags:
    - install
    - bootstrap
```

Run:
```bash
ansible-playbook --tags install playbook.yml
ansible-playbook --skip-tags slow playbook.yml
```

For: selective runs.

## Privilege Escalation

```yaml
- name: Task as root
  command: ...
  become: true
  become_user: root  # default
  become_method: sudo  # default
```

Per-task or play-level.

## Handlers

```yaml
tasks:
  - name: Update config
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

Handlers run after tasks; only if notified; once per play.

## Run Strategy

```yaml
- hosts: all
  strategy: free     # don't wait between hosts
# Or
  strategy: linear   # default; sync
```

For speed: free.

## Forks

```bash
ansible-playbook -f 50 playbook.yml
```

Parallel hosts (default 5). Tune up for big inventory.

## Async

```yaml
- name: Long task
  command: long-running-script.sh
  async: 3600       # max seconds
  poll: 10          # check every 10s
```

Or fire-and-forget:
```yaml
async: 3600
poll: 0           # don't wait
```

## Check Mode (--check)

```yaml
- name: Always run check
  command: ls /
  check_mode: false  # skip in check mode
```

Most modules support check; some don't.

## Diff (--diff)

```bash
ansible-playbook --diff playbook.yml
# Shows file diffs
```

For: see what would change.

## Imports / Includes

### Static (import)
```yaml
- import_tasks: install.yml
- import_playbook: site.yml
```

Resolved at parse time.

### Dynamic (include)
```yaml
- include_tasks: "{{ os }}.yml"
```

Resolved at runtime; supports vars.

## Roles

```yaml
- hosts: web
  roles:
    - common
    - nginx
    - { role: app, version: "1.0" }
```

Encapsulates tasks, handlers, vars, files.

(More in T03.)

## Vars in Tasks

```yaml
- name: Templated
  debug:
    msg: "Hostname is {{ inventory_hostname }}, env is {{ env }}"
```

Jinja2 interpolation.

## Failed When

```yaml
- name: Custom failure
  command: check-status.sh
  register: result
  failed_when: result.rc != 0 and 'expected' not in result.stderr
```

Override default fail behavior.

## Changed When

```yaml
- name: Conditional changed
  command: something
  register: result
  changed_when: "'modified' in result.stdout"
```

Don't mark changed unless output indicates.

## Best Practices

- FQCN modules
- Idempotent tasks
- Tags for partial runs
- Handlers for service restarts
- block/rescue for cleanup
- Test with --check / --diff
- Sensible become scope
- No hardcoded passwords (Vault)

## Common Mistakes

- shell/command when module exists (loses idempotency)
- become at play level when only some tasks need it
- Missing handlers (config change without restart)
- Too many tags (noise)
- Run as root unnecessarily

## Quick Refs

```bash
# Run
ansible-playbook playbook.yml
ansible-playbook --check --diff playbook.yml
ansible-playbook --tags X --skip-tags Y playbook.yml
ansible-playbook --limit GROUP_OR_HOST playbook.yml
ansible-playbook -e key=val playbook.yml

# Verbose
ansible-playbook -v / -vv / -vvv

# Syntax check
ansible-playbook --syntax-check playbook.yml
```

## Interview Prep

**Junior**: "What's a playbook."

**Mid**: "Handlers vs tasks."

**Senior**: "Idempotency."

**Staff**: "Playbook at scale."

## Next Topic

→ [T03 — Roles & Collections](T03-Roles-Collections.md)
