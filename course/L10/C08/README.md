# L10/C08 — Best Practices

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Repo-Structure.md) | Repository Structure | 0.5 hr |
| [T02](T02-Secrets-IaC.md) | Secrets in IaC (Vault, KMS, SOPS) | 1 hr |
| [T03](T03-Policy-as-Code.md) | Policy as Code (OPA, Sentinel, Checkov) | 1 hr |
| [T04](T04-Cost-Estimation.md) | Cost Estimation (Infracost) | 0.5 hr |

## Repository Structure

```
infrastructure/
├── .github/workflows/
├── modules/              # reusable modules (versioned, tagged)
│   ├── vpc/
│   ├── eks/
│   ├── rds/
│   └── monitoring/
├── live/                 # actual deployments
│   ├── shared/           # org, IAM, log archive (one-off resources)
│   ├── prod/
│   │   ├── us-east-1/
│   │   │   ├── network/
│   │   │   ├── compute/
│   │   │   └── data/
│   │   └── us-west-2/
│   ├── staging/
│   └── dev/
├── policies/             # OPA/Sentinel policies
├── scripts/
├── docs/
└── README.md
```

Or split into multiple repos:
- `tf-modules/` — published, versioned modules
- `tf-live/` — actual env configurations
- `tf-policies/` — guardrails

## Secrets

### Don't
- Commit secrets (even encrypted in plaintext-readable form)
- Pass secrets as Terraform variables in CI logs
- Print secrets in `output` blocks (unless `sensitive = true`)
- Bake secrets into AMIs / images

### Do
- Generate secrets in Terraform if possible (`random_password`); store in Secrets Manager
- Read secrets from a vault at runtime
- Mark sensitive vars/outputs `sensitive = true`
- Use SOPS for committing encrypted files

### Patterns

**Generate + Store**:
```hcl
resource "random_password" "db" {
  length  = 32
  special = true
}

resource "aws_secretsmanager_secret_version" "db" {
  secret_id     = aws_secretsmanager_secret.db.id
  secret_string = random_password.db.result
}

resource "aws_db_instance" "main" {
  password = random_password.db.result
}
```

**Read at Runtime**:
```hcl
data "aws_secretsmanager_secret_version" "db" {
  secret_id = "prod/db/password"
}

# Use jsondecode if needed
locals {
  db_password = jsondecode(data.aws_secretsmanager_secret_version.db.secret_string)["password"]
}
```

**SOPS**: encrypt YAML/JSON; commit; decrypt at apply time via env var or KMS.

## Policy as Code

Enforce rules at plan time. Block non-compliant changes.

### OPA (Open Policy Agent)

```rego
package terraform.s3

deny[msg] {
  resource := input.resource_changes[_]
  resource.type == "aws_s3_bucket"
  not resource.change.after.server_side_encryption_configuration
  msg := sprintf("S3 bucket %s must have encryption", [resource.address])
}
```

Run against `terraform show -json plan.tfplan`:
```bash
terraform show -json plan.tfplan | opa eval -d policies/ -i - 'data.terraform.deny'
```

### Sentinel (HashiCorp)
- Native to Terraform Cloud / Enterprise
- More opinionated than OPA
- Integration into TFC workflow

### Checkov (Bridgecrew)
```bash
checkov -d .
checkov --framework terraform --file plan.tfplan
```
Pre-baked rules for AWS/Azure/GCP best practices.

### tfsec
Focuses on security. Similar to Checkov but lighter.

### Recommended Stack
- pre-commit: `terraform fmt`, `validate`, `tflint`, `tfsec`, `checkov`
- CI: same + `terraform plan` + OPA policy check
- TF Cloud: Sentinel for production gates

## Cost Estimation

### Infracost
Predict cost impact of a PR:
```bash
infracost diff --path plan.tfplan
```

Output:
```
Project: my-infra
+ aws_instance.web (m6i.large): +$73/mo
- aws_instance.old (m5.xlarge): -$140/mo
Net change: -$67/mo
```

Integrate into PR via GitHub Action.

### Terraform Cloud Cost Estimation
Built-in for TFC users; tracks before/after per plan.

### When It Matters
- Catch expensive misclicks before merge
- Show cost in PR for review
- Budget enforcement (block if > X/mo)

## Module Naming

```
terraform-<provider>-<name>     # GitHub repo
e.g., terraform-aws-vpc
e.g., terraform-azurerm-aks
```

## Pinning Versions

Always pin:
```hcl
terraform {
  required_version = ">= 1.6, < 2.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"
}
```

Update intentionally:
- Lockfile (`.terraform.lock.hcl`) — commit it
- Renovate / Dependabot for PRs that bump versions

## Code Hygiene

- `terraform fmt -recursive` (pre-commit)
- `terraform validate` (early error)
- `tflint` — provider-specific lint
- Consistent variable naming (snake_case)
- Group related variables (don't sprinkle)
- Use locals for derived values
- Provider blocks at root only (not in modules)

## Common Pitfalls

- Provider blocks in modules (breaks reuse)
- `count` then deleting middle items (state shifts → broken plans)
- Massive single TF root (slow plans, blast radius)
- No lifecycle on prod databases (`prevent_destroy` saves accidents)
- Using `terraform destroy` in CI (one bug ≈ wiped infra)
- Not using lockfile

## Interview Themes

- "Walk me through your TF repo structure"
- "Secrets handling in IaC"
- "Policy as code — what gates do you have?"
- "Cost estimation in PR — how?"
- "TF best practices for a 50-engineer org"
