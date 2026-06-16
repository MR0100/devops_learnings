# L10/C01/T02 — Mutable vs Immutable Infrastructure

## Learning Objectives

- Distinguish mutable / immutable
- Apply immutable where possible

## Mutable Infrastructure

Modify in-place:
- SSH to VM; install new package
- Edit config; restart
- Apply patches

Traditional ops. Familiar.

## Immutable Infrastructure

Never modify; replace.

- Bake new AMI / image with changes
- Launch new instances
- Decommission old

"Cattle vs pets."

## Why Immutable

### Reproducibility
Image = exact state. Launching it elsewhere = same. Modify VM in-place: state drifts; can't reproduce.

### Snowflake Servers
"Long-running VM with 5 years of manual changes" = snowflake. Nobody knows true state.

Immutable: each VM identical from image.

### Rollback
Failed deploy: launch old image; cut traffic. Vs un-installing package and hoping.

### Audit
What's running? Look at image version. Vs SSHing to investigate.

### Security
Compromised VM: destroy; replace. Vs forensic cleaning (slow, uncertain).

### Configuration Drift
Mutable: ops engineer SSHes; tweaks. Days later: forgotten; can't reproduce.

Immutable: change only via new image. No SSH.

## Patterns

### AMI Pipeline
1. Packer builds AMI with code + config
2. AMI versioned in registry
3. ASG launches from AMI
4. Deploys = new AMI; ASG rolls out
5. No SSH ever (debug via logs)

### Container Image
1. Dockerfile builds image
2. Image in registry
3. K8s deployment references image
4. Deploy = new image tag
5. Old pods replaced

## Hybrid

Most systems mix:
- App tier: immutable (containers / AMIs)
- Stateful (DB): mutable (in-place upgrade typical)
- Network: declarative + applied (terraform applies in-place)

Pure-immutable everywhere expensive; impractical for stateful.

## Stateful Challenges

Immutable databases:
- Hard (data persists)
- Blue/green with replication
- Test data migration

Mutable DBs more common; data has gravity.

## Build Pipeline

For VMs:
1. Source change
2. CI builds AMI (Packer)
3. Tag image (Git SHA)
4. Push to registry (AMI / ECR)
5. Deploy: ASG with new AMI
6. Rolling replacement

For containers similar.

## Tooling

- Packer: build AMIs / images
- Docker / Podman: container images
- Terraform: infra (replaces resources sometimes)
- Spinnaker / Argo CD / FluxCD: orchestrate deploys

## Immutable Resources via Terraform

```hcl
resource "aws_instance" "web" {
  ami = "ami-xxxxx"
}
```

Change AMI in Terraform → Terraform plans replace (destroy + create).

For non-trivial: Blue/Green pattern, ASG with health checks.

## When Mutable

- Stateful (DB, file storage)
- High update freq + state evolution
- Cost (replacement too expensive)

E.g., RDS: in-place engine upgrade vs replace + migrate.

## Cattle vs Pets

Pets:
- Named (web-server-01)
- Hand-managed
- Loved when broken
- Replaced rarely

Cattle:
- Numbered (web-fleet-1, 2, 3, ...)
- Replaced freely
- Health checked
- Auto-replaced

Modern: cattle. Pet patterns = anti-pattern at scale.

## Drift Prevention

Immutable + IAM lockdown:
- No SSH in production
- No console mods
- All changes via pipeline

Mutable + drift:
- Someone fixes prod manually
- Forgotten
- Next deploy: undoes
- Or: state diverges silently

## Trade-offs

Immutable:
- Higher build cost (CI runs)
- Slower iteration (test, build, deploy)
- Better reliability
- Lower ops debt

Mutable:
- Faster small changes (SSH; restart)
- More ops debt (drift, snowflakes)
- Risky at scale

For prod / production-critical: immutable.

## Lambda + Container

Lambda: immutable by definition (function deployed; can't SSH).

ECS / EKS containers: immutable image + pod replacement.

Default modern.

## Anti-Patterns

- SSH to production
- Hand-edit /etc/* on prod
- Hot fix without code change
- "I'll just install this on prod" mentality

## Best Practices

- AMI / image pipeline
- Versioned (Git SHA tag)
- ASG / orchestrator replaces
- No SSH (use SSM if must)
- Logs / metrics external
- Stateless apps preferred

## When Pure Immutable Hard

- Legacy app expecting persistent disk
- Stateful service (need replication)
- Expensive build (huge image / slow startup)

For those: hybrid; mutable in some dimensions.

## K8s

Pods immutable: spec doesn't change; replaced.

Deployments declare; ReplicaSet manages pods.

Image change → new pods; old terminated.

## Practical Migration

Mutable → immutable:
1. Containerize app
2. CI builds images
3. ASG / K8s deployment uses images
4. Block SSH
5. Deploys via pipeline

Takes months for complex apps. Worth it.

## Configuration

For immutable: config baked in image OR injected at runtime.

- Bake: simple; image version = config version
- Inject: 12-factor; config via env / Secrets Manager

Modern: inject. Image stays generic.

## Phoenix Server

Periodically replace ALL servers from fresh image. Forces drift to nil.

For: high-security; ensure consistency.

## Common Mistakes

- "I'll just patch in place this once"
- Long-running mutable VMs
- No image pipeline
- Image build manual (not CI)

## Quick Refs

```bash
# Bake an immutable image (Packer)
packer build app.pkr.hcl          # produces a versioned AMI / image

# Tag image with the Git SHA for traceability
docker build -t myrepo/app:$(git rev-parse --short HEAD) .

# Roll out new image, no in-place mutation
aws autoscaling start-instance-refresh --auto-scaling-group-name web   # AMI
kubectl set image deploy/app app=myrepo/app:v1.2.3                     # container
```

| | Mutable | Immutable |
|---|---|---|
| Change model | Modify in place (SSH, patch) | Replace (new image) |
| Analogy | Pets | Cattle |
| Drift | Accumulates | Zero |
| Rollback | Un-patch and hope | Re-deploy old image |
| Build cost | Low | Higher (CI bakes image) |
| Best for | Stateful (DB) | Stateless app tier |
| Tooling | Chef, Puppet, Ansible | Packer, Docker, ASG/K8s |

## Interview Prep

**Mid**: "Mutable vs immutable."

**Senior**: "AMI pipeline design."

**Staff**: "Migrate legacy mutable to immutable."

## Next Topic

→ [T03 — GitOps for Infrastructure](T03-GitOps.md)
