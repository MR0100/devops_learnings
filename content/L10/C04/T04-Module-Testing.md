# L10/C04/T04 — Module Testing (Terratest, Terraform Test)

## Learning Objectives

- Test Terraform modules
- Apply different test strategies

## Why Test

Without:
- Refactors break consumers
- Regressions slip
- Manual verification expensive

With:
- Confidence
- Faster iteration
- Catch issues early

## Test Pyramid

```
        E2E (Terratest: real cloud)
       /   \
      /     \
     Integration (terraform test)
    /        \
   /          \
  Validation (terraform validate, tflint)
```

## terraform validate

Syntax + reference check:
```bash
terraform validate
```

Free, fast. CI baseline.

## tflint

Linter:
```bash
tflint --init
tflint
```

Catches:
- Provider-specific issues
- Best practice violations
- Unused vars
- Type issues

## terraform fmt

```bash
terraform fmt -check -recursive
```

Format check. CI required.

## terraform plan

Plan = test:
```bash
terraform plan -out=plan.tfplan
```

Catches:
- Syntax errors
- Reference errors
- Provider issues

CI: plan in PR.

## Terraform Test (Native)

1.6+:
```hcl
# tests/basic.tftest.hcl
run "create_vpc" {
  command = plan
  
  variables {
    cidr = "10.0.0.0/16"
  }
  
  assert {
    condition = aws_vpc.main.cidr_block == "10.0.0.0/16"
    error_message = "CIDR mismatch"
  }
}

run "apply_real" {
  command = apply
  
  variables {
    cidr = "10.0.0.0/16"
  }
  
  assert {
    condition = output.vpc_id != ""
    error_message = "VPC ID empty"
  }
}
```

```bash
terraform test
```

Tests in same repo.

## Terratest (Go)

For richer testing:
```go
package test

import (
    "testing"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/stretchr/testify/assert"
)

func TestVPC(t *testing.T) {
    opts := &terraform.Options{
        TerraformDir: "../examples/basic",
        Vars: map[string]interface{}{
            "cidr": "10.0.0.0/16",
        },
    }
    
    defer terraform.Destroy(t, opts)
    terraform.InitAndApply(t, opts)
    
    vpcID := terraform.Output(t, opts, "vpc_id")
    assert.NotEmpty(t, vpcID)
}
```

```bash
go test -v -timeout 30m
```

Provisions real infrastructure; verifies; destroys.

## Examples Directory

```
modules/vpc/
├── ...
└── examples/
    ├── basic/
    │   └── main.tf
    └── advanced/
        └── main.tf
```

Examples = integration tests.

```go
// In test
TerraformDir: "../examples/basic",
```

Test each example.

## Compliance Testing

OPA / Conftest:
```rego
deny[msg] {
    input.resource_changes[_].type == "aws_s3_bucket"
    not input.resource_changes[_].change.after.versioning[0].enabled
    msg := "S3 bucket must have versioning enabled"
}
```

Test against plan output:
```bash
terraform plan -out=plan.json
conftest test plan.json --policy policies/
```

For: enforce standards in CI.

## Checkov / tfsec

Static security analysis:
```bash
checkov -d .
tfsec .
```

Catches:
- Public S3
- Open SGs
- Unencrypted volumes
- Many CVE-related

## Cost Estimation

Infracost in CI:
```bash
infracost diff --path=. --baseline=main
```

Comment cost change on PR.

For: cost-aware PRs.

## Test Strategies

### Unit
- terraform validate
- terraform fmt
- tflint

Fast (seconds).

### Integration
- terraform test (1.6+)
- Examples
- OPA/Conftest

Medium (minutes).

### E2E
- Terratest
- Apply real cloud
- Verify
- Destroy

Slow (10-30 min); expensive.

For: PR runs unit + integration; nightly runs E2E.

## CI Pipeline

```yaml
- run: terraform fmt -check -recursive
- run: terraform init
- run: terraform validate
- run: tflint
- run: tfsec
- run: terraform plan -out=plan
- run: conftest test plan --policy ./policies
- run: terraform test    # if 1.6+
- if: nightly
  run: go test ./tests/...   # Terratest
```

## Test Data

For Terratest:
```go
uniqueID := strings.ToLower(random.UniqueId())
namespace := fmt.Sprintf("test-%s", uniqueID)

opts := &terraform.Options{
    TerraformDir: "../examples/basic",
    Vars: map[string]interface{}{
        "namespace": namespace,
    },
}
```

Unique per test run; avoid conflicts.

## Cleanup

```go
defer terraform.Destroy(t, opts)
```

Always cleanup. Else: leftover infra; cost.

## Test Failure

If destroy fails: orphaned resources.

CI handles:
- Tagged with unique ID
- Cleanup script removes by tag
- Cost monitoring

## Parallelism

Terratest:
```go
t.Parallel()
```

Multiple tests concurrently. Faster but more API calls.

## Test Environment

Dedicated AWS account / GCP project for testing:
- Isolated
- Easy to nuke
- Cost-tracked separately

## Module Documentation

terraform-docs generates docs from code:
```bash
terraform-docs markdown table . > README.md
```

CI: check up-to-date.

## terraform-docs in CI

```yaml
- run: terraform-docs markdown table . > /tmp/README.md
- run: diff /tmp/README.md README.md
# fails if README stale
```

For: enforce docs.

## Best Practices

- Validate + lint in PR
- Plan in PR with diff
- Security scan (tfsec/checkov)
- Cost estimation (Infracost)
- terraform test for integration
- Terratest for E2E (nightly)
- Examples documented
- Versions pinned

## Common Mistakes

- No tests
- Tests in main account (cost / conflict)
- No cleanup (orphans)
- Skip security scan
- Skip plan in PR

## Real World Setup

For module repo:
```
module-vpc/
├── main.tf
├── variables.tf
├── outputs.tf
├── README.md
├── examples/
│   ├── basic/
│   └── advanced/
├── tests/
│   ├── basic.tftest.hcl
│   ├── advanced.tftest.hcl
│   └── terratest/
│       └── vpc_test.go
├── policies/
│   └── opa/
└── .github/workflows/
    └── test.yaml
```

## Quick Refs

```bash
# Native test
terraform test

# Terratest
go test -v -timeout 30m ./tests

# Security
tfsec .
checkov -d .

# Lint
tflint

# Docs
terraform-docs markdown table .

# Cost
infracost diff --path=.
```

## Interview Prep

**Mid**: "Why test Terraform."

**Senior**: "Terratest workflow."

**Staff**: "Module testing strategy for org."

## Next Topic

→ Move to [L10/C05 — Terraform at Scale](../C05/README.md)
