# L10/C01 — IaC Fundamentals

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Imperative-Declarative.md) | Imperative vs Declarative | 0.5 hr |
| [T02](T02-Mutable-Immutable.md) | Mutable vs Immutable Infrastructure | 0.5 hr |
| [T03](T03-GitOps-Infra.md) | GitOps for Infrastructure | 0.5 hr |

## Imperative vs Declarative

### Imperative
> Tell the system **how** to do it, step by step.

Example (bash):
```bash
aws ec2 run-instances --image-id ami-X --count 2
aws ec2 wait instance-running --instance-ids ...
aws elbv2 register-targets --target-group-arn ... --targets ...
```

If anything changes between runs, you have to figure out the diff.

### Declarative
> Tell the system **what** you want; let it figure out how.

Example (Terraform):
```hcl
resource "aws_instance" "web" {
  count         = 2
  ami           = data.aws_ami.latest.id
  instance_type = "m6i.large"
}
```

The tool computes the diff between desired and actual.

### Why Declarative Wins (for infra)
- Idempotency — running again is safe
- Convergence — system always moves toward desired state
- Diff visibility — see what will change before applying
- Easier reasoning — describe end state, not intermediate states
- Drift detection — compare actual to desired

## Mutable vs Immutable Infrastructure

### Mutable (legacy)
- Servers are pets — patched, upgraded, hand-tuned
- Long-lived
- Drift inevitable over time
- "Cattle vs pets" — these are pets

### Immutable
- Servers are cattle — never modified after deploy
- New version = new server, replace old
- Built from versioned images (AMI, container image)
- Zero drift

### Implications
- **Mutable**: SSH in, run `apt upgrade`, modify config files
- **Immutable**: bake new image with changes, deploy, kill old

### Tooling
- **Mutable**: Chef, Puppet, Ansible (in mutable mode)
- **Immutable**: Packer (bake images), containers, K8s

Modern cloud-native is mostly immutable: containers, Lambda (new version, no in-place patch), AMIs replaced not patched.

## GitOps for Infrastructure

> Git is the source of truth. Reconciliation moves real infra toward Git state.

Principles:
- **Declarative state in Git** — Terraform/manifests
- **Versioned + immutable** — history is the audit trail
- **Pulled automatically** — controller reconciles
- **Continuous reconciliation** — drift detection + correction

### Patterns

**Terraform via CI** (pull from Git, apply on merge):
```
PR → terraform plan in CI
Merge → terraform apply (manual approval gate optional)
```

**Atlantis** — PR-driven workflow with Terraform:
- Posts `terraform plan` output on PR
- Apply via comment
- Lock per directory

**Crossplane / Config Connector** — K8s controllers that provision cloud resources from K8s CRDs. Real GitOps for infra.

**Pulumi Automation API** — programmatic Pulumi runs (similar to Terraform Cloud).

### vs Click-Ops

Manual cloud console clicks are an anti-pattern:
- No history
- No reviews
- No reproducibility
- Encourages drift

Mandate IaC; detect drift (Terraform Cloud, native AWS Config rules).

## Benefits of IaC

| Benefit | What it Means |
|---|---|
| Version control | Diff, blame, rollback |
| Code review | Multiple eyes before change |
| Automation | CI runs plans, applies |
| Reproducibility | Same code → same infra anywhere |
| Documentation | Code is the doc (mostly) |
| Disaster recovery | Re-create from code |
| Multi-environment | Same code, different vars per env |
| Drift detection | Compare actual vs declared |

## Tooling Landscape

- **Cloud-native**: CloudFormation, ARM/Bicep, Deployment Manager
- **Multi-cloud declarative**: Terraform, OpenTofu (fork)
- **Multi-cloud programming**: Pulumi, AWS CDK, CDK for TF (CDKTF)
- **Kubernetes-extending**: Crossplane, Config Connector
- **Higher-level**: Anthos Config Management, Atlantis

## Interview Themes

- "Imperative vs declarative — example"
- "Immutable infrastructure — what does it solve?"
- "GitOps — define and apply to infra"
- "Compare CloudFormation, Terraform, Pulumi"
- "Why click-ops is an anti-pattern"
