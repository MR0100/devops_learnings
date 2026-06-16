# L13/C18/T04 — Self-Managed vs Managed Tradeoffs

## Learning Objectives

- Decide K8s deployment strategy
- Calculate true costs

## Comparison

| | Managed (EKS/GKE/AKS) | Self-Managed (kops/kubeadm) |
|---|---|---|
| Control plane cost | $73/mo per cluster | Free (you run VMs) |
| Node cost | EC2/VM | EC2/VM |
| Operational burden | Low | High |
| Customization | Limited | Full |
| Upgrade complexity | Click | Multi-step |
| HA | Built-in | You configure |
| Backup | Provider often handles | You handle |
| Compliance certs | Provider's | Yours |
| Cloud-specific features | Native | Manual |

## Total Cost

### Managed
- Control plane fees
- Compute (nodes)
- Network (LBs, NAT, egress)
- Storage (EBS, etc.)
- Logging / monitoring

### Self-Managed
- Compute (control plane VMs)
- Compute (worker nodes)
- Network
- Storage
- Logging / monitoring
- **Plus**: engineering time

## Engineering Time

For managed:
- 10-20% of one DevOps engineer
- Mostly: cluster lifecycle, monitoring

For self-managed:
- 0.5-1 FTE
- Patches, upgrades, etcd, incidents

For 10 clusters: managed saves 5 FTEs.

## When Self-Managed

- Air-gapped (no Internet)
- Strict compliance (FedRAMP High, etc.)
- Specific kernel needs
- Cost-optimization at HUGE scale
- Specific cloud not supported
- Existing on-prem investment

For most: managed.

## When Managed

- New cluster, cloud-native
- Don't want control plane ops
- Standard workloads
- Smaller team
- Multi-cluster (managed easier)

## Hybrid

Some run:
- Production: managed (reliability)
- Dev: self-managed (cost / experimentation)

Or:
- Cloud: managed
- On-prem: self-managed

## Real Cost Example

10-cluster organization:
- Managed: $73 × 10 = $730/mo + nodes
- Self-managed: $0 + nodes + 1 FTE (~$150k/yr)

Managed saves $150k/yr; pays for itself.

For 1-2 clusters: similar costs.

## Operational Tasks

### Managed
- Configure (Terraform)
- Apply upgrades when notified
- Monitor cluster health
- Manage workloads

### Self-Managed (Additional)
- Patch OS on control plane
- Backup etcd
- Renew certs (mostly auto)
- Upgrade control plane components
- Manage CNI
- Manage runtime
- Tune scheduler
- Troubleshoot control plane

Real overhead.

## Disaster Recovery

### Managed
- Provider's SLA + backups
- Plus your workload backups (Velero)

### Self-Managed
- Full DR your responsibility
- etcd snapshots + restore process
- Reproducible cluster build
- Tested annually

For: more risk.

## Vendor Lock-In

Managed:
- API K8s standard
- Workloads portable
- Some cluster config provider-specific (IAM annotations etc.)

Self-managed:
- Less provider lock-in
- But still vendor-specific (AWS APIs underneath)

For pure portable: workloads + Helm charts.

## Compliance

Managed:
- Provider's certs (SOC, ISO, HIPAA, FedRAMP)
- Customer responsibility per cert
- Limited customization (less compliance flexibility)

Self-managed:
- You control everything
- Your compliance certs
- More work to certify

For regulated: depends on cert scope.

## Upgrade Speed

Managed:
- Provider releases new K8s version
- You upgrade (control plane in-place; rolling nodes)
- Lag: weeks behind upstream

Self-managed:
- Day-zero possible
- Full control of timing
- Risk of issues without provider QA

## Scale

Both scale to ~5000 nodes per cluster (K8s limit).

Beyond: multi-cluster.

Managed: provider-imposed limits (raise via support).
Self-managed: you tune (etcd, API server, scheduler).

## Production Choice

For 90%+ cloud users in 2025: managed.

Self-managed only when:
- Compliance requires
- Air-gapped
- Massive scale + cost-conscious

## Cost-Optimized Self-Managed

For 100+ cluster organizations:
- Self-managed control plane on Spot
- Saves $7300/mo (vs EKS × 100)
- Engineering team to maintain

If engineering cost < savings: worth.

## Managed Limitations

Things you can't change:
- API server flags (limited)
- Scheduler customization (some)
- etcd access (none for EKS / GKE)
- Control plane upgrades timing (during support windows)

For full control: self-managed.

## Hybrid Strategy

Common:
- Workload clusters: managed
- Special-purpose: self-managed

E.g., managed for prod web; self-managed for compliance-restricted data.

## Migration Strategies

Self-managed → Managed:
- Velero backup → restore to managed
- Or migrate workloads (kubectl apply to managed)

Test gradually.

Managed → Self-managed:
- Rare; usually scale forces
- Plan months for ops setup

## Tools Help Both

For both:
- Terraform / Crossplane: cluster provisioning
- Argo CD: app deployment
- Velero: backup
- Helm: package management

## Decision Framework

Pick managed unless:
- ☑ Compliance forbids
- ☑ Air-gapped
- ☑ Cost > 1 FTE at scale
- ☑ Need control plane mods
- ☑ Specific cloud not supported

For 95% of teams: managed.

## Real Companies

- Netflix: managed (mostly) + some self-managed
- Airbnb: managed
- Spotify: managed
- DoorDash: managed
- Google internal: self-managed (Borg → K8s)

Most adopt managed eventually.

## Cost vs Time

Managed cost: $73/mo per cluster.
Self-managed time saved: ~10 hrs/mo per cluster.

If 10 hr cost > $73 (almost always): managed.

## Best Practices

For managed:
- Use IRSA / Workload Identity
- Auto-upgrade or scheduled
- Monitor cluster + workloads
- Backup workloads (Velero)
- Documented procedures

For self-managed (if you must):
- HA control plane (3 masters)
- External etcd (HA)
- Backup etcd hourly
- Test DR annually
- Documented procedures
- Same CI/CD as workloads

## Common Mistakes

- Self-managed for "control" without actually needing
- Single control plane (no HA)
- No backups
- Skip upgrades (deprecated)

## Modern Reality

For 2026:
- Managed K8s is default
- Self-managed for niche
- Even on-prem: managed via Anthos / EKS Anywhere / Azure Arc

## Quick Refs

```bash
# Decision questions:
# 1. Compliance allows managed?
# 2. Cloud-supported managed?
# 3. Team has K8s control plane expertise?
# 4. Cost of 1 FTE > 10 × cluster fee?
# If yes to any "self-managed": rare.
# Default: managed.
```

## Interview Prep

**Mid**: "Managed vs self-managed."

**Senior**: "When self-managed justified."

**Staff**: "K8s strategy for 100-cluster org."

## Next Topic

→ Move to [L13/C19 — Performance Tuning](../C19/README.md)
