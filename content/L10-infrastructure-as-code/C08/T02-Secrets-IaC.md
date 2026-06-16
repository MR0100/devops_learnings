# L10/C08/T02 — Secrets in IaC (Vault, KMS, SOPS)

## Learning Objectives

- Handle secrets in Terraform
- Avoid plaintext

## Problem

Terraform needs secrets:
- DB passwords
- API keys
- TLS certs

If committed: leaked.

## Anti-Patterns

```hcl
# BAD
password = "supersecret"

# BAD
password = var.password    # in .tfvars (committed)
```

NEVER commit plaintext secrets.

## Solutions

### 1. Environment Variables
```hcl
variable "db_password" {
  type      = string
  sensitive = true
}
```

```bash
export TF_VAR_db_password=secret
terraform apply
```

CI: pass via secret manager.

### 2. AWS Secrets Manager / Parameter Store
```hcl
data "aws_secretsmanager_secret_version" "db" {
  secret_id = "prod/db/password"
}

resource "aws_db_instance" "main" {
  password = jsondecode(data.aws_secretsmanager_secret_version.db.secret_string)["password"]
}
```

Secret in Secrets Manager; Terraform reads at apply.

### 3. Vault
```hcl
data "vault_generic_secret" "db" {
  path = "secret/prod/db"
}

resource "aws_db_instance" "main" {
  password = data.vault_generic_secret.db.data["password"]
}
```

For: HashiCorp ecosystem.

### 4. SOPS (Encrypted Files)
```bash
# Encrypt
sops -e secrets.yaml > secrets.enc.yaml

# Decrypt for apply (via plugin)
sops -d secrets.enc.yaml | terraform apply -var-file=-
```

Files in Git encrypted; decrypted at apply.

For: GitOps-friendly secrets.

## Random Generation

```hcl
resource "random_password" "db" {
  length  = 32
  special = true
}

resource "aws_db_instance" "main" {
  password = random_password.db.result
}

resource "aws_secretsmanager_secret" "db" {
  name = "prod/db"
}

resource "aws_secretsmanager_secret_version" "db" {
  secret_id     = aws_secretsmanager_secret.db.id
  secret_string = random_password.db.result
}
```

Terraform generates; stores in Secrets Manager.

Caveat: `random_password.result` in state (plaintext).

## State Encryption

Terraform state contains secrets. Encrypt:
- S3 backend: SSE-KMS
- Terraform Cloud: encrypted by HashiCorp

```hcl
backend "s3" {
  encrypt        = true
  kms_key_id     = "alias/tfstate"
}
```

## Sensitive Output

```hcl
output "db_password" {
  value     = random_password.db.result
  sensitive = true
}
```

Not displayed in plan/apply. Still in state.

## Sensitive Variable

```hcl
variable "api_key" {
  type      = string
  sensitive = true
}
```

Marked sensitive; not logged.

## Pipeline Secrets

For CI:
- GitHub Actions: secrets (encrypted)
- GitLab CI: variables
- Use OIDC for cloud auth (no static keys)

```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::ACCT:role/GitHubActionsRole
    aws-region: us-east-1
- run: terraform apply
```

## OIDC for Terraform Cloud

```hcl
# Terraform Cloud workspace
# Variables tab: AWS_ROLE_ARN
# Workspace uses OIDC to assume role
```

No static AWS keys.

## Per-Environment Secrets

```hcl
data "aws_secretsmanager_secret_version" "db" {
  secret_id = "${var.env}/db/password"
}
```

Different secret per env.

## Initial Password Pattern

For DB initial password:
```hcl
resource "random_password" "db_initial" {
  length = 32
  keepers = {
    # only generate once
  }
}

resource "aws_db_instance" "main" {
  password = random_password.db_initial.result
}
```

After first apply: user changes password; Terraform tracks (or ignore_changes).

## Lifecycle ignore_changes

```hcl
resource "aws_db_instance" "main" {
  password = ...
  
  lifecycle {
    ignore_changes = [password]
  }
}
```

For: rotated externally.

## Vault Dynamic Credentials

Vault generates per-app DB credentials:
- Short TTL
- Auto-rotated
- Audit per app

Terraform fetches; app uses.

Complex setup; powerful.

## CMK for KMS

```hcl
resource "aws_kms_key" "main" {
  description = "App encryption key"
  policy      = ...
}

resource "aws_secretsmanager_secret" "db" {
  kms_key_id = aws_kms_key.main.arn
}
```

Customer-managed key.

## Secrets Manager Rotation

```hcl
resource "aws_secretsmanager_secret_rotation" "db" {
  secret_id           = aws_secretsmanager_secret.db.id
  rotation_lambda_arn = aws_lambda_function.rotator.arn
  
  rotation_rules {
    automatically_after_days = 30
  }
}
```

Lambda rotates; secret updated; Terraform doesn't manage password.

## TFE Variable Sets

Terraform Cloud:
- Variable Sets across workspaces
- Marked sensitive
- Used by runs

For: shared credentials.

## OPA Policy

Prevent secrets in code:
```rego
deny[msg] {
    input.module_calls[_].constants.password
    msg := "Hardcoded password forbidden"
}
```

CI check.

## detect-secrets

```bash
pip install detect-secrets
detect-secrets scan .
```

Pre-commit hook.

For: catch in PR.

## trufflehog

```bash
trufflehog filesystem .
```

Deep scan; finds historical secrets in Git.

## Common Mistakes

- Plaintext in .tfvars
- Committing .tfvars
- Sensitive vars not marked
- State in unencrypted bucket
- Long-lived AWS keys in CI

## Best Practices

- Secrets in external manager (Secrets Manager / Vault)
- Reference via data source
- Sensitive marker on vars/outputs
- State encrypted
- OIDC for CI cloud auth
- Pre-commit secret scanning
- Audit access (CloudTrail KMS)
- Rotation

## Secret Lifecycle

```
Generate (random_password)
  ↓
Store (Secrets Manager)
  ↓
Reference (data source)
  ↓
Use (resource)
  ↓
Rotate (Lambda)
```

Automated.

## Multi-Account

For shared secrets:
- Secret in central account
- Cross-account access via KMS policy
- Terraform in each account reads

## State Backup

State has secrets. Backup:
- S3 versioning enabled
- Encrypted
- Restricted access

## Audit

CloudTrail KMS events:
- Decrypt events
- Who, when, why

For: forensics.

## Rotation Strategy

For DB password:
- Secrets Manager handles
- Terraform ignores `password`
- App pulls latest

For app code:
- Don't store in code
- Fetch on startup
- Cache; refresh periodically

## Quick Refs

```hcl
# Sensitive var
variable "secret" {
  type      = string
  sensitive = true
}

# From Secrets Manager
data "aws_secretsmanager_secret_version" "x" {
  secret_id = "..."
}

# Random
resource "random_password" "x" {
  length = 32
}

# Lifecycle
lifecycle {
  ignore_changes = [password]
}
```

```bash
# SOPS
sops -e secrets.yaml > secrets.enc.yaml
sops -d secrets.enc.yaml

# detect-secrets
detect-secrets scan
detect-secrets audit
```

## Interview Prep

**Mid**: "Secrets in Terraform."

**Senior**: "Vault integration."

**Staff**: "Org secret strategy."

## Next Topic

→ [T03 — Policy as Code](T03-Policy-as-Code.md)
