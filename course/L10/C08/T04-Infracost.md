# L10/C08/T04 — Cost Estimation (Infracost)

## Learning Objectives

- Use Infracost
- Build cost-aware culture

## Infracost

Cost estimation for Terraform:
- Parses plan
- Looks up cloud pricing
- Outputs cost per resource

Free for individuals; team plans paid.

## Install

```bash
brew install infracost
infracost auth login
```

## Basic

```bash
infracost breakdown --path=.
```

Output:
```
Project: terraform-aws

 Name                                   Monthly Qty  Unit                     Monthly Cost
 aws_instance.web                                           
 ├─ Instance usage (Linux/UNIX, on-demand, m5.large)   730  hours                     $70.08
 ├─ root_block_device                                       
 │  └─ Storage (general purpose SSD, gp3)                100  GB                         $8.00
 └─ Memory                                                                                  
 
 aws_db_instance.main                                       
 ├─ Database instance (db.t3.medium, Single-AZ)        730  hours                     $51.10
 └─ Storage (general purpose SSD, gp2)                  100  GB                         $11.50
 
 OVERALL TOTAL                                                                       $140.68
```

Monthly cost breakdown.

## CI Integration

```yaml
- uses: infracost/actions/setup@v2
  with:
    api-key: ${{ secrets.INFRACOST_API_KEY }}

- name: Generate Infracost diff
  run: |
    infracost breakdown --path=. \
      --format=json --out-file=/tmp/infracost-base.json
    
- name: Post comment
  run: |
    infracost comment github --path=/tmp/infracost.json \
      --repo=${{ github.repository }} \
      --github-token=${{ secrets.GITHUB_TOKEN }} \
      --pull-request=${{ github.event.pull_request.number }} \
      --behavior=update
```

PR comment shows cost diff.

## Diff

```bash
# Baseline
git checkout main
infracost breakdown --path=. --format=json --out-file=baseline.json

# Branch
git checkout feature
infracost diff --path=. --compare-to=baseline.json
```

Output: cost change.

## Policy

Block PRs with cost spikes:
```bash
infracost comment github --path=infracost.json \
  --fail-on-budget=1000   # fail if > $1000/mo
```

For: cost-aware merges.

## Per-Resource

```
+ aws_instance.web
    + Instance: m5.large × 730 hrs = $70.08
    + Storage: 100 GB gp3 = $8.00
    
~ aws_db_instance.main
    ~ Class: db.t3.medium → db.r5.large
    Δ +$120/mo
    
- aws_s3_bucket.old (deleted)
    - $5/mo savings
```

Clear what's costly.

## What Infracost Estimates

Most AWS, Azure, GCP services:
- Compute (EC2, RDS)
- Storage (S3, EBS)
- LB
- NAT, CloudFront
- Lambda
- Many more

What it doesn't:
- Data transfer (variable; estimates)
- Spot pricing (variable)
- Custom usage patterns

For: estimate not exact.

## Custom Usage

For: usage-based pricing (Lambda invocations, S3 requests):
```yaml
# infracost-usage.yml
version: 0.1
resource_usage:
  aws_lambda_function.api:
    monthly_requests: 1000000
    request_duration_ms: 200
    
  aws_s3_bucket.uploads:
    storage_gb: 100
    monthly_tier_1_requests: 100000
```

```bash
infracost breakdown --path=. --usage-file=infracost-usage.yml
```

Provides realistic numbers.

## Multi-Module

For repo with many envs:
```yaml
# infracost.yml
version: 0.1
projects:
  - path: live/prod/us-east-1/network
  - path: live/prod/us-east-1/apps
  - path: live/dev/us-east-1
```

Aggregated.

## Tagging Strategy

For cost attribution:
```hcl
provider "aws" {
  default_tags {
    tags = {
      Project    = "my-project"
      Team       = "platform"
      Env        = "prod"
      CostCenter = "ENG-001"
    }
  }
}
```

Infracost respects tags; group by tag.

## Showback / Chargeback

Use Infracost in CI to:
- Per-team cost reports
- Trend over time
- Budget alerts

For: financial transparency.

## Cloud Pricing Updates

Infracost updates pricing data continuously. No-op for you.

For: current quotes.

## Comparison with Cloud Calculators

| | Infracost | AWS Calculator |
|---|---|---|
| Source | Terraform | Manual |
| Speed | Seconds | Minutes |
| Automation | CI | Manual |
| Diff | Yes | No |
| Multi-cloud | Yes | Per cloud |

For Terraform users: Infracost wins.

## Limitations

- Estimates (real cost varies)
- Doesn't account for RIs/SPs
- Usage assumptions
- Spot pricing variability

For: directional, not exact.

## Best Practices

- Infracost in every PR
- Comment with diff
- Budget per project
- Custom usage file
- Tag for attribution
- Trend over time
- Review monthly

## Cost-Aware Culture

PRs:
- Engineer sees cost change
- Reviewer asks "needed?"
- Justify large additions
- Optimize before merge

For: spending discipline.

## Cloud Cost Tools

Beyond Infracost:
- AWS Cost Explorer
- AWS Cost Anomaly Detection
- Kubecost (K8s)
- CloudHealth
- Cloudability
- Vantage

For ongoing: cost dashboards.
For Terraform PRs: Infracost.

## CI Failure

For massive cost (e.g., $10k/mo new):
- Block PR
- Require explicit approval

```yaml
- run: |
    if [ $(jq .diffTotalMonthlyCost infracost.json | cut -d. -f1) -gt 1000 ]; then
      echo "Cost > $1000/mo. Need approval."
      exit 1
    fi
```

## ENG Communication

PR comment template:
```
## Infracost Estimate

Monthly cost: $1,234.56
Diff: +$200 (16.2%)

### Cost increase
- aws_instance.api: +$70 (m5.large vs t3.medium)
- aws_rds.main: +$130 (Multi-AZ enabled)

### Justification
Multi-AZ for production tier-0 service (PR #123).
```

For: context.

## Sentinel + Infracost

Sentinel policy on cost:
```hcl
import "tfplan/v2" as tfplan
import "decimal"

monthly_cost = decimal.new(...)   # via infracost

main = rule {
    monthly_cost.lt(decimal.new(10000))
}
```

For: hard limits.

## Open Source vs Cloud

Infracost CLI: free.
Infracost Cloud (org features): paid (~$/user/mo).

For teams: paid for visibility, governance.

## Common Mistakes

- Skipping in PR
- Ignoring diff
- No budgets
- Estimates assumed exact
- No tagging for cost

## Quick Refs

```bash
# Install
brew install infracost
infracost auth login

# Breakdown
infracost breakdown --path=.

# Diff
infracost diff --path=. --compare-to=baseline.json

# Format
infracost breakdown --path=. --format=json --out-file=cost.json
infracost output --path=cost.json --format=table

# Comment PR
infracost comment github --path=cost.json ...
```

## Interview Prep

**Mid**: "Cost-aware Terraform PRs."

**Senior**: "Cost governance via CI."

**Staff**: "FinOps for IaC."

## Next Topic

→ Move to [L10/C09 — Disasters & Recovery](../C09/README.md)
