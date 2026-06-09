# L13/C07 — Scheduling & Resources

## Topics

- **T01 Requests & Limits** — `requests` reserved by scheduler; `limits` enforced by cgroup. CPU limit throttles; memory limit OOM-kills.
- **T02 QoS Classes** — Guaranteed (req=limit on both CPU and mem), Burstable (some specified), BestEffort (nothing). Eviction priority: BestEffort first.
- **T03 Node Selectors, Affinity, Anti-Affinity** — nodeSelector is simple; nodeAffinity supports preferred/required, expressions. podAntiAffinity spreads pods across nodes/zones.
- **T04 Taints & Tolerations** — Taints repel (`NoSchedule`, `PreferNoSchedule`, `NoExecute`); tolerations allow. Use for dedicated nodes, GPU nodes, control-plane isolation.
- **T05 Topology Spread Constraints** — Modern alternative to anti-affinity. Spread evenly across zones/nodes.
- **T06 Priority & Preemption** — PriorityClass; higher-priority pods can preempt (evict) lower. `system-cluster-critical`, `system-node-critical` reserved.
- **T07 Custom Schedulers** — Multi-scheduler clusters. Scheduler plugins framework. Use for ML/HPC workloads with specific needs.

## Resource Recommendations

| Workload | Strategy |
|---|---|
| Latency-sensitive | Guaranteed QoS; CPU request=limit; integer CPUs (CPU Manager static policy) |
| Batch | Burstable; high requests, looser limits |
| Best-effort tasks | BestEffort |

## CPU Limit Trap

Setting `cpu.limit=1` doesn't mean "use up to 1 CPU"; it means "throttled if you exceed 100ms of CPU time in any 100ms window". For Java/Go apps with many threads, this often causes p99 spikes. **Common advice: don't set CPU limits**; set requests only.

## Anti-Affinity Pattern (Spread Across Zones)

```yaml
spec:
  topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: topology.kubernetes.io/zone
    whenUnsatisfiable: DoNotSchedule
    labelSelector:
      matchLabels:
        app: web
```

## Interview Themes

- "What's the difference between request and limit?"
- "Why do people say not to set CPU limits?"
- "Spread my pods across AZs — how?"
- "How does eviction order work?"
