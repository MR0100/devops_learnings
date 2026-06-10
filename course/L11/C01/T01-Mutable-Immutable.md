# L11/C01/T01 — Mutable vs Immutable Patterns

## Learning Objectives

- Understand mutable vs immutable infra
- Choose pattern

## Mutable Infrastructure

Servers modified in place:
```
1. Boot VM with base OS
2. Run Ansible / Chef / Puppet
3. Configure
4. Updates: re-run config tool on same VM
5. State: drifts over time
```

For: legacy, hybrid, day-2.

## Immutable Infrastructure

New servers replace old:
```
1. Build AMI with everything baked in
2. Launch ASG with AMI
3. Update: build new AMI, replace ASG (blue/green)
4. Old VMs destroyed
5. State: pristine each time
```

For: cloud-native, containers.

## Trade-Offs

| | Mutable | Immutable |
|---|---|---|
| Drift | Common | Impossible |
| Debug | "Why is this VM broken?" | "Roll back to last good" |
| Update speed | Fast (in place) | Slow (rebuild + deploy) |
| Rollback | Hard | Trivial |
| Snowflakes | Common | Impossible |
| Day-2 patching | Live OS patch | New AMI |
| Stateful | Easy | Hard (need persistent storage) |

## Why Immutable Won

- Containers + K8s: deployments = immutable
- AMIs / images cheap to build
- Cattle vs pets philosophy
- Predictable
- Easier debugging
- Auto-scaling friendly

## Why Mutable Still Exists

- Stateful (DBs hard to immutable)
- Hybrid (on-prem servers stay around)
- Legacy
- Day-2 ops (config drift fixes)
- Bare metal

## Cattle vs Pets

### Pets
Named, cared for individually.
"Web01 is acting up; fix it."

For: traditional ops.

### Cattle
Numbered, interchangeable.
"Replace instance i-abc123 with new."

For: cloud-native.

## Phoenix Servers

Mutable, but rebuilt regularly:
```
Every week: destroy and rebuild from scratch
```

Combines:
- Mutable convenience
- Reduces drift accumulation

Conceptual middle ground.

## When Mutable (Ansible)

### Day-2 Ops
- Restart services
- Rotate certificates
- Patch CVE quickly
- Update config files

### Hybrid
On-prem servers: can't easily rebuild AMI.

### Stateful
Databases configuration: in-place tuning.

### Legacy
Pre-cloud apps.

## When Immutable

### Stateless Web Tier
Build AMI; deploy via ASG.

### Containers
Image is immutable by design.

### Functions / Serverless
Inherently immutable.

### Multi-region / multi-cloud
Image-based portable.

## Hybrid Pattern

```
Base AMI built by Packer (Ansible during build)
   ↓
Deploy AMI to ASG
   ↓
Day-2 patches: rebuild AMI; rolling update
   ↓
For emergency fixes: Ansible to live VMs (rare)
```

Best of both.

## Packer + Ansible

```bash
packer build template.pkr.hcl
```

```hcl
source "amazon-ebs" "ubuntu" {
  ami_name = "myapp-{{timestamp}}"
  instance_type = "t3.micro"
  source_ami_filter { ... }
}

build {
  sources = ["source.amazon-ebs.ubuntu"]

  provisioner "ansible" {
    playbook_file = "playbook.yml"
  }
}
```

Build immutable image via mutable config tool.

For: production AMIs.

## Lifetime

### Cattle
- Containers: minutes
- VMs in ASG: hours-days
- Replaced on deploy

### Pets
- Months-years
- Long-lived state

Aim: cattle for stateless; pets for stateful.

## State Persistence

Immutable servers:
- State in DB
- Object storage
- Persistent volumes (K8s)
- NOT on the VM itself

Anything on the VM = lost on rebuild.

## Drift Detection

### Mutable
- Ansible --check
- Puppet noop
- Chef why-run
- Continuous reconciliation

### Immutable
- Doesn't drift (rebuilt fresh)
- Compare AMI to running

## CI/CD Implications

### Mutable
```
Code → CI → Test → Ansible push to servers
```

### Immutable
```
Code → CI → Test → Build image → Deploy new image
```

Image-based: clear audit trail.

## Rollback

### Mutable
"Re-run Ansible with old playbook." Risky.

### Immutable
"Point ASG at old AMI." Atomic, trivial.

## Best Practices

- Default: immutable
- Mutable for day-2 emergency + stateful
- Phoenix: rebuild regularly
- Packer + Ansible for AMI bake
- State out of VM
- CI builds artifacts; deploy is data plane

## Common Mistakes

- Mutable for stateless app (drift, debug pain)
- Immutable for stateful DB (lost data)
- No rebuild cadence (drift)
- Snowflakes (each server unique)

## Containers

Containers: maximally immutable.
- Image = artifact
- Deploy = new image
- No in-place patches

For app workloads: containers natural.

## Quick Refs

```
Mutable:    Ansible / Chef / Puppet → live servers
Immutable:  Packer → AMI → ASG/K8s
Phoenix:    Mutable + scheduled rebuild
```

## Interview Prep

**Junior**: "Mutable vs immutable."

**Mid**: "When each."

**Senior**: "Hybrid pattern."

**Staff**: "Migration to immutable."

## Next Topic

→ [T02 — Pull vs Push Models](T02-Pull-Push.md)
