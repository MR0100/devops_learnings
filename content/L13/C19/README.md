# L13/C19 — Day 2 Operations

## Topics

- **T01 Cluster Upgrades** — Upgrade order: etcd → control plane → addons → workers. Skew policy: kubelet can be 3 minor behind apiserver (widened from 2 by KEP-3935, GA since 1.28); kube-proxy must match its node's kubelet minor.
- **T02 etcd Backup & Restore** — Snapshot daily minimum. Restore is destructive; rebuilds the cluster state.
- **T03 Certificate Rotation** — Internal certs auto-rotate with kubeadm or managed services. External certs (Ingress) via cert-manager.
- **T04 Capacity Planning** — Track requests vs allocatable; tune to maintain headroom (typically 20–30%).

## Upgrade Strategy

```
Pre-upgrade:
  • Backup etcd
  • Review release notes & deprecations
  • Test in staging cluster
  • Check addon compatibility

Execute:
  • Upgrade control plane (apiserver, scheduler, controller-mgr)
  • Upgrade etcd if needed
  • Upgrade core addons (CoreDNS, kube-proxy)
  • Upgrade workers (rolling, one node group at a time)
  • Verify

Post-upgrade:
  • Monitor errors, restarts
  • Run regression tests
```

## Version Skew (K8s)

| Component | Skew Rule |
|---|---|
| apiserver | Newest |
| kubelet | Up to 3 minor behind apiserver (KEP-3935, GA 1.28; was 2 before) |
| controller-manager / scheduler | Same as apiserver |
| kubectl | ±1 minor |
| kube-proxy | Same minor as kubelet on its node |

## Certificate Rotation

- Internal certs (apiserver, etcd, kubelet) — kubeadm renews via `kubeadm certs renew`; or auto-renewed on kubelet by `--rotate-certificates`
- Managed clusters: cloud handles internal certs
- Application certs (Ingress TLS): cert-manager + Let's Encrypt is the standard

## Capacity Headroom Math

```
For a workload that bursts 2× under load:
  Steady-state CPU requests ≤ 50% of cluster allocatable
  Headroom = 30% for failover, scheduling pressure, scaling delay
```

## Disaster Drills

Run quarterly:
- Lose 1 control plane node
- Lose 1 AZ
- Lose etcd (restore from snapshot)
- Upgrade rollback rehearsal

## Interview Themes

- "Walk me through a K8s upgrade plan"
- "How do you back up and restore etcd?"
- "Version skew — what's allowed?"
- "Capacity planning for a 100-node cluster"
