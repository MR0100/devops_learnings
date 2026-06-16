# L10/C04/T02 — Versioning & the Registry

## Learning Objectives

- Version modules
- Use registry

## Why Version

Without: consumer pulls latest; breaking change = broken builds.

With: pin specific version; controlled upgrades.

## Semver

```
v1.2.3
│ │ └─ Patch (bug fix)
│ └─── Minor (new feature, backward-compat)
└───── Major (breaking change)
```

For modules:
- Add optional input: minor
- Change required input: major
- Remove input: major
- Rename output: major
- Fix bug: patch
- Add output: minor (usually)

## Tag

In Git:
```bash
git tag v1.0.0
git push origin v1.0.0
```

Reference:
```hcl
source = "git::https://...//path?ref=v1.0.0"
```

## CHANGELOG

Document per release:
```markdown
# Changelog

## [2.0.0] - 2024-06-09
### Breaking
- Renamed input `vpc_cidr` to `cidr_block`

## [1.1.0] - 2024-05-15
### Added
- Optional `enable_flow_logs` input

## [1.0.1] - 2024-04-10
### Fixed
- Tag inheritance for subnets
```

## Constraints

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"        # exact
  version = "~> 5.0"       # 5.x but not 6
  version = ">= 5.0, < 6"  # same
  version = ">= 5.1"       # any 5.1+
}
```

`~> 5.0`: 5.0, 5.1, 5.99 OK; 6.0 not.

Pin to allow patch updates; lock major.

## Terraform Registry

`registry.terraform.io`:
- Public modules
- Verified (HashiCorp partner)
- Community

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"
}
```

Format: `namespace/name/provider`.

## Verified Modules

Check mark badge:
- Tested
- Documented
- Maintained

Prefer verified for production.

## Private Registry

### HCP Terraform / Terraform Cloud
Workspace publish modules to org registry.

### Spacelift / env0 / etc.
Similar; private modules.

### Self-Hosted
- Artifactory
- Cloudsmith
- GitHub Packages
- Custom

For: org-specific modules.

## Git-Based "Registry"

For private: just use Git tags.

```hcl
source  = "git::https://github.com/my-org/tf-modules.git//vpc?ref=v1.0.0"
```

No registry server; tags ARE versions.

For most teams: enough.

## Pulling Module

```bash
terraform init
# Initializing modules...
# Downloading from github.com/...
# - vpc in modules/vpc
```

Cached in `.terraform/modules/`.

## Updating

Bump version constraint:
```hcl
version = "~> 5.1"     # was 5.0
```

```bash
terraform init -upgrade
terraform plan
```

Review diff. Apply if good.

## Major Version Migration

Big change. Plan:
1. Read CHANGELOG
2. Identify breaking changes
3. Update code (rename inputs, etc.)
4. Test in dev / staging
5. Migrate per env

For: well-managed module ecosystems.

## Pin Strategy

For prod:
- Pin to exact version (deterministic)
- Or `~>` patch range
- Upgrade deliberately

For dev:
- Same as prod (avoid surprise)

## Internal Module Versioning

Same idea:
- Tag releases
- CHANGELOG
- Semver
- Consumers pin

## When Pin Major

Always:
```hcl
version = "~> 5.0"     # allows 5.x
```

Never:
```hcl
# No version → always latest → breaks
```

Or:
```hcl
version = ">= 5.0"     # 5+, including 6 (breaking)
```

## Lock File for Modules

`.terraform.lock.hcl`: pins providers. NOT modules.

Modules pinned via `version` constraint + cache.

For deterministic builds: exact versions or lock cache.

## Module Discoverability

For internal:
- Document in README per module
- Index in central docs
- terraform-docs auto-generated

## Module Standards

For org:
- Required README
- Required CHANGELOG
- Required tests (Terratest)
- Required examples
- CI checks

Enforce via PR review.

## Validation in Module

Add input validation; catches at plan:
```hcl
validation {
  condition = can(regex("^...", var.x))
  error_message = "..."
}
```

## Pre-Release Versions

```bash
git tag v2.0.0-beta1
```

```hcl
version = "~> 2.0.0-beta"
```

For testing before stable.

## Deprecation

Soft-deprecate:
```hcl
variable "old_name" {
  description = "DEPRECATED: use new_name"
}
```

Hard-deprecate (major bump):
- Remove old_name in v2
- Migration guide

## When Not to Use Public Modules

- Specific compliance requirements
- Niche needs not covered
- Performance critical (custom optimized)
- Trust concerns

For most: prefer public verified.

## Forking

Public module doesn't meet need:
1. Fork
2. Customize
3. Track upstream changes
4. Or merge back if generic

Avoid: maintenance burden.

## Examples of Strong Modules

- terraform-aws-modules/vpc/aws (industry standard)
- terraform-aws-modules/eks/aws
- terraform-aws-modules/rds/aws
- terraform-aws-modules/security-group/aws

Battle-tested; widely used.

## Common Mistakes

- No version pin
- Pin to commit SHA (immutable but no semver clarity)
- Tracking `main` (broken any time)
- Forks without upstream sync
- Custom versions of public modules

## Best Practices

- Semver
- Tag releases
- CHANGELOG
- Pin in consumer
- Test before bumping major
- terraform-docs

## Private Registry Choice

| | HCP Terraform | Spacelift | Git+tags |
|---|---|---|---|
| Cost | Paid | Paid | Free |
| Features | Many | Many | Basic |
| Discoverability | Good | Good | Manual |
| Verified | Yes | Yes | No |

For early teams: Git+tags.
For mature: HCP Terraform or similar.

## Quick Refs

```bash
# Use specific version
module "x" {
  source = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"
}

# Update
terraform init -upgrade

# Tag and push
git tag v1.2.3
git push origin v1.2.3
```

## Interview Prep

**Mid**: "Module versioning."

**Senior**: "Major version migration."

**Staff**: "Private registry strategy."

## Next Topic

→ [T03 — Composition Patterns](T03-Composition.md)
