# L10/C03/T05 — State Drift Detection

## Learning Objectives

- Detect drift
- Prevent + remediate

## Drift

Resources changed outside Terraform:
- Manual console mod
- AWS-side change
- Other tool (CLI, SDK)

Code says X; reality is Y.

## Why Bad

- Reality not in code (can't reproduce)
- Apply may surprise (undo manual fix)
- Compliance gap (auditor expects code = truth)
- Wasted effort understanding

## Detection

### terraform plan
```bash
terraform plan
# Note: Objects have changed outside of Terraform
# ~ aws_security_group.web ingress modified
```

Or `-refresh-only`:
```bash
terraform plan -refresh-only
```

Shows drift without modifying state.

```bash
terraform apply -refresh-only
```

Updates state to match reality (without changing reality).

### terraform refresh (deprecated)

Use `apply -refresh-only` instead.

## Continuous Detection

Run `plan` periodically (CI scheduled):
- Detect drift
- Alert if found
- Don't auto-fix (may be legitimate)

```yaml
on:
  schedule:
    - cron: "0 4 * * *"
jobs:
  drift:
    runs-on: ubuntu-latest
    steps:
      - run: terraform init
      - run: terraform plan -detailed-exitcode
        # exit 0: no diff; 1: error; 2: diff
```

Exit code 2 = drift; alert.

## Remediation Options

### Re-Apply (overwrite manual)
```bash
terraform apply
```

Console change reverted. For: enforcing code.

### Update Code (codify the change)
1. Update `.tf` to match new state
2. `terraform plan` → no diff
3. Commit

For: legitimate manual change codified.

### Ignore (lifecycle)
```hcl
lifecycle {
  ignore_changes = [tags]
}
```

For: known auto-managed attrs (AWS Org tags, ASG desired count).

### Remove (intentional removal)
If resource shouldn't be managed anymore:
```bash
terraform state rm aws_x.y
```

Remove from code too.

## Tools

### Terraform Cloud / HCP
Built-in drift detection runs. Notifies on drift.

### driftctl
Open-source; detects drift across infrastructure (covers resources not in Terraform too).
```bash
driftctl scan --from tfstate+s3://bucket/key
```

For: comprehensive (managed + unmanaged).

### Atlantis
PR-driven; doesn't auto-detect but plan in PR shows drift.

### Custom Scheduled Job
Plan; if changes, alert.

## Prevention

### IAM Lockdown
Restrict console / CLI access to read-only for engineers:
- Production: no manual changes
- All changes via PR → Terraform

SCP enforces:
```json
{
  "Effect": "Deny",
  "Action": "ec2:*",
  "Resource": "*",
  "Condition": {
    "StringNotEquals": {"aws:PrincipalArn": "arn:aws:iam::*:role/TerraformDeploy"}
  }
}
```

Only Terraform's role can change.

### Break-Glass
Emergency direct access (logged, alerted):
- Special role
- Used rarely
- Followed by codification

### GitOps
PR is the only change mechanism. Education + tooling.

## Specific Drift Types

### Resource Modified
SG rule added in console.
- Detect: plan diff
- Remediate: re-apply OR codify

### Resource Deleted
Console delete.
- Detect: plan shows recreate
- Remediate: apply (recreate) OR rm from code

### Resource Created
Console creates new.
- Detect: NOT detected (Terraform unaware)
- Use driftctl or similar

### Attribute Modified
AWS-side change (e.g., default tags by Org).
- Detect: plan diff
- Remediate: ignore_changes OR codify

## Drift in Stateful Resources

DB password rotated externally:
```hcl
resource "aws_db_instance" "main" {
  password = var.db_password
  
  lifecycle {
    ignore_changes = [password]
  }
}
```

Drift expected; ignored.

## Configuration Drift vs State Drift

State drift: Terraform state mismatches actual.
Config drift: actual mismatches intended (code).

Both addressed by Terraform plan.

## Common Mistakes

- No drift detection (silent)
- Auto-apply detected drift (may revert good changes)
- Ignore_changes too broad
- Plan in CI, never reviewed

## Best Practices

- Drift detection scheduled (daily)
- Alert on drift
- Investigate before remediate
- Lockdown manual changes
- Document break-glass
- Codify legitimate changes

## Scheduled CI

```yaml
on:
  schedule:
    - cron: "0 8 * * MON-FRI"
jobs:
  drift:
    steps:
      - terraform init
      - terraform plan -detailed-exitcode
      - if drift: notify Slack
```

## Reporting

Dashboard of drift:
- Per workload
- Per resource type
- Trend over time

For team visibility.

## Auto-Remediate (Careful)

Some teams auto-apply on detected drift:
- Reverts to code
- Quick "correction"

Risk:
- May undo legitimate emergency fix
- Without human review

Default: alert, manual review.

## Refresh

`terraform refresh` (alias for `apply -refresh-only`):
- Updates state to match actual
- Doesn't change actual
- After: plan shows no drift (if state synced)

For: sync state to reality without intervening.

## Sentinel / OPA

Policy as code:
- Check Terraform plan
- Block bad changes (open SG, public S3)
- Detect drift via policy

For: org-wide enforcement.

## driftctl Example

```bash
brew install driftctl

driftctl scan --from tfstate+s3://bucket/prod.tfstate \
  --to aws+tf
```

Output:
- Managed (Terraform tracks)
- Unmanaged (exists in AWS; not in Terraform)
- Drifted (managed but changed)

## Anti-Patterns

- "Just one console change"
- Console changes during incident; never codified
- ignore_changes for everything
- Drift exists; nobody acts

## When Drift Acceptable

- Auto-scaling (desired count changes constantly)
- AWS-side metadata
- Read-only attributes
- Org-applied tags

Lifecycle ignore.

For everything else: code is source of truth.

## Investigating Drift

1. `terraform plan -refresh-only` → see what changed
2. CloudTrail → who changed
3. Communicate with that person
4. Decide: revert, codify, or ignore
5. Act

Document decision.

## Refresh Failure

`refresh` may fail if:
- Resource deleted (now state stale)
- Permission revoked
- API errors

Solutions:
- `state rm` if confirmed deleted
- Fix permissions

## Drift in Multi-Team

Team A manages VPC; Team B manages app on VPC.
- Team A's drift in VPC affects Team B's app
- Coordinate; alert across teams

## CI Failure on Drift

```bash
terraform plan -detailed-exitcode -lock-timeout=2m
echo $?
# 0: no changes
# 1: error
# 2: changes detected (drift!)
```

CI flags 2 as warning.

## Quick Refs

```bash
# Detect
terraform plan
terraform plan -refresh-only

# Update state from reality
terraform apply -refresh-only

# Detailed exit code
terraform plan -detailed-exitcode

# driftctl
driftctl scan --from tfstate+s3://bucket/key
```

## Interview Prep

**Mid**: "Drift detection."

**Senior**: "Drift remediation strategy."

**Staff**: "Org-wide drift program."

## Next Topic

→ Move to [L10/C04 — Terraform Modules](../C04/README.md)
