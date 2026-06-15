# L11/C03/T04 — Idempotency Patterns

## Learning Objectives

- Write idempotent playbooks
- Avoid common anti-patterns

## Idempotency

Running task N times = running once. State converges.

For Ansible: critical. Reruns happen.

## Built-in Module Behavior

Most modules: idempotent.
- `apt`/`yum`: check if installed
- `file`: check if exists / right perms
- `template`: check if content matches
- `service`: check if started

For: use modules, not raw commands.

## Anti-Pattern: shell/command

```yaml
# BAD
- shell: cp /src /dst
```

Runs every time; always "changed".

Better:
```yaml
- copy:
    src: /src
    dest: /dst
```

Only copies if different.

## When You Need shell

Use `creates` / `removes`:
```yaml
- shell: my-installer.sh
  args:
    creates: /opt/my-app/installed
```

Runs only if /opt/my-app/installed doesn't exist.

For: shell idempotent.

## changed_when

```yaml
- shell: check-status.sh
  register: result
  changed_when: false  # never report changed
```

For: read-only commands.

## failed_when

```yaml
- shell: maybe-error.sh
  register: result
  failed_when: result.rc != 0 and 'expected' not in result.stderr
```

For: custom failure logic.

## Patterns

### Check Then Modify
```yaml
- name: Check if user
  command: id alice
  register: user_check
  failed_when: false
  changed_when: false

- name: Create user
  user:
    name: alice
  when: user_check.rc != 0
```

(Most modules do this internally; for raw cmd cases.)

### File Marker
```yaml
- shell: configure-app.sh
  args:
    creates: /var/lib/configured.flag

- file:
    path: /var/lib/configured.flag
    state: touch
```

After running, touch flag. Next run skips.

### Compare Hashes
```yaml
- stat:
    path: /etc/myapp/config
    get_checksum: true
  register: current

- set_fact:
    new_checksum: "{{ lookup('file', 'config.j2') | hash('sha256') }}"

- copy:
    src: config
    dest: /etc/myapp/config
  when: current.stat.checksum != new_checksum
```

(Or just use `template` / `copy` directly.)

## Common Modules

### file
Manage file presence, perms:
```yaml
- file:
    path: /opt/app
    state: directory
    owner: app
    mode: '0755'
```

### copy
Idempotent file copy:
```yaml
- copy:
    src: app.conf
    dest: /etc/app.conf
    owner: root
    mode: '0644'
```

### template
Render + copy idempotent:
```yaml
- template:
    src: app.j2
    dest: /etc/app.conf
```

### lineinfile
Single line in file:
```yaml
- lineinfile:
    path: /etc/hosts
    line: '1.2.3.4 myhost'
    state: present
```

### blockinfile
Block (idempotent via markers):
```yaml
- blockinfile:
    path: /etc/sysctl.conf
    block: |
      net.ipv4.ip_forward = 1
      net.ipv6.conf.all.forwarding = 1
    marker: "# {mark} ANSIBLE MANAGED"
```

### replace
Regex replace:
```yaml
- replace:
    path: /etc/myapp.conf
    regexp: '^bind ='
    replace: 'bind = 0.0.0.0'
```

### service
Manage service state:
```yaml
- service:
    name: nginx
    state: started
    enabled: true
```

### user
Manage user:
```yaml
- user:
    name: app
    groups: docker
    state: present
```

### apt / yum / dnf
Manage packages:
```yaml
- apt:
    name: nginx
    state: present
    update_cache: true
```

`state: latest` upgrades; not idempotent (re-checks every run; may upgrade).

### git
Clone / update:
```yaml
- git:
    repo: https://github.com/me/code.git
    dest: /opt/code
    version: v1.0
```

## Force-Idempotent for shell

```yaml
- shell: |
    if ! systemctl is-active myapp >/dev/null 2>&1; then
      systemctl start myapp
    fi
  register: result
  changed_when: "'started' in result.stdout"
```

(Or just use service module.)

## Database Migrations

Often non-idempotent (DDL changes).

Pattern:
```yaml
- shell: alembic upgrade head
  register: result
  changed_when: "'Running' in result.stdout"
```

Or schema tools handle it.

## Configs that Self-Heal

Some apps detect config drift and self-correct. Don't fight it.

For: trust the app.

## Restart Patterns

```yaml
- template:
    src: app.conf.j2
    dest: /etc/app.conf
  notify: Restart app
```

Restart only on change.

## Validate Before Apply

```yaml
- template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    validate: 'nginx -t -c %s'
```

If validation fails: don't apply.

## Backup Before Change

```yaml
- template:
    src: config.j2
    dest: /etc/myapp/config
    backup: true
```

Saves previous version.

## Tags for Selective Runs

```yaml
- name: Config
  template: ...
  tags: config

- name: Install
  apt: ...
  tags: install
```

```bash
ansible-playbook --tags config playbook.yml
```

For: targeted fixes.

## Check Mode (--check)

```bash
ansible-playbook --check playbook.yml
```

Shows what would change. Most modules support.

For: validation.

## Diff Mode (--diff)

```bash
ansible-playbook --diff playbook.yml
```

Shows file content changes.

For: review.

## Avoid Restart Loops

```yaml
# BAD
- service:
    name: nginx
    state: restarted   # Always restarts!

# GOOD
- template:
    ...
  notify: Restart nginx

# Handler only runs on change.
```

## Avoid State Drift

Run playbook regularly (cron or AWX schedule):
- Detects drift
- Reconciles

For: continuous compliance.

## Best Practices

- Use modules over shell
- Idempotency check (run twice; second = ok)
- `creates`/`removes` for shell
- `changed_when: false` for read-only
- Validate config before apply
- Handlers for restarts
- Backup critical files
- Test --check

## Common Mistakes

- shell everywhere (no idempotency)
- `state: latest` accidentally (creates churn)
- Restart in tasks (always restarts)
- Missing changed_when (false positives)
- No backup
- Skipping --check

## Idempotency Test

```bash
ansible-playbook playbook.yml
ansible-playbook playbook.yml
# Second run: 0 changed
```

If second shows changes: not idempotent. Fix.

## Molecule

```bash
molecule test
```

Runs:
1. Create
2. Converge (first run)
3. Idempotence (second run; must = 0 changed)
4. Verify
5. Destroy

For: automated idempotency check.

## Quick Refs

```yaml
# Idempotent
- module:
    name: x
    state: present

# shell idempotent
- shell: cmd
  args:
    creates: /flag

# read-only
- shell: cmd
  changed_when: false

# validate
- template:
    validate: 'cmd %s'
```

## Interview Prep

**Junior**: "What's idempotency."

**Mid**: "Make shell idempotent."

**Senior**: "Idempotency patterns."

**Staff**: "Continuous reconciliation strategy."

## Next Topic

→ Move to [L11/C04 — Puppet](../C04/README.md)
