# L11/C02/T05 — Handlers & Notifications

## Learning Objectives

- Use handlers correctly
- Avoid common bugs

## Handler

Task that runs only when notified:
```yaml
tasks:
  - name: Update nginx config
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

If config doesn't change: no restart.
If changes: restart once at end of play.

## Why Handlers

- Avoid restart on every run
- Only when needed
- Run after all tasks (batched)
- Run once even if multiple tasks notify

## When Handlers Run

Default: end of play (after all tasks).

Force earlier:
```yaml
- meta: flush_handlers
```

For: ensure restart before subsequent task depends on it.

## Multiple Notifications

```yaml
- name: Change config A
  template: ...
  notify:
    - Restart nginx
    - Reload logger

- name: Change config B
  template: ...
  notify: Restart nginx
```

Nginx restarts once (even if both tasks change).

## Handler Ordering

Run in handler definition order, NOT notification order:
```yaml
handlers:
  - name: First
    ...
  - name: Second
    ...

# Even if "Second" notified before "First", handlers run in order: First, Second
```

For: control order in handlers section.

## Listen

Multiple handlers respond to one notification:
```yaml
tasks:
  - name: Update config
    template: ...
    notify: nginx config changed

handlers:
  - name: Restart nginx
    listen: nginx config changed
    service:
      name: nginx
      state: restarted

  - name: Update metrics
    listen: nginx config changed
    command: refresh-metrics.sh
```

For: complex orchestration.

## Conditional Notify

```yaml
- name: Change config
  template: ...
  register: result
  notify: Restart nginx
  # Only notifies if task changed
```

Tasks always notify if changed; not if no change.

For: explicit:
```yaml
- name: Change config
  template: ...
  changed_when: false  # Don't notify
```

## Handlers Run Only on Change

If task reports "ok" (not changed): handler not called.

For: idempotent retries don't restart.

## Force Run

```yaml
- meta: flush_handlers
```

Run handlers immediately.

For: depend on handler effect in subsequent task.

```yaml
tasks:
  - name: Update config
    template: ...
    notify: Restart nginx

  - meta: flush_handlers

  - name: Verify service responds
    wait_for: port=80
```

## Failed Handler

If handler fails: play fails (after all hosts).

For: cleanup with always:
```yaml
- block:
    - name: Risky task
      command: ...
      notify: Cleanup
  always:
    - meta: flush_handlers
```

## Handlers in Roles

```
roles/nginx/handlers/main.yml
```

Used by tasks in role. Cross-role:
```yaml
notify: nginx : Restart nginx
```

## Restart vs Reload

```yaml
handlers:
  - name: Reload nginx
    service:
      name: nginx
      state: reloaded
```

Reload: SIGHUP; no downtime.
Restart: stop + start; brief downtime.

For: prefer reload.

## Service States

- `started` (and `enabled: true`): on boot + now
- `restarted`: stop + start (force)
- `reloaded`: SIGHUP (config reread)
- `stopped`
- `enabled`: at boot

## Async Handler

```yaml
handlers:
  - name: Slow restart
    command: slow-restart.sh
    async: 300
    poll: 0  # fire and forget
```

For: long-running.

## Common Pattern

```yaml
- name: Configure app
  hosts: app
  become: true

  tasks:
    - name: Install
      apt:
        name: myapp
        state: present
      notify: Restart myapp

    - name: Render config
      template:
        src: app.conf.j2
        dest: /etc/myapp/app.conf
      notify: Restart myapp

    - name: Render env
      template:
        src: env.j2
        dest: /etc/myapp/env
      notify: Restart myapp

  handlers:
    - name: Restart myapp
      systemd:
        name: myapp
        state: restarted
        daemon_reload: true
```

Any change → one restart.

## Rolling Updates with Handlers

```yaml
- name: Rolling update
  hosts: web
  serial: 1   # one at a time
  tasks:
    - name: Update config
      template: ...
      notify: Restart nginx

  handlers:
    - name: Restart nginx
      service:
        name: nginx
        state: restarted
```

Each host: config + restart, then next.

Combine: serial + handlers + healthcheck.

## Naming Conventions

Use descriptive names:
```yaml
# Good
- name: Restart nginx after config change

# Bad
- name: Restart
```

For: clarity in logs.

## Best Practices

- Handlers for service restart
- One handler name per service
- Use `listen` for orchestration
- flush_handlers when needed
- Test handler triggers
- Backup before template (handler runs after)
- Validate config before reload

## Common Mistakes

- Notify a handler that doesn't exist (silent fail in some Ansible versions)
- Restart inline (not via handler)
- Force restart every run (unnecessary downtime)
- Missing flush_handlers for dependent tasks
- Handlers in wrong order
- Forget changed_when: false for read-only tasks

## Debug Handlers

```bash
ansible-playbook -vvv playbook.yml
# Shows handler notifications
```

## Verify Service

```yaml
- name: Verify service after restart
  wait_for:
    port: 80
    delay: 5
    timeout: 60
```

After flush_handlers; before next phase.

## Quick Refs

```yaml
# Define
handlers:
  - name: Handler name
    service:
      name: svc
      state: restarted

# Notify
- name: Task
  ...
  notify: Handler name

# Force run
- meta: flush_handlers

# Multiple
notify:
  - Handler A
  - Handler B

# Listen
listen: tag-name
```

## Interview Prep

**Junior**: "What's a handler."

**Mid**: "When handlers run."

**Senior**: "flush_handlers use case."

**Staff**: "Rolling update orchestration."

## Next Topic

→ Move to [L11/C03 — Advanced Ansible](../C03/README.md)
