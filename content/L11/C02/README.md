# L11/C02 — Ansible Fundamentals

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Inventory-Variables-Facts.md) | Inventory, Variables, Facts | 1 hr |
| [T02](T02-Playbooks-Plays-Tasks.md) | Playbooks, Plays, Tasks | 1 hr |
| [T03](T03-Roles-Collections.md) | Roles & Collections | 1 hr |
| [T04](T04-Templates-Jinja2.md) | Templates (Jinja2) | 1 hr |
| [T05](T05-Handlers-Notifications.md) | Handlers & Notifications | 0.5 hr |

## Inventory

```ini
# inventory/hosts.ini
[webservers]
web1.example.com ansible_user=ubuntu
web2.example.com ansible_user=ubuntu

[dbservers]
db1.example.com ansible_user=postgres

[production:children]
webservers
dbservers

[production:vars]
env=production
ntp_server=time.example.com
```

Or YAML:
```yaml
all:
  children:
    webservers:
      hosts:
        web1.example.com: {}
        web2.example.com: {}
    dbservers:
      hosts:
        db1.example.com: {}
  vars:
    ansible_python_interpreter: /usr/bin/python3
```

### Dynamic Inventory
Generate inventory from a cloud provider:
- AWS: `aws_ec2` plugin
- Azure: `azure_rm`
- GCP: `gcp_compute`

```yaml
# aws.yml (used with -i aws.yml)
plugin: aws_ec2
regions:
  - us-east-1
keyed_groups:
  - key: tags.Environment
    prefix: env
  - key: tags.Role
    prefix: role
```

## Variables

Hierarchy (low → high precedence):
1. role defaults (`defaults/main.yml`)
2. inventory vars
3. host_vars
4. group_vars
5. play vars
6. task vars
7. `-e` extra vars (highest)

### group_vars / host_vars
```
inventory/
├── hosts.yml
├── group_vars/
│   ├── all.yml          # for everyone
│   ├── webservers.yml
│   └── production.yml
└── host_vars/
    └── web1.example.com.yml
```

### Facts
Auto-gathered at start of each play (about each host):
- `ansible_distribution`, `ansible_os_family`
- `ansible_processor_vcpus`, `ansible_memtotal_mb`
- `ansible_default_ipv4.address`
- `ansible_eth0.ipv4.address`
- ... thousands

Disable for speed: `gather_facts: no`

## Playbooks

A playbook contains plays. A play applies tasks to hosts.

```yaml
- name: Configure web tier
  hosts: webservers
  become: true
  vars:
    nginx_workers: 4
  tasks:
    - name: Install nginx
      apt:
        name: nginx
        state: present
        update_cache: yes

    - name: Copy nginx config
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
        owner: root
        group: root
        mode: '0644'
      notify: Restart nginx

  handlers:
    - name: Restart nginx
      service:
        name: nginx
        state: restarted
```

### Idempotency
Most modules are idempotent: re-running doesn't change state if already converged. Use `state: present` for declarative.

### Common Modules
- `apt` / `yum` / `package` (universal package manager)
- `file` (perms, dirs, symlinks)
- `copy` (push file)
- `template` (Jinja2 render then push)
- `lineinfile` / `blockinfile` (idempotent file edits)
- `service` / `systemd`
- `user` / `group`
- `cron`
- `command` / `shell` (not idempotent by default; use sparingly)
- `uri` (HTTP requests)
- `wait_for` (wait for condition)
- `set_fact`, `register`, `debug`

### Loops
```yaml
- name: Install packages
  apt:
    name: "{{ item }}"
    state: present
  loop:
    - nginx
    - postgresql-client
    - htop

- name: Create users
  user:
    name: "{{ item.name }}"
    uid: "{{ item.uid }}"
    groups: "{{ item.groups }}"
  loop:
    - {name: alice, uid: 1001, groups: admin}
    - {name: bob, uid: 1002, groups: dev}
```

### Conditionals
```yaml
- name: Only on Debian
  apt: name=foo state=present
  when: ansible_os_family == "Debian"

- name: Only if file missing
  template: ...
  when: not foo_file.stat.exists
```

### Register & Debug
```yaml
- name: Run a command
  command: cat /etc/hostname
  register: result

- name: Print result
  debug:
    var: result.stdout
```

## Roles

Reusable units. Standard structure:
```
roles/nginx/
├── defaults/main.yml       # default vars
├── files/                  # static files
├── handlers/main.yml       # handlers
├── meta/main.yml           # role metadata, dependencies
├── tasks/main.yml          # main tasks
├── templates/              # Jinja2 templates
├── tests/
└── vars/main.yml           # role vars (higher precedence than defaults)
```

```yaml
- hosts: webservers
  roles:
    - common
    - nginx
    - { role: app, app_version: "1.2.3" }
```

## Collections

Distribution unit. A collection bundles roles, modules, plugins.

- `ansible-galaxy collection install community.general`
- `requirements.yml` declares collections + roles

```yaml
collections:
  - name: community.general
    version: ">=8.0.0"
  - name: amazon.aws
    version: ">=7.0.0"

roles:
  - src: geerlingguy.docker
    version: "7.0.0"
```

## Templates (Jinja2)

```jinja2
# nginx.conf.j2
worker_processes {{ nginx_workers | default(4) }};

events { worker_connections 1024; }

http {
    upstream app {
        {% for host in groups['webservers'] %}
        server {{ hostvars[host].ansible_default_ipv4.address }}:8080;
        {% endfor %}
    }

    server {
        listen 80;
        server_name {{ ansible_fqdn }};
        location / { proxy_pass http://app; }
    }
}
```

### Filters
- `{{ var | default('x') }}`
- `{{ var | upper }}`
- `{{ var | regex_replace('foo', 'bar') }}`
- `{{ list | join(',') }}`
- `{{ obj | to_yaml }}`
- `{{ obj | to_nice_json }}`

## Handlers

Triggered by `notify:` only when task changes state.

```yaml
- name: Update config
  template: src=app.conf.j2 dest=/etc/app.conf
  notify: Restart app

handlers:
  - name: Restart app
    systemd: name=app state=restarted
```

Handlers run **at end of play** (or use `meta: flush_handlers`).

## Running

```bash
ansible-playbook -i inventory.yml playbook.yml
ansible-playbook -i inventory.yml playbook.yml --check          # dry-run
ansible-playbook -i inventory.yml playbook.yml --diff           # show diffs
ansible-playbook -i inventory.yml playbook.yml --limit web1     # subset
ansible-playbook -i inventory.yml playbook.yml --tags config    # tags
ansible-playbook -i inventory.yml playbook.yml -e env=prod

ansible web1 -i inventory.yml -m ping
ansible web1 -i inventory.yml -a "uptime"
```

## Interview Themes

- "Inventory — static vs dynamic"
- "Variable precedence"
- "Role structure"
- "What makes Ansible idempotent?"
- "Handlers — when use them?"
- "Compare collections and roles"
