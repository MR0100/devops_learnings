# L13/C20 — Production Kubernetes Checklist

## Topics

- **T01 Cluster Hardening (CIS)** — CIS K8s Benchmark. Tools: kube-bench (runs the checks), kube-hunter (pentest).
- **T02 Disaster Recovery** — Per-cluster: etcd snapshots. Per-app: Velero (cluster + PV backups).
- **T03 Cost Controls** — Right-size requests/limits, Kubecost/OpenCost, idle node consolidation (Karpenter), spot.
- **T04 Compliance Posture** — Audit logs, policy controllers (OPA/Kyverno), image scanning, NetworkPolicy default-deny.

## Production Readiness Checklist

### Security
- [ ] RBAC least privilege
- [ ] Pod Security Standards enforced (restricted in prod)
- [ ] NetworkPolicy default-deny + explicit allows
- [ ] Secrets encrypted at rest (KMS)
- [ ] Image scanning in CI + admission controller
- [ ] Image signing (Cosign) + verification policy
- [ ] No `privileged: true` outside approved DaemonSets
- [ ] Read-only root filesystem where possible
- [ ] CIS Benchmark passing
- [ ] Audit logs centralized and alerted

### Reliability
- [ ] Multi-AZ control plane (managed: confirmed; self-managed: 3+ nodes)
- [ ] etcd backup automation + restore drill quarterly
- [ ] PDBs on critical Deployments
- [ ] Topology spread on critical Deployments
- [ ] Liveness, readiness, startup probes on every workload
- [ ] Resource requests/limits sane
- [ ] HPA where applicable
- [ ] PriorityClass for critical workloads
- [ ] Cluster Autoscaler / Karpenter configured

### Observability
- [ ] Prometheus + Grafana operational
- [ ] Alerting on SLO burn (not just thresholds)
- [ ] Logs to central system (Loki, ELK, or cloud)
- [ ] Distributed tracing in place (OpenTelemetry)
- [ ] Runbooks linked from alerts

### Operations
- [ ] GitOps in place
- [ ] No manual `kubectl apply` to prod
- [ ] Upgrade plan + cadence
- [ ] Capacity headroom 20–30%
- [ ] Cost dashboard per team/namespace
- [ ] On-call rotation with escalation

## DR Strategy with Velero

```bash
velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.9 \
  --bucket my-velero-backups \
  --backup-location-config region=us-east-1

velero backup create daily --include-namespaces='*' --ttl 720h
velero restore create --from-backup daily-20260601
```

## Compliance Posture

- Audit logs: `/var/log/audit.log` (kube-apiserver `--audit-log-path`)
- Policy: OPA Gatekeeper or Kyverno
- Network: default-deny NetworkPolicies
- Encryption at rest + in transit
- Image provenance via SLSA

## Interview Themes

- "What's on your production K8s readiness checklist?"
- "How do you back up and restore K8s state?"
- "Velero — what does it cover?"
- "Walk me through K8s cost optimization at scale"

## End of L13

Congrats — you've finished the largest, most-tested lecture. Next is Service Mesh.

## Next

→ [L14 — Service Mesh](../../L14/README.md)
