# L13/C08 — Autoscaling

## Topics

- **T01 Horizontal Pod Autoscaler (HPA)** — Scales replicas based on CPU/mem/custom metrics. v2 supports multiple metrics, behavior tuning (scaleUp/scaleDown stabilization windows).
- **T02 Vertical Pod Autoscaler (VPA)** — Adjusts pod resource requests. Updater can replace pods or be Off (recommendation mode). Don't use with HPA on same metric.
- **T03 Cluster Autoscaler** — Adds/removes nodes based on Pending pods. Per-cloud node group integration. Slow at scale-up (minutes).
- **T04 Karpenter** — AWS-originated, multi-cloud. Just-in-time node provisioning. Picks instance type per pod requirement. Fast (sub-minute). Supports spot+on-demand mix.
- **T05 KEDA (Event-Driven Autoscaling)** — Scale on queue depth, Kafka lag, Prometheus, cron, etc. Can scale to zero. Bridges to HPA.

## HPA Example

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web
  minReplicas: 3
  maxReplicas: 30
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Pods
    pods:
      metric:
        name: requests_per_second
      target:
        type: AverageValue
        averageValue: 100
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
    scaleUp:
      stabilizationWindowSeconds: 0
```

## Karpenter Provisioner Pattern

Karpenter chooses nodes per pod requirements:
- Honors topology constraints
- Bin-packs efficiently
- Supports spot with interruption handling
- Replaces nodes on-demand (consolidation)

```yaml
apiVersion: karpenter.k8s.aws/v1
kind: NodePool
metadata:
  name: default
spec:
  template:
    spec:
      requirements:
      - key: karpenter.sh/capacity-type
        operator: In
        values: ["spot", "on-demand"]
      - key: kubernetes.io/arch
        operator: In
        values: ["amd64", "arm64"]
```

## Common Issues

- HPA flapping → tune stabilizationWindow
- Cluster Autoscaler slow → use Karpenter
- VPA + HPA on CPU → fight each other; don't
- KEDA + HPA → KEDA wraps HPA; can't use both directly

## Interview Themes

- "Compare HPA, VPA, Cluster Autoscaler, Karpenter, KEDA"
- "How do you scale a Kafka consumer pod fleet?"
- "Why is HPA flapping and what tunables help?"
