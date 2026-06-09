# L10/C01/T01 — Imperative vs Declarative

## Learning Objectives

- Distinguish imperative vs declarative
- Apply right approach

## Imperative

Tell HOW to do something. Sequence of commands.

```bash
# Imperative
aws ec2 run-instances --image-id ami-xxx --instance-type t3.micro --key-name my-key
aws ec2 create-tags --resources i-xxx --tags Key=Name,Value=web
aws ec2 attach-internet-gateway --vpc-id vpc-xxx --internet-gateway-id igw-xxx
```

Run scripts. Each command modifies state.

Examples: Bash scripts, Ansible playbooks (mostly), AWS CLI.

## Declarative

Describe WHAT you want. System figures out HOW.

```hcl
resource "aws_instance" "web" {
  ami           = "ami-xxx"
  instance_type = "t3.micro"
  key_name      = "my-key"
  tags = {
    Name = "web"
  }
}
```

You declare desired state; tool reconciles.

Examples: Terraform, CloudFormation, Kubernetes YAML, Pulumi, Ansible (some).

## Trade-offs

### Imperative
Pros:
- Easy for ad-hoc tasks
- Direct control
- Familiar

Cons:
- Error-prone (idempotency hard)
- Drift over time (script doesn't track state)
- Hard to know current state
- Brittle (one failure aborts)

### Declarative
Pros:
- Idempotent (run again = same state)
- Drift detection
- Tool optimizes order
- Source of truth = code

Cons:
- Learning curve
- Sometimes restrictive (escape hatches for unusual ops)
- Abstractions can leak

## Why Declarative for Infra

For 100s of resources:
- Imperative: scripts get unwieldy; manual debugging
- Declarative: terraform plan shows diff; tool applies

For prod: declarative.
For one-off (debug, learning): imperative.

## Idempotency

Declarative tools idempotent:
- Run terraform apply → resources match desired
- Run again → no changes (no-op)

Imperative needs explicit checks:
```bash
if ! aws ec2 describe-instances --instance-ids i-xxx; then
  aws ec2 run-instances ...
fi
```

Verbose.

## State Tracking

Declarative tools record what they manage (state file):
- Terraform: terraform.tfstate
- CloudFormation: stack
- Pulumi: state

Match: code → desired; state → actual.

Imperative: no state. You hope it worked.

## Hybrid

Some tools mix:
- Ansible: declarative modules (apt: state=present) but imperative orchestration (run command)
- AWS CLI: imperative
- Terraform: declarative

For prod infra: declarative tool (Terraform).
For OS configuration: hybrid (Ansible, Chef).

## Reconciliation Loop

K8s: declarative + control loop.
- You declare 3 replicas
- Controller continuously ensures 3 running
- Self-healing

Terraform: declarative but one-shot reconciliation per `apply`.

For ongoing: controllers / operators.

## Mental Model

For declarative:
1. Code describes desired
2. Tool reads current
3. Diffs
4. Applies changes to converge

For imperative:
1. Code says "do X"
2. X happens (or doesn't; you check)
3. State changes
4. Next command operates on new state

## Examples

| Tool | Style |
|---|---|
| Bash scripts | Imperative |
| AWS CLI | Imperative |
| Ansible | Hybrid (mostly declarative modules) |
| Chef | Hybrid |
| Puppet | Declarative |
| Terraform | Declarative |
| CloudFormation | Declarative |
| Kubernetes YAML | Declarative |
| Pulumi | Declarative (in code) |
| CDK | Declarative (in code) |

## When Declarative Hurts

Some tasks awkward:
- "Migrate data from X to Y" (multi-step)
- "Run a job, wait, run another" (procedural)
- "Discover and adapt" (dynamic)

Workarounds:
- Mix tools (Terraform for infra; Lambda for runtime)
- Provisioners (Terraform local-exec)
- External data source

## Code-as-Code

Declarative tools express infra as code:
- Versioned in Git
- Reviewed in PR
- Tested
- Reused via modules

Same engineering practices as app code.

## Drift

State diverges from code:
- Manual change
- External tool
- AWS-side change

Declarative tool detects:
```bash
terraform plan
# Shows "Resource modified outside Terraform"
```

Mitigate via:
- IAM lockdown (no console changes)
- Drift detection (regular plans)
- SCP

Imperative tools blind to drift.

## When Imperative Works

- Quick experiments
- One-off operations
- Initial bootstrap
- Disaster recovery (manual surgery)

For day-2 ops: declarative wins.

## Modern Trend

- Cloud-native: declarative (K8s, Terraform, Crossplane)
- Operators: declarative + reconciliation
- GitOps: declarative + Git workflow

Industry direction: declarative.

## Operations Comparison

### Adding Subnet
Imperative:
```bash
aws ec2 create-subnet ...
aws ec2 create-route-table-association ...
aws ec2 modify-subnet-attribute ...
```

Declarative:
```hcl
resource "aws_subnet" "new" {
  vpc_id     = ...
  cidr_block = "10.0.5.0/24"
}
```

terraform apply → all set.

### Removing Resource
Imperative:
```bash
aws ec2 delete-subnet --subnet-id ...
# Forget that route table; orphaned
```

Declarative:
```bash
# Remove from code
terraform apply
# Tool deletes + cleans related
```

## Interview Prep

**Junior**: "Imperative vs declarative."

**Mid**: "When pick each."

**Senior**: "Drift detection in declarative."

## Next Topic

→ [T02 — Mutable vs Immutable Infrastructure](T02-Mutable-Immutable.md)
