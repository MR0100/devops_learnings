# L11/C02/T01 — Inventory, Variables, Facts

## Learning Objectives

- Define inventory
- Use variables and facts effectively

## Inventory

Hosts to manage:
```yaml
# inventory.yml
all:
  hosts:
    web1:
      ansible_host: 10.0.0.1
      ansible_user: ubuntu
    web2:
      ansible_host: 10.0.0.2
  children:
    webservers:
      hosts:
        web1:
        web2:
      vars:
        nginx_version: "1.27"
    databases:
      hosts:
        db1:
          ansible_host: 10.0.0.10
```

## INI Format

```ini
[webservers]
web1 ansible_host=10.0.0.1
web2 ansible_host=10.0.0.2

[databases]
db1 ansible_host=10.0.0.10

[webservers:vars]
nginx_version=1.27
```

YAML preferred for new.

## Groups

Logical grouping:
```yaml
prod:
  children:
    web-prod:
    db-prod:
staging:
  children:
    web-staging:
    db-staging:
```

Run against group:
```bash
ansible-playbook -i inventory.yml --limit webservers playbook.yml
```

## Variables Hierarchy

Precedence (highest to lowest):
1. Extra vars (`-e key=value`)
2. Task vars
3. Block vars
4. Role and include vars
5. Play vars
6. Set facts
7. Registered vars
8. Host vars (host_vars/web1.yml)
9. Group vars (group_vars/webservers.yml)
10. Inventory vars
11. Role defaults

For: deliberate layering.

## host_vars / group_vars

```
inventory.yml
host_vars/
  web1.yml
  web2.yml
group_vars/
  all.yml
  webservers.yml
  databases.yml
```

```yaml
# group_vars/webservers.yml
nginx_workers: 4
nginx_port: 80
```

For: organized vars per host/group.

## Default Variables in Roles

```yaml
# roles/nginx/defaults/main.yml
nginx_workers: 2
nginx_port: 80
```

Lowest precedence; override in group_vars / playbook.

## Facts

Auto-collected by Ansible:
```yaml
- debug: var=ansible_os_family
- debug: var=ansible_default_ipv4.address
- debug: var=ansible_memtotal_mb
```

100s of facts per host. Collected at play start.

## Disable Fact Gathering

```yaml
- hosts: all
  gather_facts: false
  tasks: ...
```

For: speed when facts not needed.

## Custom Facts

```bash
# /etc/ansible/facts.d/custom.fact
[application]
version=1.2.3
```

```yaml
- debug: var=ansible_local.custom.application.version
```

For: app-specific facts.

## Set Facts

```yaml
- set_fact:
    deploy_time: "{{ lookup('pipe', 'date +%s') }}"

- debug: var=deploy_time
```

For: computed at runtime.

## Register

```yaml
- name: Get hostname
  command: hostname
  register: hostname_output

- debug: var=hostname_output.stdout
```

Capture task output.

## Vars in Templates

```jinja2
# nginx.conf.j2
worker_processes {{ nginx_workers }};
listen {{ nginx_port }};
```

Used with template module.

## Encrypted Variables (Vault)

```bash
ansible-vault encrypt secrets.yml
ansible-vault edit secrets.yml
ansible-vault decrypt secrets.yml
```

Or per-string:
```yaml
db_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  6...
```

Run:
```bash
ansible-playbook --ask-vault-pass playbook.yml
# Or
ansible-playbook --vault-password-file ~/.vault_pass.txt playbook.yml
```

For: secrets in repo.

## Dynamic Inventory

```bash
ansible-playbook -i inventory_aws.py playbook.yml
```

inventory_aws.py: queries AWS, builds inventory at runtime.

For: cloud (don't manually maintain).

## AWS Plugin

```yaml
# inventory_aws_ec2.yml
plugin: amazon.aws.aws_ec2
regions:
  - us-east-1
keyed_groups:
  - prefix: tag
    key: tags
```

Discover EC2 by tags.

## Inventory Filter

```bash
# By group
ansible-playbook --limit webservers playbook.yml

# By pattern
ansible-playbook --limit 'web*:!web3' playbook.yml
```

## Inventory Format Detection

Ansible accepts:
- INI
- YAML
- JSON
- Executable (dynamic)

Auto-detected by extension.

## Ad-hoc

```bash
# Ping all
ansible all -m ping

# Run command
ansible webservers -m shell -a "uptime"

# Use specific user
ansible all -u ubuntu --become -m apt -a "name=nginx state=present"
```

For: quick tasks; no playbook needed.

## Sensitive Vars

Use Vault. Or:
```yaml
db_password: "{{ lookup('env', 'DB_PASSWORD') }}"
```

Or vault integration:
```yaml
db_password: "{{ lookup('hashi_vault', 'secret=secret/db:password') }}"
```

## Variable Naming

Convention:
- lowercase_with_underscores
- Prefix by role: `nginx_port`, not `port`
- Avoid generic names

## Best Practices

- group_vars / host_vars hierarchy
- Vault for secrets
- Dynamic inventory for cloud
- Disable gather_facts when not needed (speed)
- Set defaults in roles
- Document required vars

## Common Mistakes

- Hardcoded values in tasks
- Generic var names
- Vault not used (plaintext secrets)
- gather_facts always on (slow)
- Static inventory in cloud

## Quick Refs

```bash
# Inventory check
ansible-inventory --list -i inventory.yml

# Specific host vars
ansible-inventory --host web1 -i inventory.yml

# Ad-hoc
ansible all -m ping
ansible all -m setup  # gather facts
```

## Interview Prep

**Junior**: "What's inventory."

**Mid**: "Variable precedence."

**Senior**: "Dynamic inventory."

**Staff**: "Inventory at scale."

## Next Topic

→ [T02 — Playbooks, Plays, Tasks](T02-Playbooks-Plays-Tasks.md)
