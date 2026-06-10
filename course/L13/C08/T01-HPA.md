# L13/C08/T01 — Horizontal Pod Autoscaler (HPA)

## Learning Objectives

- Configure HPA
- Use custom metrics

## HPA

Scales replicas based on metrics:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## How It Works

Controller loop:
1. Every 15s: query metrics for pods
2. Calculate desired replicas
3. Update Deployment replica count

```
desiredReplicas = ceil(currentReplicas × currentMetric / targetMetric)
```

For CPU 70% target, current 100%: scale up.
For 50%: scale down.

## Requirements

- Metrics Server (or custom metrics adapter) installed
- Pod resource requests defined
- Deployment / ReplicaSet / StatefulSet target

```bash
kubectl top pod    # tests metrics-server
```

## Metric Types

### Resource (CPU/Memory)
```yaml
- type: Resource
  resource:
    name: cpu
    target:
      type: Utilization
      averageUtilization: 70
```

Percentage of request.

### Or AverageValue
```yaml
target:
  type: AverageValue
  averageValue: 500m
```

Absolute value per pod.

## Custom Metrics

```yaml
- type: Pods
  pods:
    metric:
      name: http_requests_per_second
    target:
      type: AverageValue
      averageValue: 100
```

For Pod metric (per pod).

Or Object:
```yaml
- type: Object
  object:
    describedObject:
      apiVersion: networking.k8s.io/v1
      kind: Ingress
      name: my-ingress
    metric:
      name: requests_per_second
    target:
      type: Value
      value: 1000
```

## Custom Metrics Adapter

For non-CPU/memory:
- Prometheus Adapter
- Datadog Adapter
- KEDA (covered T05)

```bash
helm install prometheus-adapter prometheus-community/prometheus-adapter
```

Configure rules mapping Prometheus metrics → K8s metrics API.

## Multiple Metrics

```yaml
metrics:
- type: Resource
  resource:
    name: cpu
    target: {type: Utilization, averageUtilization: 70}
- type: Resource
  resource:
    name: memory
    target: {type: Utilization, averageUtilization: 80}
- type: Pods
  pods:
    metric: {name: http_requests_per_second}
    target: {type: AverageValue, averageValue: 100}
```

HPA scales to satisfy ALL (takes max desired).

## Scaling Behavior

```yaml
behavior:
  scaleUp:
    stabilizationWindowSeconds: 0
    policies:
    - type: Percent
      value: 100      # double per period
      periodSeconds: 60
    - type: Pods
      value: 4        # +4 per period
      periodSeconds: 60
    selectPolicy: Max
  scaleDown:
    stabilizationWindowSeconds: 300   # 5 min cooldown
    policies:
    - type: Percent
      value: 10
      periodSeconds: 60
```

Up: aggressive (handle spike).
Down: gradual (avoid flapping).

## Stabilization Window

Smooths metrics:
- ScaleUp: 0s (immediate)
- ScaleDown: 300s default (wait 5 min)

For: avoid flap on transient metrics.

## Min / Max Replicas

```yaml
minReplicas: 2     # never less
maxReplicas: 20    # never more
```

minReplicas=2 for HA. Don't set to 1.

maxReplicas: budget cap; sanity limit.

## HPA Limits

- 15s default polling
- Metrics latency adds (Prometheus scrape interval)
- Real reaction: 30-60s

For sub-second: HPA not the tool.

## Anti-Patterns

### Memory HPA on JVM
JVM allocates heap upfront; memory hovers at limit. HPA misleads.

Use CPU or custom metric (requests, queue depth).

### CPU HPA Without Limits
CPU usage > 100% possible (using all node CPU). HPA goes wild.

Set CPU request appropriately.

### Wrong Target
- 90% CPU: too tight; spikes cause scale storm
- 30% CPU: too loose; waste resources

Start 70%; tune.

## Real-World Example

Web service:
```yaml
metadata:
  name: web-hpa
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
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 600
      policies:
      - type: Percent
        value: 20
        periodSeconds: 120
    scaleUp:
      stabilizationWindowSeconds: 30
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
```

Aggressive up; conservative down.

## Worker Pool (Queue-Based)

```yaml
metrics:
- type: External
  external:
    metric:
      name: sqs_messages
      selector:
        matchLabels:
          queue: my-queue
    target:
      type: AverageValue
      averageValue: 30
```

External metric (AWS SQS queue depth via Prometheus adapter).

## KEDA Better for Events

KEDA: event-driven autoscaling:
- Scales to 0 when idle
- Many sources (Kafka, SQS, RabbitMQ, Redis)
- More flexible than HPA

Covered T05.

## HPA + VPA

Don't use HPA + VPA on same metric:
- HPA on CPU
- VPA on CPU: conflict

Use:
- HPA on CPU
- VPA on memory

Or HPA only.

## HPA Status

```bash
kubectl get hpa
kubectl describe hpa web-hpa
```

Shows current/target, recent events.

## Common Mistakes

- minReplicas=1 (no HA)
- Memory HPA for JVM
- No behavior config (flapping)
- Wrong target percentage
- Missing pod resource requests
- maxReplicas too low (caps at peak)

## Best Practices

- minReplicas ≥ 2
- CPU 70% start
- Behavior config to prevent flap
- Pod requests defined
- Test in staging
- Combine with PDB
- Monitor scaling events

## Monitoring

```
# Prometheus
kube_horizontalpodautoscaler_status_current_replicas
kube_horizontalpodautoscaler_status_desired_replicas
```

Dashboard: actual vs desired over time.

## HPA + Cluster Autoscaler

HPA increases replicas; if pods Pending, Cluster Autoscaler / Karpenter adds nodes.

Combined: handles bursts beyond cluster capacity.

## Cooldown Mechanics

Up: stabilization 0s → react immediately.
Down: 300s → don't shrink right after scale up (which might be transient).

Tune for app:
- Sticky session app: longer down (don't break sessions)
- Stateless: shorter down OK

## Limitations

- Polls every 15s (not real-time)
- Requires metrics collection (delay)
- Scaling itself takes time (pod startup)
- 30-90s from spike to readiness

For instant: pre-warm with provisioned capacity.

## Quick Refs

```bash
# Create HPA (CLI)
kubectl autoscale deployment web --cpu-percent=70 --min=2 --max=10

# Get
kubectl get hpa

# Describe
kubectl describe hpa web-hpa

# Apply YAML
kubectl apply -f hpa.yaml
```

## Interview Prep

**Junior**: "What is HPA."

**Mid**: "HPA on CPU vs memory."

**Senior**: "Custom metrics adapter."

**Staff**: "Scaling architecture for spiky traffic."

## Next Topic

→ [T02 — Vertical Pod Autoscaler (VPA)](T02-VPA.md)
