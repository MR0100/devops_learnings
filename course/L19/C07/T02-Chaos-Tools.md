# L19/C07/T02 — Tools (Chaos Mesh, Litmus, Gremlin, AWS FIS)

## Learning Objectives

- Pick chaos tool
- Run injections

## Chaos Mesh

CNCF; K8s-native:
- CRDs for each chaos
- Many failure types
- UI

## Install

```bash
helm install chaos-mesh chaos-mesh/chaos-mesh --namespace chaos-testing --create-namespace
```

## Pod Kill

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: pod-kill-test
spec:
  action: pod-kill
  mode: one
  selector:
    namespaces: [prod]
    labelSelectors:
      app: my-app
  scheduler:
    cron: '@every 10m'
```

## Network Delay

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: network-delay
spec:
  action: delay
  mode: all
  selector:
    namespaces: [prod]
  delay:
    latency: '100ms'
    correlation: '50'
    jitter: '20ms'
  duration: '5m'
```

## CPU Stress

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: StressChaos
spec:
  mode: one
  selector:
    namespaces: [prod]
  stressors:
    cpu:
      workers: 2
      load: 90
  duration: '5m'
```

## Memory Stress

Memory leak simulation.

## Disk Pressure

Fill disk.

## DNS Failure

Inject DNS errors.

## Other

- Time skew (clock drift)
- HTTP fault (return errors)
- Kernel (block IO, etc.)

## Litmus

CNCF; chaos for K8s:
- Hub of experiments
- ChaosCenter UI
- ArgoCD integration

```bash
kubectl apply -f https://litmuschaos.github.io/litmus/...
```

Many experiments shareable.

## Gremlin

Commercial:
- SaaS UI
- Cloud + K8s
- Templates
- Curated experiments

For: managed; cheaper engineer time.

## AWS FIS

Fault Injection Service:
- AWS-native
- EC2 instance reboot
- ECS task stop
- RDS failover
- Network partition

```bash
aws fis create-experiment-template ...
aws fis start-experiment ...
```

For: AWS workloads.

## Azure Chaos Studio

Similar; Azure.

## Pumba

For Docker:
- Kill containers
- Network delay
- Pause

## Toxiproxy

Proxy with chaos:
- Latency
- Bandwidth limit
- Connections

For: app-level testing.

## Chaos Monkey (Spinnaker)

Original. Kills EC2 instances randomly.

For: Spinnaker users.

## Picking

| | Chaos Mesh | Litmus | Gremlin | FIS |
|---|---|---|---|---|
| Self-host | yes | yes | no | no |
| K8s | yes | yes | partial | partial |
| Cloud | no | no | yes | AWS only |
| Cost | OSS | OSS | $$$ | per-experiment |
| Maturity | high | high | high | growing |

## Workflow

```
1. Define experiment (CRD or UI)
2. Schedule or trigger
3. Run with observation
4. Auto-rollback if defined
5. Analyze
```

## Steady State Probe

Chaos Mesh / Litmus: probes during chaos.

If steady state violated: abort chaos.

For: safety.

## Game Day Tool

For ad-hoc:
- ChaosCenter (Litmus)
- Custom (kubectl chaos)

## CI Integration

```yaml
- name: Run chaos
  run: |
    kubectl apply -f chaos-test.yaml
    sleep 300
    kubectl get podchaos
    # Verify SLO held
```

For: pre-merge or pre-deploy.

## Best Practices

- Start with one tool
- K8s: Chaos Mesh or Litmus
- AWS: FIS
- Multi-cloud: Gremlin if budget
- Pre-prod first; prod gradually

## Common Mistakes

- All tools (complexity)
- Skip probe (no abort)
- Run blindly
- No postmortem

## Quick Refs

```bash
# Chaos Mesh
kubectl apply -f chaos.yaml

# Litmus
kubectl apply -f experiment.yaml

# FIS
aws fis start-experiment

# Gremlin
gremlin attack
```

## Interview Prep

**Mid**: "Chaos tools."

**Senior**: "Picking tool."

**Staff**: "Chaos at scale."

## Next Topic

→ [T03 — Game Days](T03-Game-Days.md)
