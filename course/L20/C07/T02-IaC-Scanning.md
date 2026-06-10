# L20/C07/T02 — IaC Scanning (Checkov, tfsec)

## Learning Objectives

- Scan IaC
- Block bad configs

## Why

Catch misconfig:
- Before deploy
- In code review
- Cheaper than CSPM

## Tools

### Checkov (Bridgecrew / Prisma)
```bash
checkov -d terraform/
checkov -f main.tf
checkov -d k8s/ --framework kubernetes
```

Multi-framework: Terraform, K8s, CloudFormation, ARM, Bicep, Helm, Dockerfile.

### tfsec
```bash
tfsec terraform/
```

Terraform-specific. (Now part of Trivy.)

### Trivy
```bash
trivy config terraform/
```

Multi-framework; growing.

### Terrascan
Similar to Checkov.

### KICS
By Checkmarx.

### Snyk IaC
```bash
snyk iac test terraform/
```

## Common Rules

### Terraform
- S3 bucket public
- No encryption
- SG too open
- IAM wildcard

### K8s
- Privileged container
- No resource limits
- No security context
- Default SA

### Dockerfile
- USER root
- Curl pipe sh
- No ENTRYPOINT

## CI Integration

```yaml
- name: Checkov
  uses: bridgecrewio/checkov-action@v12
  with:
    directory: terraform/
    soft_fail: false
    framework: terraform
```

Block on critical.

## Severity

- CRITICAL: block
- HIGH: block (or warn)
- MEDIUM: warn
- LOW: info

## Skip

```hcl
# checkov:skip=CKV_AWS_20:Public access needed for static site
resource "aws_s3_bucket" "static" {
  ...
}
```

Document why.

## Custom Rules

```yaml
# Custom Checkov check
metadata:
  name: 'My custom check'
  id: 'CKV_MY_1'
definition:
  cond_type: 'attribute'
  resource_types: 'aws_s3_bucket'
  attribute: 'acl'
  operator: 'not_equals'
  value: 'public-read'
```

## Comparison

| | Checkov | tfsec | Trivy config |
|---|---|---|---|
| Frameworks | many | Terraform | many |
| Speed | medium | fast | fast |
| Maintained | active | merged into Trivy | active |
| Custom rules | yes | yes | yes |

For: Checkov broad; Trivy unified.

## SARIF Output

```bash
checkov -d . --output sarif > findings.sarif
gh sarif upload findings.sarif
```

Shows in GitHub Security tab.

## In Pre-Commit

```yaml
- repo: https://github.com/bridgecrewio/checkov.git
  rev: 3.0.0
  hooks:
    - id: checkov
```

Catch in commit.

## Helm Scanning

```bash
helm template my-chart | checkov -f - --framework kubernetes
```

Render + scan.

## Kustomize

```bash
kustomize build overlays/prod | checkov -f - --framework kubernetes
```

## OPA Rego Policies

Custom checks:
```rego
package main

deny[msg] {
  resource := input.resource.aws_s3_bucket[name]
  resource.acl == "public-read"
  msg = sprintf("S3 bucket %s is public", [name])
}
```

```bash
conftest test --policy policy/ main.tf
```

## Best Practices

- Scan in CI
- Block critical
- Allowlist with reason
- Custom rules for org
- Pre-commit + CI
- SARIF to GitHub

## Common Mistakes

- No scan
- Block on everything (noise)
- No allowlist (drown)
- One framework only

## Cost

- Checkov OSS: free
- Checkov Pro (Prisma): $$$
- Trivy: free
- Snyk IaC: free + paid

## Integration with PR

PR comment with findings:
```yaml
- uses: bridgecrewio/checkov-action@v12
  with:
    soft_fail: false
    quiet: true
    output_format: cli
```

For: visible.

## Quick Refs

```bash
# Checkov
checkov -d DIR / -f FILE
checkov --framework terraform | kubernetes | helm | ...
checkov --skip-check CKV_AWS_20

# tfsec / Trivy
trivy config DIR

# Conftest (OPA)
conftest test --policy POLICIES FILE
```

## Interview Prep

**Mid**: "IaC scanning."

**Senior**: "Pipeline integration."

**Staff**: "Policy as code."

## Next Topic

→ [T03 — CIEM (Identity Posture)](T03-CIEM.md)
