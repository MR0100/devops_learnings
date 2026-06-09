# L25/C02 — Chaos Engineering Tools

## Topics

- **T01 Chaos Monkey** — The original
- **T02 Chaos Mesh** — K8s-native, CNCF
- **T03 Litmus** — K8s, marketplace
- **T04 Gremlin** — Commercial, mature
- **T05 AWS Fault Injection Simulator** — AWS-native

## Chaos Monkey (Netflix)

The original. Started 2010.
- Randomly kills EC2 instances during business hours
- Forces engineers to design for failure
- Inspired entire ecosystem

Today: largely subsumed by broader Chaos Engineering tools.

## Chaos Mesh

CNCF graduated. K8s-native via CRDs.

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: api-latency
spec:
  action: delay
  mode: all
  selector:
    namespaces: [api]
    labelSelectors:
      app: my-app
  delay:
    latency: "500ms"
    jitter: "50ms"
    correlation: "25"
  duration: "5m"
```

### Chaos Types
- NetworkChaos (delay, loss, partition, corrupt, duplicate)
- PodChaos (kill, failure)
- StressChaos (CPU, memory)
- IOChaos (latency, fault, mistake)
- DNSChaos
- TimeChaos (clock skew)
- KernelChaos (panic, etc.)
- HTTPChaos (modify requests/responses)

### Workflow
Chain experiments:
```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: Workflow
spec:
  entry: parallel-1
  templates:
    - name: parallel-1
      templateType: Parallel
      children: [network-delay, pod-failure]
    - name: network-delay
      templateType: NetworkChaos
      ...
```

## Litmus

CNCF. Marketplace approach with "ChaosHub" sharing experiments.

```yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: pod-delete-engine
spec:
  appinfo:
    appns: default
    applabel: 'app=my-app'
    appkind: 'deployment'
  experiments:
    - name: pod-delete
      spec:
        components:
          env:
            - name: TOTAL_CHAOS_DURATION
              value: '60'
            - name: CHAOS_INTERVAL
              value: '20'
```

### ChaosHub
Reusable experiments from community. Open source extension model.

## Gremlin (Commercial)

Polished UI, multi-platform (K8s, Linux, Windows, AWS, GCP, Azure).

### Features
- Library of pre-built attacks
- Magnitude control
- Scheduled experiments
- Compliance reporting
- Multi-cloud

### Why Commercial
- Strong UI (less YAML)
- Pre-vetted attack library
- Less ops overhead
- Compliance documentation

## AWS Fault Injection Simulator (FIS)

AWS-native. CloudFormation-style templates.

```yaml
# FIS Experiment Template
{
  "actions": {
    "stop-instances": {
      "actionId": "aws:ec2:stop-instances",
      "parameters": { "startInstancesAfterDuration": "PT10M" },
      "targets": { "Instances": "asg-targets" }
    },
    "inject-latency": {
      "actionId": "aws:network:disrupt-connectivity",
      "parameters": { "duration": "PT5M" },
      "targets": { "Subnets": "private-subnets" }
    }
  },
  "targets": {
    "asg-targets": {
      "resourceType": "aws:ec2:instance",
      "filters": [{ "path": "Tags.AutoScalingGroupName", "values": ["my-asg"] }],
      "selectionMode": "PERCENT(10)"
    }
  },
  "stopConditions": [
    { "source": "aws:cloudwatch:alarm", "value": "arn:aws:cloudwatch:...:alarm/error-rate" }
  ]
}
```

### Why FIS
- AWS-native (works with FIS-enabled services natively)
- Stop conditions tied to CloudWatch alarms
- Auditable via CloudTrail
- No agent needed

### Supported Actions
- EC2 stop, terminate, reboot
- ECS / EKS task failure
- RDS reboot, failover
- Networking (subnet disrupt)
- SSM agent commands for in-instance chaos (latency, CPU, etc.)

## Choosing

| Need | Pick |
|---|---|
| K8s-only, OSS | Chaos Mesh or Litmus |
| Multi-platform, commercial UI | Gremlin |
| AWS-deep | FIS |
| Network-specific | Toxiproxy or Chaos Mesh NetworkChaos |
| Custom DSL | LinkedIn's Cleric, or roll your own |

## Other Tools

- **Toxiproxy** (Shopify) — proxy that injects network failures
- **Pumba** — Docker container chaos
- **Chaos Toolkit** — extensible Python framework
- **PowerfulSeal** — K8s, OSS
- **Steadybit** — commercial

## Operations

### Permissions
Chaos tools need permissions:
- Kill pods, instances
- Manipulate IAM, network
- Use granular IAM; audit log

### Communication
Before any prod experiment: notify on-call. Even better: dedicated war room.

### Aborts
Always have:
- Kill switch (stop experiment immediately)
- Stop conditions (auto-abort on bad signal)
- Manual override

### Schedule
- Off-peak preferred
- Avoid known peak periods
- Coordinate with deploys (don't run during a deploy)

## Interview Themes

- "Compare Chaos Mesh, Litmus, Gremlin, FIS"
- "AWS FIS — what does it offer?"
- "K8s-native chaos — which tool?"
- "Toxiproxy — what does it do?"
- "Safety mechanisms in chaos tools"
