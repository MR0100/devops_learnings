# L11/C07/T02 — When to Replace with IaC + Containers

## Learning Objectives

- Identify CM that can be replaced
- Plan migration

## The Modern Stack

```
Terraform (infra)
   ↓
Packer + Ansible (image bake)
   ↓
AMI / Container image
   ↓
ASG / K8s (deploy)
   ↓
Cloud-Init or first-boot (minimal)
```

Config mgmt minimized.

## Why Replace

- Drift: in-place config drifts
- Debug: stateful VMs hard to debug
- Speed: rebuild faster than re-converge
- Audit: image artifact = clear lineage
- Rollback: image swap atomic
- Cattle vs Pets

## What CM Did

Traditional CM tasks:
1. Install packages → bake into image
2. Configure files → templates baked
3. Manage services → systemd at boot
4. Manage users → baked
5. Patch OS → new AMI
6. Day-2 ops → still need (rare)
7. Secret rotation → secrets manager + restart
8. Cluster discovery → K8s services / service mesh

Most: baked.
Few: dynamic.

## Migration Path

### Step 1: Audit
What does CM do today? Categorize:
- Bakeable (install, config, users)
- Dynamic (cluster join, IP discovery)
- Day-2 (patch, restart)

### Step 2: Bake
Move bakeable into Packer + Ansible:
```hcl
source "amazon-ebs" "base" { ... }

build {
  sources = ["source.amazon-ebs.base"]
  provisioner "ansible" {
    playbook_file = "playbook.yml"
  }
}
```

Result: golden AMI.

### Step 3: Replace Day-2 with K8s / Containers
Where possible: app in container.
- Updates: new image, rolling.
- Config: ConfigMap / env.
- Secrets: Secrets / external manager.

### Step 4: Decommission
CM only for legacy that can't move.

## Containers Replace CM

For containerized apps:
- No package install (already in image)
- No service mgmt (container engine)
- No file deploy (in image)
- No restart on config change (new image)

CM moves up: build pipeline configures.

## When CM Still Needed

### Stateful (DB)
DBs hard to immutable:
- Persistent data
- Long-lived
- Config tuning

Use CM for: postgres.conf, pg_hba.conf.

But: most managed DB (RDS / Cloud SQL) eliminate this.

### Hybrid / On-Prem
Servers stay around:
- Network gear
- Bare metal
- Hypervisors

CM for: bootstrap + ongoing.

### Day-2 Patches
Emergency CVE:
- Push fix to live VMs
- Replace AMI later

CM for: rapid response.

### OS Hardening
CIS benchmarks.
Inspec / Ansible to validate.

### Compliance Scanning
Continuous reconciliation:
- Did someone change /etc/passwd?
- Puppet/Chef reapply.

## The 80/20

For stateless web tier:
- 80% bakeable
- 20% dynamic config (env, secrets)

CM not needed.

For stateful:
- 50/50 typical.

## Cloud-Init

```yaml
#cloud-config
package_upgrade: true
packages:
  - nginx
write_files:
  - path: /etc/myapp/config
    content: |
      port: 8080
runcmd:
  - systemctl start nginx
```

Lightweight; runs first boot.

For: simple bootstrap; no CM needed.

## Image Build Pipeline

```
Code commit
   ↓
CI runs tests
   ↓
Packer builds AMI (Ansible inside)
   ↓
AMI tagged with version
   ↓
Test in staging
   ↓
Promote to prod
```

Image = artifact.

## Auto-Scaling Group

```hcl
resource "aws_launch_template" "web" {
  image_id = data.aws_ami.golden.id
  # ...
}

resource "aws_autoscaling_group" "web" {
  launch_template { ... }
  min_size = 3
  desired_capacity = 5
}
```

New deploy:
1. Build new AMI
2. Update launch template
3. Instance refresh (rolling)
4. Old replaced with new

No live config push.

## K8s Pattern

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - image: myrepo/app:v1.2.3
        envFrom:
        - configMapRef:
            name: app-config
        - secretRef:
            name: app-secrets
```

Update image tag → rolling deploy.

## What's Left for CM?

Minimal:
- Bootstrap (Cloud-Init or quick script)
- Continuous compliance (rare)
- Day-2 patches (rare; usually rebuild AMI)

For: most teams reduce CM to 5% of effort.

## Brownfield Migration

Existing fleet using Puppet:
1. Don't add to Puppet
2. New deployments: K8s / immutable
3. Old systems: rotate out (rebuild as immutable)
4. Eventually decommission Puppet

Years-long; deliberate.

## Hybrid Approach

```
New apps: K8s
Existing apps: Ansible-managed VMs
Edge devices: Cloud-Init
DBs: RDS / Cloud SQL (no CM)
Network: Terraform
Compliance: InSpec scans (CM if needed)
```

Pragmatic.

## Resistance

Common objections:
- "We've always used Chef"
- "Migration is too risky"
- "Team doesn't know K8s"

Counters:
- ROI: less ops time
- Risk: gradual migration
- Training: invest in upskill

## Greenfield Recommendation

For new project today:
- Terraform for infra
- Containers for apps
- K8s for orchestration
- ConfigMap / Secrets for config
- Image-based deploys
- Cloud-Init for first-boot scripts
- No CM tool

CM only if: legacy integration or hardening.

## Specific Replacements

### Package install
CM: `apt install nginx`
Modern: in Dockerfile / Packer.

### Config file
CM: template
Modern: ConfigMap (K8s) or build-time bake.

### User management
CM: user resource
Modern: OS Login / IAM-based SSH.

### Service start
CM: service module
Modern: container engine.

### File deployment
CM: copy / template
Modern: in image.

### Patch
CM: `apt update && apt upgrade`
Modern: new image.

### Cluster discovery
CM: exported resources / mine
Modern: K8s service / service mesh.

## Cost Comparison

### Traditional CM Operations
- Chef Server: $$
- Engineers maintaining Chef: $$$
- Drift incidents: $$
- Slow deploys: $$

### Modern
- Container registry: $
- CI/CD: $
- K8s: $$
- Engineers (more general skills): $$

Often: lower cost over 3 years.

## When NOT to Migrate

- Small org; current works
- Heavy regulated; high migration risk
- Limited K8s expertise
- Stateful workloads majority

For: keep CM but minimize.

## Best Practices

- Audit CM usage
- New apps: K8s / immutable
- Existing: gradual migrate
- Document architecture decision
- Train team
- Measure: deploy frequency, time, incidents

## Common Mistakes

- "Bigbang" migration (risky)
- New apps adding to old Chef (compounds debt)
- No K8s expertise + force K8s (chaos)
- Keep both for years without endgame

## Real Examples

### Netflix
Minimal CM. AMIs baked; Spinnaker deploys.

### Airbnb
Migrated Chef → Terraform + K8s.

### Spotify
K8s + minimal CM (Cloud-Init).

### Many FAANGM
Custom internal tools; minimal traditional CM.

## Quick Refs

```
Existing Chef/Puppet shop + many VMs → keep, plan migration
New project → no CM; containers + IaC
Hybrid → Cloud-Init + minimal Ansible
Stateful → managed services where possible
```

## Interview Prep

**Mid**: "Why move from CM."

**Senior**: "Migration strategy."

**Staff**: "Modern stack vs traditional."

**Principal**: "CM in 2026 — what's left."

## Next Topic

→ Move to [L13 — Kubernetes Deep](../../L13/README.md)
