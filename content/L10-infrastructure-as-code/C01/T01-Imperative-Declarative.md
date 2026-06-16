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

## Convergence vs Goal-Seeking

Declarative tools are **goal-seeking**: you state the end goal; the tool finds a path. Each run re-evaluates current state and converges toward desired.

- Run 1: 0 resources → desired 3 → creates 3
- Run 2: 3 exist → desired 3 → no-op
- Someone deletes 1 manually → 2 exist → desired 3 → creates 1

Imperative scripts don't converge; they execute. Re-running a "create 3" script that doesn't check first creates 3 *more* (or errors on a name clash). Convergence is the property that makes declarative safe to re-run.

## The Order Problem

Imperative: **you** order the steps. Create VPC before subnet, subnet before instance. Get it wrong → failure mid-script, partial state.

Declarative: the tool builds a **dependency graph** (DAG) from references and orders for you.

```hcl
resource "aws_subnet" "main" {
  vpc_id = aws_vpc.main.id   # implicit dependency → VPC first
}
```

Terraform sees `aws_vpc.main.id` referenced inside the subnet and creates the VPC first automatically. Parallelizes independent resources. This is a major reason declarative wins for large graphs — humans are bad at hand-ordering 200 resources.

## Common Mistakes

- **Mixing the two without discipline** — running an imperative `aws cli` change on infra Terraform owns, then being surprised when the next `apply` reverts it (drift).
- **Treating `terraform apply` as imperative** — assuming it "runs commands" in file order. It doesn't; order comes from the dependency graph, not line order.
- **Imperative provisioners as a crutch** — leaning on `local-exec`/`remote-exec` for logic the declarative model should own; these break idempotency and don't show in `plan`.
- **No drift detection** — declaring infra in code but never running a scheduled `plan`, so manual console changes silently accumulate.
- **Procedural thinking in a declarative tool** — trying to express "do X, wait, then do Y" with `depends_on` chains instead of reaching for the right tool (a pipeline, a Lambda, a script).
- **Idempotency assumed, not verified** — assuming a hand-written Ansible `command:`/`shell:` task is idempotent when it isn't (no `creates:`/`changed_when:` guard).

## Best Practices

- **Declarative as the default for infrastructure** — Terraform/CloudFormation/Pulumi for anything that lives longer than an afternoon.
- **Imperative only at the edges** — one-off debugging, disaster-recovery surgery, initial bootstrap of the state backend itself.
- **Always review the plan/diff before applying** — the visible diff is the headline benefit of declarative; don't `apply -auto-approve` blind in prod.
- **Lock down the imperative path** — IAM/SCP to block console and CLI mutations on resources under IaC, so the declarative source of truth stays authoritative.
- **Run drift detection on a schedule** — periodic `terraform plan` (or `-refresh-only`) in CI to catch out-of-band changes early.
- **Keep escape hatches narrow and documented** — when you must drop to imperative (provisioner, external data source), wrap it, comment why, and prefer a real provider resource if one exists.
- **Make imperative steps idempotent** — guard shell/CLI actions with existence checks so re-runs are safe.

## Quick Refs

```bash
# Declarative (Terraform) — describe, diff, converge
terraform plan        # show diff between desired (code) and actual (state/cloud)
terraform apply       # converge actual → desired
terraform plan -refresh-only   # detect drift without changing config

# Imperative (AWS CLI) — direct, sequential, no state
aws ec2 run-instances --image-id ami-xxx --instance-type t3.micro
aws ec2 create-tags --resources i-xxx --tags Key=Name,Value=web

# Idempotent imperative (manual guard)
aws ec2 describe-instances --instance-ids i-xxx >/dev/null 2>&1 \
  || aws ec2 run-instances ...
```

| Property | Imperative | Declarative |
|---|---|---|
| You specify | How (steps) | What (end state) |
| Idempotent | Manual checks | Built-in |
| Drift detection | No | Yes (`plan`) |
| Ordering | You | Tool (DAG) |
| State tracking | None | State file |
| Re-run safe | Not by default | Yes (converges) |
| Best for | Ad-hoc, DR surgery | Day-2 infra |

## Interview Prep

**Junior**: "What's the difference between imperative and declarative?"
> Imperative tells the system *how* — a sequence of commands (`aws ec2 run-instances ...`). Declarative describes *what* you want — the desired end state (`resource "aws_instance" "web" { ... }`) — and the tool figures out how to get there. Bash and the AWS CLI are imperative; Terraform, CloudFormation, and Kubernetes manifests are declarative.

**Mid**: "When would you pick each?"
> Declarative for anything long-lived: infrastructure, app config, day-2 operations — you get idempotency, a reviewable diff, and drift detection. Imperative for one-offs: a quick experiment, an initial bootstrap, or emergency surgery during an incident where you need direct control and the declarative loop is too slow. In practice most stacks are declarative for the infra and keep a few imperative scripts at the edges. Ansible is the in-between case — declarative modules (`apt: state=present`) with imperative orchestration.

**Senior**: "How does drift detection work in a declarative tool, and why can't imperative tools do it?"
> A declarative tool keeps a record of what it manages — Terraform's state file, CloudFormation's stack, a Kubernetes controller's view. To detect drift it refreshes (queries the real resource), compares actual against desired (the code), and reports the delta: `terraform plan` or `-refresh-only` surfaces "modified outside Terraform." Imperative tools keep no state — they fire commands and forget — so there's no recorded "desired" to diff against; they're structurally blind to drift. You mitigate drift by locking down the imperative path (IAM/SCP blocking console changes) and running scheduled plans.

**Staff**: "We have 300 engineers, a mix of Terraform, hand-run CLI scripts, and ClickOps. How do you move the org to a declarative, drift-free posture without halting delivery?"
> Three fronts in parallel. **(1) Establish the source of truth.** Inventory what's managed where; import the highest-value, most-changed resources into Terraform first (brownfield import blocks), per-team, never big-bang. Everything new is declarative by default — a paved road of modules and a pipeline so the easy path *is* the declarative path. **(2) Close the imperative back doors.** Progressively remove human write access to the console and ad-hoc CLI on IaC-owned accounts via SCPs and permission boundaries; break-glass is audited and time-boxed. This is what actually makes drift go away — not the tool, but removing the ways to bypass it. **(3) Make drift visible and cheap to fix.** Scheduled `plan`/`-refresh-only` in CI with alerts on non-empty diffs; a dashboard (Terraform Cloud, AWS Config) so drift is a tracked metric, not a surprise. The cultural shift is the hard part: declarative changes feel slower than SSH-and-fix, so you invest in fast pipelines, good modules, and a fast break-glass so the declarative path is rarely the bottleneck. I'd sequence by blast radius — networking and IAM into IaC first (highest drift cost), stateless app tiers next, stateful last — and measure success by percent of changes that flow through code review versus out-of-band.

## Next Topic

→ [T02 — Mutable vs Immutable Infrastructure](T02-Mutable-Immutable.md)
