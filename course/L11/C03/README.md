# L11/C03 — Advanced Ansible

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Dynamic-Inventory.md) | Dynamic Inventory | 0.5 hr |
| [T02](T02-AWX-AAP.md) | AWX / Ansible Automation Platform | 0.5 hr |
| [T03](T03-Custom-Modules.md) | Custom Modules & Plugins | 1 hr |
| [T04](T04-Idempotency-Patterns.md) | Idempotency Patterns | 1 hr |

## Dynamic Inventory

### AWS EC2
```yaml
# inventory/aws.yml
plugin: amazon.aws.aws_ec2
regions:
  - us-east-1
filters:
  instance-state-name: running
hostnames:
  - tag:Name
  - private-ip-address
keyed_groups:
  - key: tags.Environment
    prefix: env
  - key: tags.Role
    prefix: role
compose:
  ansible_host: private_ip_address
```

Result: `ansible-inventory -i aws.yml --graph` shows groups by tag, with private IPs.

### Multiple Sources
```
inventory/
├── static.ini
└── aws.yml
```

```bash
ansible-playbook -i inventory/ playbook.yml
```

## AWX / Ansible Automation Platform (AAP)

UI + API for Ansible at scale.

- **Projects**: Git repos containing playbooks
- **Inventories**: hosts (static or dynamic)
- **Credentials**: SSH keys, cloud creds (vault-stored)
- **Job Templates**: parametrized playbook runs
- **Workflows**: chain templates
- **Schedules**: cron-like
- **Notifications**: Slack, email, webhook

### AWX vs AAP
- **AWX**: open-source upstream
- **AAP (Red Hat)**: commercial, supported, paid

### Why It Helps
- Centralized RBAC
- Audit log of runs
- Self-service (devs can run pre-approved templates)
- API for automation
- Workflow orchestration

## Custom Modules

Write a module when no existing module fits.

```python
#!/usr/bin/python
# library/widget.py

from ansible.module_utils.basic import AnsibleModule
import requests

def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True, type='str'),
            state=dict(default='present', choices=['present', 'absent']),
            endpoint=dict(required=True, type='str'),
            token=dict(required=True, type='str', no_log=True),
        ),
        supports_check_mode=True,
    )
    
    name = module.params['name']
    state = module.params['state']
    
    # Check existing state
    r = requests.get(f"{module.params['endpoint']}/widgets/{name}",
                     headers={"Authorization": f"Bearer {module.params['token']}"})
    exists = r.status_code == 200
    
    changed = False
    if state == 'present' and not exists:
        if not module.check_mode:
            requests.post(f"{module.params['endpoint']}/widgets",
                          json={"name": name})
        changed = True
    elif state == 'absent' and exists:
        if not module.check_mode:
            requests.delete(f"{module.params['endpoint']}/widgets/{name}")
        changed = True
    
    module.exit_json(changed=changed, name=name)

if __name__ == '__main__':
    main()
```

Use:
```yaml
- name: Manage widget
  widget:
    name: my-widget
    state: present
    endpoint: "{{ widget_api }}"
    token: "{{ widget_token }}"
```

## Custom Plugins

- **Filter plugins**: custom Jinja2 filters
- **Lookup plugins**: read external data (file, vault, API)
- **Callback plugins**: hook into events (log, notify)
- **Connection plugins**: how to reach hosts (SSH, WinRM, custom)

## Idempotency Patterns

Goal: re-running the playbook should be a no-op when state is converged.

### Use Native Modules When Possible
```yaml
# Bad
- command: useradd alice
# Good (idempotent)
- user: name=alice state=present
```

### `command`/`shell` Idempotency
Sometimes you have to use these. Add `creates` or `removes`:

```yaml
- command: /opt/setup.sh
  args:
    creates: /var/lib/setup-done    # only run if this doesn't exist

- command: rm /tmp/foo
  args:
    removes: /tmp/foo               # only run if this exists
```

Or check then act:
```yaml
- stat: path=/etc/foo
  register: foo_stat
- command: install_foo
  when: not foo_stat.stat.exists
```

### `changed_when` and `failed_when`
Override default change/fail detection:
```yaml
- command: grep -q pattern /etc/file
  register: result
  changed_when: false
  failed_when: result.rc not in [0, 1]
```

### `block` for Atomicity
```yaml
- block:
    - name: Step 1
      ...
    - name: Step 2
      ...
  rescue:
    - name: Cleanup on failure
      ...
  always:
    - name: Always run
      ...
```

### Avoid Touching Mutable Resources Redundantly
- Use templates, not lineinfile, for whole files
- Use lineinfile carefully; check first

## Performance

### Parallelism
```ini
# ansible.cfg
[defaults]
forks = 50
```

Ansible forks to that many at a time.

### Pipelining
Reduces SSH connections:
```ini
[ssh_connection]
pipelining = True
control_path = /tmp/ansible-%%C
```

### Fact Caching
```ini
[defaults]
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible-facts
fact_caching_timeout = 86400
```

### Async Tasks
Long-running:
```yaml
- name: Long task
  command: /opt/long-script.sh
  async: 3600
  poll: 30
```

## Mitogen (3rd-Party)

Mitogen reduces SSH overhead with persistent connections; can speed Ansible 5-10×.

```bash
pip install mitogen
```

```ini
[defaults]
strategy_plugins = /path/to/mitogen/ansible_mitogen/plugins/strategy
strategy = mitogen_linear
```

## Vault (Secrets in Ansible)

```bash
ansible-vault create secrets.yml
ansible-vault edit secrets.yml
ansible-vault encrypt vars/db.yml
ansible-vault decrypt vars/db.yml
ansible-vault view vars/db.yml
```

Run playbook with vault password:
```bash
ansible-playbook play.yml --ask-vault-pass
ansible-playbook play.yml --vault-password-file ~/.vault_pass
```

Encrypt individual variable:
```yaml
db_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  3461636430...
```

Use AWS Secrets Manager / Vault for production instead of `ansible-vault` for shared secrets.

## Interview Themes

- "Dynamic inventory — how?"
- "Custom module — when and how?"
- "Idempotency tricks for command/shell"
- "Ansible at scale — performance tactics"
- "Ansible Vault vs HashiCorp Vault"
