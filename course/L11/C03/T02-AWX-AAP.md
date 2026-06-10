# L11/C03/T02 — AWX / Ansible Automation Platform

## Learning Objectives

- Use AWX for centralized Ansible
- Compare to alternatives

## AWX

Open-source Ansible web UI:
- Job runs
- Inventory mgmt
- Credentials
- Schedules
- RBAC
- Audit

Upstream of Red Hat Ansible Automation Platform (AAP).

## Install (K8s)

```bash
# AWX Operator
kubectl create namespace awx
kubectl apply -k github.com/ansible/awx-operator/config/default
kubectl apply -f awx-instance.yaml
```

For: K8s-native.

## Concepts

### Project
Source of playbooks (Git repo).

### Inventory
Hosts (static or dynamic).

### Credentials
SSH keys, cloud auth, vault keys.

### Template
Defines a job: playbook + inventory + credentials.

### Job
Execution of template.

### Schedule
Cron-like trigger.

### Workflow
Chain templates with conditions.

## Run Job

UI:
1. Create credential (SSH key)
2. Add project (Git URL)
3. Sync project
4. Create inventory
5. Add template
6. Launch

CLI:
```bash
awx job_templates launch my-template
```

## RBAC

```
Org → Team → User
   → Project / Inventory / Credential
   → Template
```

Permissions:
- View
- Execute
- Admin

For: control who runs what.

## Credentials

Vault-backed:
- SSH keys
- AWS keys (or use OIDC)
- Vault password
- Ansible Vault password

For: encrypted; not in repo.

## Workflows

```
Trigger → Job A (success) → Job B
                (fail) → Notify
        → Job C (always) → Cleanup
```

For: complex orchestration.

## Surveys

Custom UI for runtime vars:
```
"Environment": prod / staging
"Version": text input
```

Job runs with `-e env=prod version=1.0`.

For: self-service.

## Notifications

- Slack
- Email
- Webhook
- PagerDuty
- ServiceNow

On job success / failure.

## Schedules

```
Daily 2 AM: patch playbook
Weekly Mon 1 AM: backup
On-demand: deploy
```

## Job Output

- Real-time log streaming
- Per-task output
- Search / filter
- Archived

For: debugging, audit.

## Logging

Audit log: who ran what when.

For: compliance.

## Isolated Nodes

For air-gapped: run jobs from local AWX instance to networks without direct AWX access.

For: regulated environments.

## Execution Environments

Containers for Ansible runtime:
- Custom Python deps
- Custom collections
- Versioned

```yaml
execution_environment: my-ee:v1
```

For: reproducible Ansible runtime.

## Build EE

```bash
ansible-builder build --tag my-ee:v1
```

ee-supplemental-build-steps for additions.

## AAP vs AWX

AAP: Red Hat product (paid):
- Support
- Curated content
- Automation Hub (private Galaxy)
- Insights (analytics)

AWX: open source upstream:
- Free
- Same features mostly
- Community support

For prod: AAP often. For prototyping / smaller: AWX.

## Comparison to Alternatives

| | AWX/AAP | Rundeck | Jenkins (Ansible plugin) | Custom |
|---|---|---|---|---|
| Ansible-native | yes | partial | partial | manual |
| RBAC | yes | yes | yes | manual |
| Inventory mgmt | yes | yes | manual | manual |
| Workflows | yes | yes | yes | depends |
| Cost | free / paid | free / paid | free | engineer time |

## Use Cases

### Compliance
Scheduled CIS benchmarks; audit log.

### Patching
Coordinated patching across fleet.

### Self-Service
Devs trigger deployments via UI.

### DR
Workflow: bring up DR site.

## Tower Survey Example

```
"Target Hosts": multi-select from inventory
"App Version": v1.0, v1.1, v1.2
"Run Migrations": yes/no
```

Job runs with selected vars.

## API

```bash
# Launch via API
curl -X POST https://awx/api/v2/job_templates/5/launch/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{"extra_vars": "version: 1.0"}'
```

For: external integrations.

## GitOps Pattern

```
Git push → CI runs → Triggers AWX template
   ↓
Job runs Ansible against fleet
   ↓
Reports back to Git as PR comment
```

For: traceable changes.

## HA

- Multiple AWX instances
- DB cluster (Postgres)
- Shared task queue (Redis)

For prod scale.

## Best Practices

- Git-backed projects (no UI edits)
- Credentials encrypted
- RBAC strict
- Workflows for complex
- Surveys for self-service
- Notifications for failures
- Audit logs reviewed

## Common Mistakes

- Credentials in playbooks (use AWX creds)
- UI-edited playbooks (no versioning)
- Wide-open RBAC
- No notifications (silent failures)
- No EE (Python deps drift)

## Alternatives

### Semaphore
Open-source Ansible UI. Lighter.

### Rundeck
Generic job runner; supports Ansible.

### Jenkins
Ansible plugin; CI integration.

### CI/CD (GitHub Actions, GitLab)
Run Ansible from pipelines.

For modern: GitHub Actions + Ansible common.

## Cloud Alternatives

- AWS Systems Manager (somewhat similar; AWS-only)
- Azure Automation (Azure-only)

## Quick Refs

```bash
# AWX CLI
awx login
awx job_templates list
awx job_templates launch ID

# REST API
curl https://awx/api/v2/job_templates/

# Operator
kubectl get awx -n awx
```

## Interview Prep

**Mid**: "AWX purpose."

**Senior**: "AWX vs CI/CD for Ansible."

**Staff**: "Enterprise Ansible platform."

## Next Topic

→ [T03 — Custom Modules & Plugins](T03-Custom-Modules.md)
