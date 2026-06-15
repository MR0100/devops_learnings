# L25/C03 — Common Experiments

## Topics

- **T01 Network Latency & Loss** — Add delay or drop packets
- **T02 CPU / Memory Exhaustion** — Resource starvation
- **T03 Disk I/O Saturation** — Storage stress
- **T04 Pod / Node Kills** — Container/VM failure
- **T05 Region Failover** — Cross-region DR test

## Network Experiments

### Latency
Add 500ms delay to all traffic to a service. Tests:
- Timeout handling
- Retry behavior
- Circuit breaker
- User-visible latency budget

```yaml
# Chaos Mesh
spec:
  action: delay
  delay:
    latency: "500ms"
    jitter: "50ms"
```

### Loss
Drop X% of packets. Tests:
- TCP retransmission behavior
- App-level error handling
- Connection pooling recovery

### Partition
Split network so two halves can't talk. Tests:
- Split-brain prevention
- Leader election under partition
- Consistency vs availability tradeoffs

### Corruption
Bit-flip packets. Tests:
- Checksum handling
- Application validation

## CPU / Memory Exhaustion

### CPU
Spin loops eating CPU. Tests:
- Pod resource limits enforced
- Other tenants unaffected
- Auto-scaling response

```yaml
spec:
  mode: one
  selector: { ... }
  stressors:
    cpu:
      workers: 4
      load: 80
```

### Memory
Allocate until OOM. Tests:
- OOM killer behavior
- Pod restart policy
- Other pods on node unaffected (with proper limits)

```yaml
  stressors:
    memory:
      workers: 1
      size: 1GB
```

## Disk I/O

### Latency
Slow down disk operations. Tests:
- Database under stress
- App handling slow writes

### Saturation
Fill disk with writes. Tests:
- Disk full handling
- Cleanup mechanisms
- Eviction strategies

### Read Errors
Inject read errors. Tests:
- Retry on transient errors
- Failover to replicas

## Pod / Node Kills

### Pod Kill
Kill random pods. Tests:
- ReplicaSet replacement
- Service endpoints update
- In-flight request handling (graceful shutdown)

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
spec:
  action: pod-kill
  mode: one
  selector:
    labelSelectors:
      app: my-app
```

### Node Kill / Drain
Drain a node. Tests:
- PDB respect
- Pod rescheduling
- Workload disruption budget

### Container Kill (not pod)
Kill specific container in a pod (keeps pod). Tests:
- Init/sidecar restart
- Probe handling

## Region Failover

### Simulate AZ Failure
- Stop all instances in one AZ
- Tests: Multi-AZ HA, surviving AZs absorb load

### Simulate Region Failure
- Route 53 health checks fail
- DNS routes to secondary region
- Tests: cross-region replication, app warmup

### AWS FIS region experiment template
```json
{
  "actions": {
    "stop-az-instances": {
      "actionId": "aws:ec2:stop-instances",
      "targets": { "Instances": "az-a-instances" }
    }
  },
  "targets": {
    "az-a-instances": {
      "resourceType": "aws:ec2:instance",
      "filters": [
        { "path": "Placement.AvailabilityZone", "values": ["us-east-1a"] }
      ],
      "selectionMode": "ALL"
    }
  }
}
```

## DNS Failures

Inject:
- Slow DNS resolution
- NXDOMAIN responses
- Random IP responses

Tests:
- DNS retry behavior
- Caching policy
- Failover

## Time Skew

Skew clocks:
- Forward 1 hour
- Backward 30 seconds

Tests:
- TLS cert validation
- TOTP / OTP systems
- Time-based locks
- Distributed systems sensitive to clock

## HTTP Chaos

### Inject 500s
Random 5% of requests return 500. Tests:
- Retry logic
- Circuit breaker tripping
- User-facing error handling

### Slow Responses
Drip-feed responses. Tests:
- Timeout enforcement
- Connection pool depletion

## Dependency Outage

### Database Down
Take down DB primary. Tests:
- Failover time
- App reconnection
- Stale connection cleanup

### Cache Down
Stop Redis. Tests:
- Fallback to DB
- DB overload from miss storm
- Graceful degradation

## State-Recovery Experiments

### Snapshot Restore
Periodically restore a backup to a sandbox; verify integrity.

### Disaster Recovery Drill
- Force failover to DR region
- Verify capabilities
- Measure RTO

## What to Always Verify After Experiment

- Service recovered to baseline?
- Any unintended damage?
- Alerts fired correctly?
- On-call could resolve unaided?
- Customers impacted? (Measure with synthetic + real metrics)
- Action items identified?

## Pre-Experiment Checklist

- [ ] On-call notified
- [ ] War room open
- [ ] Steady-state baseline captured
- [ ] Stop conditions configured
- [ ] Rollback plan
- [ ] Customer-facing comms templates ready
- [ ] Off-peak hours
- [ ] Recent backup verified

## Interview Themes

- "Design a chaos experiment for X scenario"
- "What's the abort criteria?"
- "Network latency experiment — what to watch?"
- "Region failover drill — process"
- "Clock skew chaos — what it tests"
