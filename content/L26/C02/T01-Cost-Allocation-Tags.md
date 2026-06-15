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

Find untagged (instances that do NOT have an `env` tag). Note the
server-side `tag-key` filter only matches resources that *have* the tag, so
inverting it means filtering client-side with JMESPath for a missing key:
```bash
# Instances MISSING the env tag — the actual "untagged" set
aws ec2 describe-instances \
  --query "Reservations[].Instances[?!not_null(Tags[?Key=='env'].Value | [0])].InstanceId" \
  --output text

# Count them
aws ec2 describe-instances \
  --query "length(Reservations[].Instances[?!not_null(Tags[?Key=='env'].Value | [0])][])"
```
Filtering `Name=tag-key,Values=env` would count the *tagged* resources — the
opposite of what you want for an untagged audit.

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

**Junior**: "What are cost allocation tags?" — Key-value metadata on cloud resources (env, team, project, cost-center) that the billing system can group by, so you can attribute spend to who owns it. In AWS you must activate them in Billing → Cost Allocation Tags before they appear in Cost Explorer.

**Mid**: "How do you find untagged resources?" — Filter client-side for the *absence* of the key — e.g. `describe-instances` with a JMESPath query for instances whose Tags lack `env`. A `tag-key` server-side filter does the opposite (it returns resources that *have* the tag), so it counts the tagged set, not the untagged one.

**Senior**: "How do you enforce tagging so it doesn't rot?" — Apply tags automatically via IaC (Terraform `default_tags`) for everything provisioned that way, and block manual creation of untagged resources with an SCP that denies the action when the required tag is null. Then audit quarterly and treat untagged resources as orphans to be tagged or terminated.

**Staff**: "Design a tagging strategy for a large org." — Publish a small mandatory schema (env, team, project, cost-center, owner) with documented allowed values, enforce it at create time via SCP/Org Tag Policies plus IaC default tags, normalize case to prevent `Backend` vs `backend` splits, and assign an owner per tag. Feed it into showback first (awareness) and chargeback once data is trusted, with continuous audits so coverage stays near 100% rather than drifting to the typical 20–30% untagged.

## Next Topic

→ [T02 — Showback vs Chargeback](T02-Showback-Chargeback.md)
