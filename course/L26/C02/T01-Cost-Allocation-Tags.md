# L26/C02/T01 — Cost Allocation Tags

## Learning Objectives

- Tag resources
- Track per team

## Tags

Key-value metadata:
- env: prod
- team: backend
- project: api
- cost-center: 1234

## Per Cloud

### AWS
Tags on resources.

```hcl
tags = {
  env = "prod"
  team = "backend"
  project = "api"
  cost-center = "1234"
}
```

Activate cost allocation:
- Billing → Cost Allocation Tags → Activate

### Azure
Tags on resources.

Cost Management reports by tag.

### GCP
Labels on resources.

Billing exports include labels.

## Required Tags

Common:
- env (prod, staging, dev)
- team (who owns)
- project / app (what for)
- cost-center (billing)
- owner (point of contact)
- created-by (Terraform / ClickOps)
- expiration (optional cleanup)

## Enforce

### Terraform
```hcl
default_tags {
  tags = {
    env = var.env
    team = var.team
    managed-by = "terraform"
  }
}
```

Applied to all resources.

### Policy
```hcl
# AWS Organizations Tag Policy
{
  "tags": {
    "env": { "tag_value": { "@@assign": ["prod", "staging", "dev"] } }
  }
}
```

Block resources without required.

### Service Control Policy
```json
{
  "Effect": "Deny",
  "Action": "ec2:RunInstances",
  "Condition": {
    "Null": {"aws:RequestTag/env": "true"}
  }
}
```

For: enforce at create.

## Common Mistakes

### Untagged
20-30% of resources untagged is common.

For: orphan; can't attribute.

### Inconsistent
team=Backend vs team=backend.

For: normalize.

### Wrong Tag
Cost-center wrong; bill goes wrong.

For: verify.

## Tag Audit

```bash
aws ec2 describe-instances \
  --filters "Name=tag:env,Values=prod" \
  | jq ...
```

Find untagged:
```bash
aws ec2 describe-instances --filters "Name=tag-key,Values=env" --query 'length(Reservations)'
```

## Bulk Update

```bash
aws ec2 create-tags --resources i-... i-... --tags Key=env,Value=prod
```

## Reports

```
Cost Explorer:
  Group by: tag:team
  Report: each team's spend
```

## Showback

Per team:
- Last month: $X
- Trend: up / down

For: awareness.

## Chargeback

Per team:
- Charged actual cost
- Budgeted spend

For: accountability.

## Best Practices

- Mandatory tags
- Enforced via IaC + policy
- Audit quarterly
- Owner per tag
- Document tag schema

## Common Mistakes

- Optional (untagged accumulates)
- No enforcement
- Inconsistent values
- Stale (resources outlive owners)

## Tag Schema Doc

```markdown
## Required Tags

env: prod | staging | dev
team: <team-name>
project: <project-name>
cost-center: <number>

## Optional

owner: <email>
expiration: YYYY-MM-DD
```

## Quick Refs

```bash
# Tag
aws ec2 create-tags --resources X --tags Key=env,Value=prod

# Search
aws ec2 describe-instances --filters Name=tag:env,Values=prod

# Untagged
aws resourcegroupstaggingapi get-resources --tag-filters Key=env

# Policy
aws organizations create-policy --type TAG_POLICY
```

## Interview Prep

**Mid**: "Cost tags."

**Senior**: "Enforce tags."

**Staff**: "Tag strategy."

## Next Topic

→ [T02 — Showback vs Chargeback](T02-Showback-Chargeback.md)
