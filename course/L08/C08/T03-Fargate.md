# L08/C08/T03 — Fargate Pricing & Limits

## Learning Objectives

- Calculate Fargate cost
- Know limits

## Fargate

Serverless container compute. Works with ECS or EKS.

You: container image, CPU + RAM, network config.
AWS: host, OS, patching, scaling.

## Pricing

Per second:
- $0.04048 per vCPU-hour
- $0.004445 per GB-hour

Plus storage:
- 20 GB ephemeral free
- $0.000111/GB-hour beyond

Plus data transfer (egress) as usual.

## Example

1 vCPU + 2 GB, 24/7:
- vCPU: 1 × $0.04048 × 24 × 30 = $29
- RAM: 2 × $0.004445 × 24 × 30 = $6.40
- Total: $35.40/mo per task

For 10 tasks: $354/mo.

## Fargate Spot

50-70% off:
- $0.012 per vCPU-hour
- $0.001332 per GB-hour

Subject to interruption (2-min warning).

For: batch, dev/test, tolerant workloads.

## Compute Savings Plan

Compute SP applies to Fargate:
- 1-yr SP: 30% off
- 3-yr SP: 50% off

Stack with Spot (no, Spot is separate pricing).

## Fargate vs EC2

vCPU comparison:
- Fargate: $0.04048/hour
- EC2 (m6i.large = 2 vCPU): $0.0464/hour = $0.0232/vCPU/hour

EC2 ~40% cheaper per vCPU. But you manage nodes.

Tradeoff: ops time vs cost.

For small fleet: Fargate wins (ops > cost).
For large steady: EC2 wins (cost > ops).

## CPU + RAM Combinations

Fixed combos (not arbitrary):
- 0.25 vCPU: 0.5, 1, 2 GB
- 0.5 vCPU: 1-4 GB
- 1 vCPU: 2-8 GB
- 2 vCPU: 4-16 GB
- 4 vCPU: 8-30 GB
- 8 vCPU: 16-60 GB
- 16 vCPU: 32-120 GB

Pick combo; pay for both.

## Storage

20 GB ephemeral free.

Up to 200 GB:
- $0.000111/GB-hour
- 100 GB extra × $0.000111 × 24 × 30 = $8/mo per task

For more / persistent: EFS volume mount (EFS pricing).

## Limits

| | Limit |
|---|---|
| CPU | 16 vCPU |
| Memory | 120 GB |
| Storage | 200 GB ephemeral |
| Network | 100 Gbps (large tasks) |
| GPU | Yes (limited; specific configs) |

For >: use EC2.

## Networking

awsvpc mode: each task has ENI in your VPC.
- Task gets IP from subnet
- SG per task
- Subject to ENI per-instance limit (Fargate manages)

Public IP optional (Fargate Task → assignPublicIp).

## ENI Costs

Each task = 1 ENI. For 1000 tasks: 1000 ENIs in subnet. Plan CIDR.

## Cold Start

Task launch: ~30s typically.
- Pull image (depends on size)
- Mount ENI
- Container start

For latency-critical: pre-warm (constant tasks) or use Lambda.

## Image Pull

From ECR: fast (regional, AWS network).
From Docker Hub: slower; rate limits possible.

Optimize:
- ECR
- Smaller images (multi-stage; minimal base)
- Cached layers (Fargate caches sometimes)

## Logging

CloudWatch Logs (awslogs driver):
```json
"logConfiguration": {
  "logDriver": "awslogs",
  "options": {
    "awslogs-group": "/ecs/myapp",
    "awslogs-region": "us-east-1",
    "awslogs-stream-prefix": "web"
  }
}
```

Or splunk, syslog, firelens.

CloudWatch ingestion cost: $0.50/GB. For high-log apps: consider Firelens → S3.

## Health Check

Container health:
```json
"healthCheck": {
  "command": ["CMD-SHELL", "curl -f http://localhost:8080/health"],
  "interval": 30,
  "timeout": 5,
  "retries": 3
}
```

Failures → task killed.

## Auto-Scaling

For ECS Service on Fargate:
- Target CPU
- Target memory
- ALB request count per target
- Custom CloudWatch metric

```bash
aws application-autoscaling register-scalable-target ...
aws application-autoscaling put-scaling-policy ...
```

## Fargate vs Lambda

For long-running:
- Lambda: 15 min max
- Fargate: unlimited

For request:
- Lambda: cold start; auto-scale
- Fargate: longer cold; runs continuously

For batch:
- Lambda for short
- Fargate / Batch for long

Cost comparison:
- 1 GB function 24/7:
  - Lambda: $216/mo (always on; impossible; only for high-traffic)
  - Fargate 0.25 vCPU + 1 GB: ~$15/mo

For sporadic: Lambda. Steady: Fargate.

## When NOT Fargate

- Need DaemonSet pattern (EC2 needed)
- Privileged containers
- Host networking
- Big data with local SSD
- GPU at large scale
- Massive RAM (>120 GB)
- Cost-sensitive steady (EC2 with RIs cheaper)

## Best Practices

- Right-size (don't over-provision)
- Fargate Spot for tolerant
- CSP for steady production
- ECR images
- Health check + auto-scaling
- Container Insights

## Calculation Tool

AWS Fargate calculator: pricing.aws/calculator.

## Patterns

### Sporadic API
- Min 1 always-on Fargate task
- Auto-scale on traffic

### Batch (Daily)
- One-shot Fargate task (EventBridge schedule)
- Or AWS Batch on Fargate

### Worker Pool
- Auto-scale on SQS depth
- Fargate Spot

### Periodic Cron
- Lambda if < 15 min
- Fargate scheduled task if longer

## Common Mistakes

- 4 vCPU when 1 enough (4× cost)
- Too much RAM (paying for unused)
- All on-demand when Spot OK
- Forgetting log cost
- Not using SP

## Cost Optimization

- Right-size monthly review
- Spot for ~70% off (where appropriate)
- 1-yr or 3-yr SP for steady
- Smaller container = faster start (less data transfer)
- ECR over Docker Hub
- Shut off non-prod outside hours

## Quick Refs

```bash
# Task def with Fargate
aws ecs register-task-definition --family myapp \
  --requires-compatibilities FARGATE \
  --network-mode awsvpc \
  --cpu 256 --memory 512 \
  --execution-role-arn arn:... \
  --container-definitions ...

# Service
aws ecs create-service --cluster mycluster --service-name web --task-definition myapp:1 \
  --desired-count 3 --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[...],securityGroups=[...]}"
```

## Interview Prep

**Mid**: "Fargate vs EC2 launch."

**Senior**: "Fargate cost optimization."

**Staff**: "When NOT Fargate."

## Next Topic

→ [T04 — ECR (Image Scanning, Replication)](T04-ECR.md)
