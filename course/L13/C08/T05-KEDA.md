# L13/C08/T05 — KEDA (Event-Driven Autoscaling)

## Learning Objectives

- Use KEDA for events
- Scale to zero

## KEDA

Kubernetes Event-Driven Autoscaler:
- Scales based on external events (Kafka, SQS, Redis, etc.)
- Can scale to 0 (HPA can't)
- 60+ scalers built-in

## Install

```bash
helm install keda kedacore/keda --namespace keda --create-namespace
```

## ScaledObject

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: kafka-consumer
spec:
  scaleTargetRef:
    name: my-consumer
  minReplicaCount: 0
  maxReplicaCount: 30
  triggers:
  - type: kafka
    metadata:
      bootstrapServers: kafka:9092
      consumerGroup: my-group
      topic: my-topic
      lagThreshold: "10"
```

KEDA creates HPA under hood; manages scale.

## Scale to Zero

When no events:
- Replicas to 0
- Save cost
- Cold start when event arrives

For sporadic workloads: huge cost savings.

## Scalers

Common:
- Kafka (consumer lag)
- AWS SQS (queue depth)
- AWS Kinesis
- RabbitMQ
- Redis (list/stream length)
- Azure Service Bus / Event Hubs
- GCP Pub/Sub
- PostgreSQL / MySQL (query result)
- Prometheus (any metric)
- CPU / Memory
- Cron

## Examples

### SQS Consumer
```yaml
triggers:
- type: aws-sqs-queue
  metadata:
    queueURL: https://sqs.../my-queue
    queueLength: "5"
    awsRegion: us-east-1
  identityOwner: pod
```

Scale based on queue depth.

### Kafka Consumer
```yaml
triggers:
- type: kafka
  metadata:
    bootstrapServers: kafka:9092
    consumerGroup: workers
    topic: events
    lagThreshold: "100"
```

Scale on consumer lag.

### Redis Stream
```yaml
triggers:
- type: redis-streams
  metadata:
    address: redis:6379
    stream: events
    pendingEntriesCount: "10"
    consumerGroup: workers
```

### Prometheus
```yaml
triggers:
- type: prometheus
  metadata:
    serverAddress: http://prometheus:9090
    metricName: http_requests_per_second
    threshold: "100"
    query: sum(rate(http_requests_total[1m]))
```

Any Prom metric.

### Cron
```yaml
triggers:
- type: cron
  metadata:
    timezone: America/Los_Angeles
    start: "0 9 * * 1-5"
    end: "0 17 * * 1-5"
    desiredReplicas: "10"
```

Scale up during business hours.

## Multiple Triggers

```yaml
triggers:
- type: kafka
  ...
- type: prometheus
  ...
```

KEDA scales to max desired across triggers.

## ScaledJob

For long-running per-event:
```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledJob
metadata:
  name: process-events
spec:
  jobTargetRef:
    template:
      spec:
        containers:
        - name: worker
          image: worker:v1
  triggers:
  - type: aws-sqs-queue
    metadata: ...
  maxReplicaCount: 100
```

Each event spawns Job; doesn't reuse pods.

For: long batch tasks per event.

## Authentication

```yaml
apiVersion: keda.sh/v1alpha1
kind: TriggerAuthentication
metadata:
  name: kafka-auth
spec:
  secretTargetRef:
  - parameter: sasl
    name: kafka-secrets
    key: sasl
```

ScaledObject references:
```yaml
triggers:
- type: kafka
  authenticationRef:
    name: kafka-auth
  metadata: ...
```

For: secrets to external systems.

## IRSA / Workload Identity

For AWS SQS:
```yaml
triggers:
- type: aws-sqs-queue
  metadata:
    ...
  identityOwner: pod   # use pod's IRSA
```

## Behavior

```yaml
advanced:
  horizontalPodAutoscalerConfig:
    behavior:
      scaleUp:
        stabilizationWindowSeconds: 0
      scaleDown:
        stabilizationWindowSeconds: 300
```

Same as HPA behavior.

## When KEDA

- Event-driven workloads
- Sporadic traffic
- Want scale-to-zero
- Non-CPU metrics

## When NOT KEDA

- Steady traffic (HPA OK)
- Latency-critical (cold start)
- Simple CPU scaling (HPA enough)

## Cold Start

Scale-to-zero downside: first event waits for pod start.
- Lambda-like: 5-30s typical
- App-startup time matters

For sub-second: minReplicaCount > 0.

## Cost Savings

Sporadic worker:
- HPA: minReplicas=2 always → $50/mo
- KEDA: 0 when idle → $5/mo (most of day idle)

Sometimes 90% savings.

## Integration with Karpenter

KEDA scales pods → Pending → Karpenter adds nodes.

Combined:
- KEDA: zero pods → pod
- Karpenter: zero nodes → node
- Full elasticity

## Comparison

| | HPA | KEDA |
|---|---|---|
| Metrics | CPU/memory + custom adapter | 60+ sources |
| Scale to 0 | No | Yes |
| Setup | Simple | Per-scaler |
| Latency | Some | Same + cold start if 0 |

For events / queues: KEDA.
For CPU: HPA.

## Real-World

### SQS Worker Pool
```yaml
# Scale on queue depth
triggers:
- type: aws-sqs-queue
  metadata:
    queueURL: ...
    queueLength: "20"
minReplicaCount: 0
maxReplicaCount: 50
```

Pool 0-50 workers based on queue.

### Kafka Lag-Based
```yaml
triggers:
- type: kafka
  metadata:
    lagThreshold: "1000"
```

Scale on consumer lag (events behind).

### Daily Batch
```yaml
triggers:
- type: cron
  metadata:
    start: "0 2 * * *"
    end: "0 4 * * *"
    desiredReplicas: "10"
```

Scale up overnight; down during day.

## Multiple Triggers Logic

For multiple triggers: KEDA takes max desired.

```yaml
triggers:
- type: kafka
  metadata:
    lagThreshold: "100"
# scales to 5

- type: prometheus
  metadata:
    threshold: "100"
# scales to 3

# Final: 5 (max)
```

## Authorization

SQS access: IRSA role with `sqs:GetQueueAttributes`.

KEDA pod uses role, or pod uses its own (`identityOwner: pod`).

## Best Practices

- minReplicaCount 0 for sporadic
- minReplicaCount 1+ for latency-critical
- Test cold start time
- Monitor lag metrics
- Use TriggerAuthentication for secrets

## Common Mistakes

- minReplicaCount 0 for latency-sensitive
- Forgetting auth (KEDA can't query)
- Wrong threshold (over/under scale)
- Multiple triggers conflict (max takes priority)

## Operations

```bash
# ScaledObjects
kubectl get scaledobject

# HPA created by KEDA
kubectl get hpa
# Named: keda-hpa-<scaledobject>

# Logs
kubectl logs -n keda keda-operator-xxx
```

## Quick Refs

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: my-scaler
spec:
  scaleTargetRef:
    name: my-deployment
  minReplicaCount: 0
  maxReplicaCount: 100
  triggers:
  - type: <scaler>
    metadata: ...
```

## Interview Prep

**Mid**: "KEDA vs HPA."

**Senior**: "Scale-to-zero pattern."

**Staff**: "Event-driven architecture with KEDA."

## Next Topic

→ Move to [L13/C09 — Operators & CRDs](../C09/README.md)
