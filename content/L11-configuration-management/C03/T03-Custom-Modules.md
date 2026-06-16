# L11/C03/T03 — Custom Modules & Plugins

## Learning Objectives

- Write custom modules
- Understand plugin types

## Module

Reusable task unit. Built-ins: 1000+.

Custom: Python script in `library/`.

## Simple Module

```python
# library/my_module.py
#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule

def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            state=dict(type='str', default='present', choices=['present', 'absent']),
        ),
        supports_check_mode=True
    )

    name = module.params['name']
    state = module.params['state']

    # Check current state
    current = check_state(name)
    changed = False

    if state == 'present' and not current:
        if not module.check_mode:
            create(name)
        changed = True
    elif state == 'absent' and current:
        if not module.check_mode:
            delete(name)
        changed = True

    module.exit_json(changed=changed, name=name, state=state)

def check_state(name):
    # Implementation
    return False

def create(name):
    pass

def delete(name):
    pass

if __name__ == '__main__':
    main()
```

## Use Custom Module

```yaml
- name: Use custom
  my_module:
    name: thing
    state: present
```

Module found in:
- `library/` next to playbook
- Role's `library/`
- Configured `library` path

## Module Requirements

- Idempotent
- Check mode support
- JSON output
- Exit codes
- Reasonable args

## Check Mode

```python
if module.check_mode:
    module.exit_json(changed=changed, ...)
    return

# Actually do the change
```

For: `--check` to work.

## Return Values

```python
module.exit_json(
    changed=True,
    result='success',
    meta={'key': 'value'}
)

module.fail_json(
    msg="What went wrong",
    rc=1
)
```

## Argument Spec

```python
argument_spec=dict(
    name=dict(type='str', required=True),
    age=dict(type='int', default=0),
    active=dict(type='bool', default=True),
    tags=dict(type='list', elements='str'),
    config=dict(type='dict'),
    password=dict(type='str', no_log=True),
)
```

`no_log=True`: don't log password in output.

## Plugin Types

Modules: tasks.
Plugins: extend Ansible itself.

Types:
- Action
- Cache
- Callback
- Cliconf
- Connection
- Filter
- Inventory
- Lookup
- Strategy
- Test
- Vars

## Filter Plugin

```python
# filter_plugins/my_filters.py

def add_prefix(value, prefix):
    return f"{prefix}{value}"

class FilterModule(object):
    def filters(self):
        return {
            'add_prefix': add_prefix,
        }
```

Use:
```jinja2
{{ name | add_prefix('user_') }}
```

## Lookup Plugin

```python
# lookup_plugins/my_lookup.py

from ansible.plugins.lookup import LookupBase

class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        return [f"result-{t}" for t in terms]
```

Use:
```yaml
- debug:
    msg: "{{ lookup('my_lookup', 'foo') }}"
```

## Callback Plugin

Custom output formatting:
```python
# callback_plugins/my_callback.py

from ansible.plugins.callback import CallbackBase

class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'my_callback'

    def v2_playbook_on_task_start(self, task, is_conditional):
        print(f"Task: {task.get_name()}")
```

## Connection Plugin

Custom transport (e.g. via API):
```python
# connection_plugins/my_conn.py
```

For: non-SSH connections.

## Module Documentation

```python
DOCUMENTATION = '''
---
module: my_module
short_description: Manage thing
description:
  - Detailed description.
options:
  name:
    description: Name of the thing
    required: true
    type: str
'''

EXAMPLES = '''
- name: Create
  my_module:
    name: foo
    state: present
'''

RETURN = '''
name:
  description: Name
  returned: always
  type: str
'''
```

For: `ansible-doc my_module`.

## Distribution

Custom modules: ship in:
- Collection (modern)
- Roles' library/
- Repo library/

For Galaxy: build collection.

## Collection Structure

```
my_namespace/
  my_collection/
    galaxy.yml
    plugins/
      modules/
        my_module.py
      filter/
      lookup/
    roles/
    tests/
```

```bash
ansible-galaxy collection build
ansible-galaxy collection publish
```

## Testing Modules

### Unit tests
```python
# tests/unit/test_my_module.py
import unittest
from plugins.modules import my_module

class TestMyModule(unittest.TestCase):
    def test_create(self):
        ...
```

### Integration tests
Real run; verify.

## ansible-test

```bash
ansible-test units
ansible-test integration
ansible-test sanity
```

For: built-in test harness.

## When Custom Module

- No existing module
- Existing module clunky for your use
- Reusable across many playbooks
- API integration

For one-off: use `uri` / `command` / `shell`.

## When Custom Filter

- Reuse logic in templates
- Complex transforms
- Org-specific naming

## When Custom Lookup

- Pull from custom data source
- Computed at runtime
- Reusable across vars

## Action Plugin

Runs on control node (not target):
```python
class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        result = super().run(tmp, task_vars)
        # Custom logic
        return result
```

For: pre-processing args, calling module remotely.

## Best Practices

- Idempotent
- Check mode
- Argument spec strict
- DOCUMENTATION block
- Tests (unit + integration)
- Distribute via collection
- Version semver

## Common Mistakes

- Not idempotent
- No check mode
- Hardcoded paths
- No error handling
- Missing DOCUMENTATION
- Library scattered (not collection)

## Quick Refs

```bash
# Doc
ansible-doc my_module

# Test
ansible-test units --target plugins/modules/my_module.py
ansible-test sanity

# Build collection
ansible-galaxy collection build
```

## Interview Prep

**Mid**: "Custom module."

**Senior**: "Plugin types."

**Staff**: "Ansible extension at scale."

## Next Topic

→ [T04 — Idempotency Patterns](T04-Idempotency-Patterns.md)
