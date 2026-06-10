# L10/C08/T03 — Policy as Code (OPA, Sentinel, Checkov)

## Learning Objectives

- Enforce policies via code
- Use Checkov / OPA / Sentinel

## Why

Without:
- Reviewers manually check
- Mistakes slip through
- Compliance audit nightmare

With:
- Codified standards
- CI enforces
- Audit evidence

## Tools

| Tool | Use |
|---|---|
| Checkov | Static analysis (free) |
| tfsec | Static analysis (free) |
| Terrascan | Static analysis (free) |
| OPA / Conftest | Plan analysis (open) |
| Sentinel | Plan policy (Terraform Cloud paid) |

## Checkov

```bash
pip install checkov
checkov -d .
```

Output:
```
Check: CKV_AWS_18: "Ensure the S3 bucket has access logging enabled"
  FAILED for resource: aws_s3_bucket.data
  File: /modules/data/main.tf:10-15

Check: CKV_AWS_19: "Ensure all data stored in the S3 bucket is securely encrypted at rest"
  PASSED for resource: aws_s3_bucket.data
```

Per check: PASSED / FAILED.

## Checkov in CI

```yaml
- uses: bridgecrewio/checkov-action@master
  with:
    directory: ./
    output_format: cli
```

Fail PR on findings.

## Custom Checkov Rules

```python
# .checkov/custom_check.py
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories

class S3BucketHasVersioning(BaseResourceCheck):
    def __init__(self):
        super().__init__(
            name="S3 bucket has versioning",
            id="CUSTOM_001",
            categories=[CheckCategories.GENERAL_SECURITY],
            supported_resources=["aws_s3_bucket"],
        )
    
    def scan_resource_conf(self, conf):
        if conf.get("versioning", [{}])[0].get("enabled") == [True]:
            return CheckResult.PASSED
        return CheckResult.FAILED

check = S3BucketHasVersioning()
```

For: org-specific.

## tfsec

```bash
brew install tfsec
tfsec .
```

Similar to Checkov.

```yaml
- uses: aquasecurity/tfsec-action@v1
```

## OPA / Conftest

Test against plan JSON:
```bash
terraform plan -out=plan.tfplan
terraform show -json plan.tfplan > plan.json
conftest test plan.json --policy ./policies
```

## Rego Policy

```rego
# policies/s3.rego
package terraform.s3

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_s3_bucket"
    resource.change.after.acl == "public-read"
    msg := sprintf("S3 bucket %v has public ACL", [resource.address])
}

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_s3_bucket_versioning"
    resource.change.after.versioning_configuration[0].status != "Enabled"
    msg := sprintf("Bucket %v has versioning disabled", [resource.address])
}
```

For: complex logic.

## Conftest in CI

```yaml
- run: terraform plan -out=plan
- run: terraform show -json plan > plan.json
- run: conftest test plan.json --policy ./policies
```

## Sentinel (Terraform Cloud)

Paid; integrated with TFC:
```hcl
import "tfplan/v2" as tfplan

s3_buckets = filter tfplan.resource_changes as _, rc {
    rc.type is "aws_s3_bucket"
}

main = rule {
    all s3_buckets as _, bucket {
        bucket.change.after.versioning[0].enabled is true
    }
}
```

Enforcement levels:
- Advisory
- Soft mandatory (override possible)
- Hard mandatory (no override)

## Policies to Enforce

### Security
- No public S3
- Encrypted at rest
- TLS enforced
- No 0.0.0.0/0 in SG (port 22)
- IAM roles (not users)

### Cost
- No huge instance types
- No on-demand for batch
- Tag required (cost-center)

### Compliance
- Required labels
- Approved regions only
- Specific KMS keys
- Logging enabled

### Org Standards
- Naming conventions
- Required tags
- Approved providers / versions

## Levels

Per environment:
- Dev: advisory (warn)
- Staging: soft mandatory
- Prod: hard mandatory

For: gradual rollout.

## CI Workflow

```yaml
jobs:
  validate:
    steps:
    - run: terraform fmt -check
    - run: terraform validate
    - run: tflint
  
  security:
    steps:
    - uses: bridgecrewio/checkov-action@master
    - uses: aquasecurity/tfsec-action@v1
  
  policy:
    steps:
    - run: terraform plan -out=plan
    - run: terraform show -json plan > plan.json
    - run: conftest test plan.json --policy ./policies
  
  cost:
    steps:
    - uses: infracost/actions/setup@v2
    - run: infracost breakdown --path=. --format=table
```

Layered checks.

## Policy Tests

```rego
# policies/s3_test.rego
package terraform.s3

test_public_bucket_denied {
    deny[_] with input as {
        "resource_changes": [{
            "type": "aws_s3_bucket",
            "address": "aws_s3_bucket.bad",
            "change": {
                "after": {"acl": "public-read"}
            }
        }]
    }
}

test_private_bucket_allowed {
    count(deny) == 0 with input as {
        "resource_changes": [{
            "type": "aws_s3_bucket",
            "address": "aws_s3_bucket.good",
            "change": {
                "after": {"acl": "private"}
            }
        }]
    }
}
```

```bash
opa test policies/
```

For: policy reliability.

## Catalog

Pre-built policies:
- Checkov has 1000s
- tfsec has 100s
- OPA Terraform community policies

Start with these; customize.

## False Positives

Policies overly strict:
- Tighten / relax thresholds
- Whitelist exceptions
- Suppress per-resource

Checkov:
```hcl
# checkov:skip=CKV_AWS_18:Logging not needed for ephemeral bucket
resource "aws_s3_bucket" "scratch" {
  ...
}
```

Document why.

## Documentation

Policies need docs:
- Why
- How to fix
- Examples

For: developer self-service.

## Continuous Compliance

Run periodically:
- Daily scan of existing
- Alert on regression
- Report to dashboard

For: ongoing posture.

## Pre-Commit

```yaml
- repo: https://github.com/antonbabenko/pre-commit-terraform
  hooks:
  - id: terraform_tfsec
  - id: terraform_checkov
```

Local before commit.

## Cost Policy

Infracost in CI:
```bash
infracost diff --path=. --baseline-path=baseline.json
```

Block PRs with > $X/mo cost increase.

For: cost-aware development.

## Open vs Paid

Open source:
- Checkov, tfsec, Terrascan
- OPA / Conftest
- Free

Paid:
- Sentinel (TFC)
- Spacelift
- Snyk IaC

For: rich features, support.

## Best Practices

- Multiple tools (defense in depth)
- Policy tested
- Catalog + custom
- Per-env levels
- CI enforces
- Documented exceptions
- Continuous scan (not just PR)

## Common Mistakes

- One tool only (gaps)
- Policy without docs
- Suppressing without reason
- Too strict (delivery friction)
- Too loose (no value)

## Real-World

For org with 100s of repos:
- Standard policy library (versioned)
- Per-repo policy CI
- Central dashboard (Bridgecrew / Snyk / Wiz)
- Reports to security team

## Compliance Mapping

Map policies to:
- SOC 2 controls
- PCI DSS requirements
- HIPAA safeguards

For: audit evidence.

## Quick Refs

```bash
# Checkov
checkov -d .
checkov -d . --output github_failed_only

# tfsec
tfsec .

# Conftest
conftest test plan.json --policy ./policies

# OPA test
opa test policies/

# Infracost
infracost breakdown --path=.
```

## Interview Prep

**Mid**: "Why policy as code."

**Senior**: "Checkov vs OPA."

**Staff**: "Compliance program for Terraform."

## Next Topic

→ [T04 — Cost Estimation (Infracost)](T04-Infracost.md)
