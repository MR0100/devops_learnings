# L25/C03/T04 — Pod / Node Kills

## Learning Objectives

- Test auto-replace
- Verify HA

## PodChaos

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
spec:
  action: pod-kill
  mode: one
  selector: ...
  scheduler:
    cron: '@every 10m'
```

## Actions

- pod-kill: delete
- pod-failure: pause (not running)
- container-kill: kill one container

## Tests

- K8s replaces?
- LB removes from rotation?
- Sessions handled?
- Customer impact?

## Node Kill

Drain or shutdown:
```bash
kubectl drain node-1 --ignore-daemonsets
```

Or chaos:
```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NodeChaos
spec:
  action: node-shutdown
```

## Tests

- Pods reschedule
- DaemonSet?
- Persistent volumes
- Time to reach steady

## AZ Kill

Simulate AZ failure:
- Drain all nodes in AZ
- Block traffic

Tests:
- Multi-AZ resilience
- Cross-AZ replication

## Region Kill

(See T05.)

## Best Practices

- Start with one pod
- Then node
- Then AZ
- Then region (rarely)

## Frequency

For continuous chaos:
- Pod kill: every 10 min
- Node kill: weekly

For: build muscle.

## Watching

- Service availability
- Recovery time
- Customer reports

## Common Mistakes

- Kill stateful without replication (data loss)
- Multiple kills (cascading)
- No PDB (PodDisruptionBudget)

## PDB

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: my-app
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: my-app
```

K8s respects:
- Chaos / drain blocked if would violate

For: protect availability.

## Quick Refs

```yaml
PodChaos:
  action: pod-kill / pod-failure / container-kill
  mode: one / all / fixed-percent

NodeChaos:
  action: node-shutdown / node-restart
```

## Interview Prep

**Mid**: "Pod chaos."

**Senior**: "Node chaos."

**Staff**: "AZ failure test."

## Next Topic

→ [T05 — Region Failover](T05-Region-Failover.md)
