# L10/C04 — Terraform Modules

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Module-Anatomy.md) | Module Anatomy | 0.5 hr |
| [T02](T02-Versioning-Registry.md) | Versioning & the Registry | 0.5 hr |
| [T03](T03-Composition.md) | Composition Patterns | 1 hr |
| [T04](T04-Module-Testing.md) | Module Testing (Terratest, Terraform Test) | 1 hr |

## Module Anatomy

A module is just a directory with .tf files.

```
modules/vpc/
├── main.tf            # resources
├── variables.tf       # inputs
├── outputs.tf         # outputs
├── versions.tf        # provider + tf version requirements
├── README.md
└── examples/
    └── basic/
        ├── main.tf
        └── README.md
```

### Using a Module
```hcl
module "vpc" {
  source = "./modules/vpc"
  # or
  # source = "git::https://github.com/org/repo.git//modules/vpc?ref=v1.0.0"
  # source = "terraform-aws-modules/vpc/aws"
  # source = "s3::https://s3-eu-west-1.amazonaws.com/bucket/modules.zip"

  version = "5.0.0"   # only for Registry / git source w/ ref

  name = "prod"
  cidr = "10.0.0.0/16"

  azs            = ["us-east-1a", "us-east-1b", "us-east-1c"]
  public_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]

  tags = local.common_tags
}

# use outputs
resource "aws_security_group" "x" {
  vpc_id = module.vpc.vpc_id
}
```

## Module Principles

### Good Module
- Single responsibility (e.g., "VPC")
- Reasonable defaults for most users
- Few required inputs
- Clear outputs
- Examples in `examples/`
- README with usage
- Pinned provider versions
- Pure (no provider blocks; consumer configures)

### Anti-Patterns
- Wrap a single resource (no value-add)
- Too many input variables (configurability for its own sake)
- Provider blocks inside (consumers can't override)
- Hard-coded names (collisions)

## Module Sources

```hcl
source = "./modules/vpc"                                              # local
source = "git::https://github.com/org/repo.git//modules/vpc?ref=v1.0"  # git tag
source = "github.com/org/repo//modules/vpc?ref=v1.0"                   # shorthand
source = "registry.terraform.io/terraform-aws-modules/vpc/aws"        # registry
source = "app.terraform.io/<org>/<name>/<provider>"                   # private TFC registry
source = "s3::https://s3-eu-west-1.amazonaws.com/bucket/m.zip"        # s3
source = "git::ssh://git@github.com/org/repo.git//modules/vpc?ref=..."
```

## Versioning

Tag modules with semver (`v1.2.3`). Consumers pin:
```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"   # ≥ 5.0, < 6.0
}
```

Why pin: changes in a module may break consumers.

## Composition Patterns

### Pattern 1: Building Blocks
Small, focused modules combined in a root:
```
root/
├── vpc.tf       (module "vpc")
├── eks.tf       (module "eks")
├── rds.tf       (module "rds")
```

### Pattern 2: Composite / Higher-Order
```
modules/
├── vpc/
├── eks/
└── stack/
    └── main.tf (uses vpc + eks + rds)

root/
└── main.tf (uses stack)
```

### Pattern 3: Stage-Specific Roots
```
live/
├── prod/
│   ├── network/     (uses module/vpc)
│   ├── compute/     (uses module/eks)
│   └── data/        (uses module/rds)
├── staging/
└── dev/
```

Each directory is a separate Terraform state. Reference outputs across via `terraform_remote_state` data source.

## Cross-Module References

### Same Root (just use module outputs)
```hcl
module "eks" {
  source = "./modules/eks"
  vpc_id = module.vpc.vpc_id
}
```

### Different Roots (remote state)
```hcl
data "terraform_remote_state" "network" {
  backend = "s3"
  config = {
    bucket = "my-tf-state"
    key    = "prod/network/terraform.tfstate"
    region = "us-east-1"
  }
}

module "eks" {
  source = "./modules/eks"
  vpc_id = data.terraform_remote_state.network.outputs.vpc_id
}
```

Or use data sources (`data "aws_vpc"`) — looser coupling.

## Module Registry

### Public Terraform Registry
- `registry.terraform.io`
- Vetted community modules
- e.g., `terraform-aws-modules/vpc/aws` (excellent VPC module)

### Private Registry
- Terraform Cloud / Enterprise
- Your org's modules
- Versioned

## Module Testing

### Terratest (Go-based, mature)
```go
func TestVPC(t *testing.T) {
    opts := &terraform.Options{
        TerraformDir: "../examples/basic",
        Vars: map[string]interface{}{"name": "test"},
    }
    defer terraform.Destroy(t, opts)
    terraform.InitAndApply(t, opts)
    
    vpcId := terraform.Output(t, opts, "vpc_id")
    assert.Contains(t, vpcId, "vpc-")
}
```

### Terraform Test (built-in, 1.6+)
```hcl
# tests/basic.tftest.hcl
run "create_vpc" {
  command = apply
  variables {
    name = "test"
    cidr = "10.0.0.0/16"
  }
  assert {
    condition     = output.vpc_id != ""
    error_message = "VPC ID should not be empty"
  }
}
```

Native, no Go required.

### Other
- **kitchen-terraform** (legacy, Ruby/Inspec)
- **awspec** (Ruby)
- **policy-as-code** for compliance testing (OPA, Sentinel, Checkov)

## CI Integration

```yaml
- name: terraform fmt
  run: terraform fmt -check -recursive
- name: terraform validate
  run: terraform init -backend=false && terraform validate
- name: tfsec
  uses: aquasecurity/tfsec-action@v1
- name: checkov
  uses: bridgecrewio/checkov-action@v12
- name: terraform plan
  run: terraform plan -out=plan.tfplan
```

## Interview Themes

- "Module design — what makes a good one?"
- "Composition vs monolithic modules"
- "How do you test Terraform modules?"
- "Walk me through a multi-env setup"
- "Cross-module references — patterns"
