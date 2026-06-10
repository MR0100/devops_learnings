# L11/C03/T01 — Dynamic Inventory

## Learning Objectives

- Generate inventory from cloud
- Avoid manual maintenance

## Why Dynamic

Cloud:
- VMs ephemeral
- ASGs scale
- Tags carry meaning
- Manual file = stale

Solution: query cloud at runtime.

## Plugin Configuration

```yaml
# inventory_aws_ec2.yml
plugin: amazon.aws.aws_ec2
regions:
  - us-east-1
  - us-west-2
filters:
  tag:Environment: prod
  instance-state-name: running
keyed_groups:
  - prefix: env
    key: tags.Environment
  - prefix: tag
    key: tags
hostnames:
  - tag:Name
```

```bash
ansible-inventory -i inventory_aws_ec2.yml --list
ansible-playbook -i inventory_aws_ec2.yml playbook.yml
```

## AWS

```bash
ansible-galaxy collection install amazon.aws
```

```yaml
plugin: amazon.aws.aws_ec2
regions: [us-east-1]
filters:
  tag:Role: web
```

Auth: env vars / instance role.

## GCP

```yaml
plugin: google.cloud.gcp_compute
projects:
  - my-project
regions:
  - us-central1
auth_kind: serviceaccount
service_account_file: /path/to/sa.json
```

Filter by labels:
```yaml
filters:
  - 'labels.env = "prod"'
```

## Azure

```yaml
plugin: azure.azcollection.azure_rm
include_vm_resource_groups:
  - my-rg
keyed_groups:
  - prefix: tag
    key: tags
```

Auth: az login.

## DigitalOcean / Linode / Hetzner

Similar plugins. Most clouds.

## K8s

```yaml
plugin: kubernetes.core.k8s
connections:
  - kubeconfig: ~/.kube/config
```

Pods as inventory.

For: cross-K8s automation.

## Custom Script (Legacy)

Any executable returning JSON:
```bash
#!/bin/bash
# inventory.sh
case "$1" in
  --list)
    echo '{"webservers": {"hosts": ["10.0.0.1", "10.0.0.2"]}}'
    ;;
  --host)
    echo '{}'
    ;;
esac
```

```bash
chmod +x inventory.sh
ansible-playbook -i inventory.sh playbook.yml
```

For: legacy / custom sources.

## Multiple Sources

```bash
ansible-playbook -i inventory_aws.yml -i inventory_static.yml playbook.yml
```

Merges. For: hybrid.

## Inventory Directory

```
inventory/
  aws.yml      # dynamic
  static.yml   # static
  group_vars/
  host_vars/
```

```bash
ansible-playbook -i inventory/ playbook.yml
```

Auto-loads all files.

## Caching

```yaml
plugin: amazon.aws.aws_ec2
cache: true
cache_plugin: jsonfile
cache_connection: /tmp/aws_cache
cache_timeout: 600
```

For: avoid AWS API calls every run.

## Performance

Big AWS account: inventory call slow.
Cache: amortizes.

For huge: split by region; limit filters.

## Auth

### AWS
- `aws configure` profile
- IAM role (EC2)
- Env vars: `AWS_ACCESS_KEY_ID`, etc.

### GCP
- Service Account JSON
- `gcloud auth application-default login`

### Azure
- `az login`
- Service Principal env vars

## Keyed Groups

```yaml
keyed_groups:
  - prefix: env
    key: tags.Environment
    # Creates groups: env_prod, env_staging
  - prefix: az
    key: placement.availability_zone
    # Creates: az_us-east-1a, etc.
  - prefix: arch
    key: architecture
    separator: '_'
```

For: tag-based grouping.

## Hostnames

```yaml
hostnames:
  - tag:Name           # use Name tag
  - dns-name           # public DNS
  - private-ip-address
```

Fallback list: first available used.

## Composed Vars

```yaml
compose:
  ansible_host: private_ip_address
  region: placement.region
```

Set vars per host based on cloud data.

## Use Case Examples

### Group by Tag
```yaml
plugin: amazon.aws.aws_ec2
keyed_groups:
  - prefix: tag
    key: tags
# Creates: tag_Role_web, tag_Role_db
```

### Multi-Region
```yaml
plugin: amazon.aws.aws_ec2
regions:
  - us-east-1
  - us-west-2
  - eu-west-1
keyed_groups:
  - prefix: region
    key: placement.region
```

### Production Only
```yaml
filters:
  tag:Environment: prod
  instance-state-name: running
```

## Strategies

### Dynamic Only
Pure cloud; no static.

### Hybrid
Static for on-prem; dynamic for cloud.

### Mixed
Both files in inventory dir.

## Debugging

```bash
# See full inventory
ansible-inventory -i inventory_aws.yml --list

# Specific host
ansible-inventory -i inventory_aws.yml --host i-1234567

# Graph
ansible-inventory -i inventory_aws.yml --graph
```

## CI/CD

```yaml
# GitHub Actions
- name: Run Ansible
  env:
    AWS_REGION: us-east-1
  run: |
    ansible-playbook -i inventory_aws.yml playbook.yml
```

OIDC for AWS auth.

## Best Practices

- Dynamic for cloud (never manual VMs)
- Cache (performance)
- Filter (security; reduce surface)
- Keyed groups (tag-based)
- Tested per env
- Inventory in version control

## Common Mistakes

- Static inventory in cloud (stale)
- No cache (slow)
- Auth via secrets in repo
- No filters (huge inventory)
- Wrong keyed groups (no matches)

## Quick Refs

```bash
# Check inventory
ansible-inventory --list -i inv.yml
ansible-inventory --graph -i inv.yml
ansible-inventory --host HOST -i inv.yml

# Plugin
ansible-doc -t inventory amazon.aws.aws_ec2
```

## Interview Prep

**Mid**: "Why dynamic inventory."

**Senior**: "AWS inventory plugin."

**Staff**: "Inventory architecture at scale."

## Next Topic

→ [T02 — AWX / Ansible Automation Platform](T02-AWX-AAP.md)
