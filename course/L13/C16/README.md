# L13/C16 — Troubleshooting K8s

## Topics

- **T01 kubectl describe, logs, exec, debug** — The first 4 tools you reach for. `kubectl debug` for ephemeral debug containers.
- **T02 ImagePullBackOff, CrashLoopBackOff, OOMKilled** — Image issues (registry auth, name typo); crash loops (probes too aggressive, app fails); OOM (limit too low, memory leak).
- **T03 DNS Issues, Service Issues, Ingress Issues** — Test each layer: CoreDNS → kube-proxy → Service endpoints → Ingress controller.
- **T04 etcd Recovery** — Snapshot, restore, repair (if corrupt).
- **T05 Node Not Ready** — kubelet down, network partition, disk pressure, kernel issue.

## Diagnosis Toolkit

```bash
kubectl get pods -A --field-selector=status.phase!=Running
kubectl describe pod <pod> -n <ns>
kubectl logs <pod> -n <ns> --previous   # last failed run
kubectl logs <pod> -n <ns> -c <container>
kubectl exec -it <pod> -n <ns> -- /bin/sh
kubectl debug <pod> -it --image=nicolaka/netshoot --target=<container>
kubectl get events -n <ns> --sort-by=.lastTimestamp
kubectl top pod -n <ns>
kubectl top node
```

## Decision Tree

```
Pod problem
├── Pending → no node? insufficient resources? affinity blocks it?
│            kubectl describe pod → look at Events
├── ImagePullBackOff → image name? auth? registry reachable?
├── CrashLoopBackOff → check kubectl logs --previous; probe configuration
├── OOMKilled → kubectl describe shows reason; raise memory limit; fix leak
├── ContainerCreating stuck → CNI? CSI? container runtime?
├── Running but not Ready → readiness probe; app health
└── Running but unreachable → Service endpoints? NetworkPolicy? DNS?
```

## DNS Debugging

```bash
kubectl run dnsutils --image=registry.k8s.io/e2e-test-images/jessie-dnsutils -- sleep 3600
kubectl exec dnsutils -- nslookup kubernetes.default
kubectl exec dnsutils -- dig +trace mysvc.myns.svc.cluster.local
# Check CoreDNS pods, CoreDNS configmap, kubelet DNS settings
```

## Common Service Issues

| Symptom | Check |
|---|---|
| Service unreachable | `kubectl get endpoints` — pods matched? |
| Endpoints empty | Selector mismatch, pods not Ready |
| Endpoints present but no traffic | NetworkPolicy, kube-proxy rules, iptables |
| External LB unreachable | cloud LB health checks, security groups, NLB target health |

## etcd Recovery

```bash
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=... --cert=... --key=... \
  snapshot save /backup/etcd-$(date +%Y%m%d).db

# restore
etcdctl snapshot restore /backup/etcd.db \
  --name m1 --initial-cluster m1=https://10.0.0.10:2380 \
  --initial-advertise-peer-urls https://10.0.0.10:2380 \
  --data-dir=/var/lib/etcd-new
```

## Node Not Ready Causes

- kubelet not running → ssh and `systemctl status kubelet`
- Network: can node reach API server?
- Disk pressure (>85% disk) → DiskPressure taint added
- Memory pressure → MemoryPressure taint
- PID pressure
- Kernel deadlock (rare)

## Interview Themes

- "My pod is stuck Pending — walk me through diagnosis"
- "CrashLoopBackOff — how do you debug?"
- "DNS in K8s — how does it work and how does it fail?"
- "How do you back up and restore etcd?"
