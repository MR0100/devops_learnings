# L08/C08/T01 — ECS (EC2 vs Fargate)

## Learning Objectives

- Use ECS effectively
- Pick launch type

## ECS

AWS's container orchestrator. Simpler than K8s.

Concepts:
- **Cluster**: logical grouping
- **Task Definition**: container spec (image, CPU, RAM, IAM, env)
- **Task**: running instance
- **Service**: keeps N tasks running; integrates with LB

## Launch Types

### EC2
You manage EC2 nodes; ECS schedules tasks.

Pros:
- Cheaper for steady workloads
- More instance type variety
- Can use Spot

Cons:
- Manage AMI / patching
- Scale node count yourself (or via ASG)

### Fargate
AWS manages compute; you specify CPU + RAM per task.

Pros:
- No node management
- Better security (isolated)
- Per-task billing

Cons:
- More expensive per vCPU
- Some networking limits
- Slower start (~30s)

Default for new: Fargate.

## Task Definition

```json
{
  "family": "myapp",
  "containerDefinitions": [{
    "name": "web",
    "image": "123.dkr.ecr.us-east-1.amazonaws.com/myapp:v1",
    "memory": 512,
    "cpu": 256,
    "essential": true,
    "portMappings": [{"containerPort": 8080, "hostPort": 8080}],
    "environment": [
      {"name": "ENV", "value": "prod"}
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/ecs/myapp",
        "awslogs-region": "us-east-1",
        "awslogs-stream-prefix": "web"
      }
    }
  }],
  "executionRoleArn": "arn:...",      # role for task setup (ECR pull, log)
  "taskRoleArn": "arn:...",            # role for task at runtime (S3 access)
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"]
}
```

## Task vs Container

A task can have 1+ containers (sidecar pattern).

Co-located:
- Same host (EC2) or same Fargate task
- Share network
- One task = one ENI (awsvpc mode)

## Network Modes

- **awsvpc**: each task gets ENI (Fargate requires)
- **bridge**: shared docker bridge (EC2 only)
- **host**: use host network (EC2)
- **none**: no networking

awsvpc preferred; clean SG per task.

## Service

Keeps N tasks running:
```bash
aws ecs create-service \
  --cluster mycluster \
  --service-name web \
  --task-definition myapp:1 \
  --desired-count 3 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[...],securityGroups=[...]}" \
  --load-balancers "targetGroupArn=arn:...,containerName=web,containerPort=8080"
```

Service:
- Maintains desired count (replaces failed)
- LB integration (registers/deregisters tasks)
- Deployment (rolling update)
- Auto-scaling

## Service Auto Scaling

Target tracking:
- CPU utilization
- Request count per target (LB)
- Custom CloudWatch metric

```bash
aws application-autoscaling register-scalable-target ...
aws application-autoscaling put-scaling-policy --policy-type TargetTrackingScaling ...
```

## Deployments

Rolling (default):
- N% new tasks deployed
- Health check passes
- Drain old

Configurable:
- `MinimumHealthyPercent`: 100% (no downtime)
- `MaximumPercent`: 200% (extra during deploy)

For 6 tasks, MinHealthy=100, Max=200: 6 new + 6 old briefly; old drain.

## Blue/Green (CodeDeploy)

Switch traffic between two task sets:
- Blue: current
- Green: new
- Test green; cut traffic
- Rollback fast

For: critical services; sensitive deploys.

## Container Insights

Detailed metrics for ECS:
```bash
aws ecs put-account-setting --name containerInsights --value enabled
```

Cost: small. Worth enabling for prod.

## Auto-Scaling Cluster (EC2)

For EC2 launch:
- ASG for EC2 nodes
- ECS Capacity Provider scales ASG based on task demand
- Spot mixed (if configured)

For Fargate: AWS scales; no nodes to manage.

## ECS Exec

SSH-like into running task:
```bash
aws ecs execute-command --cluster mycluster --task task-id --container web --command "/bin/bash" --interactive
```

For debugging. Requires task config + SSM agent in task.

## Service Discovery

ECS Service Discovery: integrates with Cloud Map.

Tasks register with name; other services resolve via DNS:
```
web.mycluster.local → IPs of web tasks
```

For: internal microservices without LB.

## Tasks Running (Spot for EC2)

ECS Capacity Provider with Spot mix saves money.

```yaml
CapacityProviders: [SPOT_CAPACITY_PROVIDER, ON_DEMAND_CAPACITY_PROVIDER]
DefaultCapacityProviderStrategy:
  - capacityProvider: SPOT_CAPACITY_PROVIDER
    weight: 4
  - capacityProvider: ON_DEMAND_CAPACITY_PROVIDER
    weight: 1
```

## Fargate Pricing

Per vCPU-hour + GB-hour:
- 0.25 vCPU + 0.5 GB: ~$10/mo per task 24/7
- 1 vCPU + 2 GB: ~$36/mo
- 4 vCPU + 8 GB: ~$144/mo

Plus Fargate Spot (50-70% off, can be interrupted).

vs EC2: Fargate ~20% more expensive per vCPU but no node mgmt.

## Fargate Limits

- 4 vCPU max (16 vCPU with arm64 or specific configs; up to 16 on newer)
- 30 GB max RAM
- 200 GB ephemeral storage

For >these: EC2 with bigger instance.

## ECS vs EKS

| | ECS | EKS |
|---|---|---|
| Complexity | Simpler | More |
| Lock-in | AWS | K8s portable |
| Community | Smaller | Huge |
| Features | Less | More |
| Cost | Control plane free | $73/mo + nodes |

If AWS-only & simple: ECS. If K8s skills / multi-cloud: EKS.

## App Mesh

Service mesh integration. mTLS, traffic management, observability.

For: many microservices.

(Covered separately.)

## Common Patterns

### Stateless Web Service
- Fargate
- ALB → tasks
- Auto-scaling on CPU / request count
- Container Insights

### Worker (Queue Consumer)
- SQS → tasks polling
- Auto-scaling on queue depth (custom metric)

### Scheduled Task
- EventBridge schedule → ECS RunTask
- Don't need service (one-shot)

### Migration from VMs
- Containerize app
- ECS Fargate as VM replacement
- Easier than full K8s

## IAM

- **Task Execution Role**: setup tasks (pull image, send logs)
- **Task Role**: assumed by task at runtime (your app uses)

Separate concerns.

## Networking

awsvpc mode:
- Each task ENI in VPC
- Task IP from subnet
- SG per task / service
- For 1000 tasks: 1000 IPs in subnet

Plan subnet CIDR.

## Health Checks

Container health:
```yaml
healthCheck:
  command: ["CMD-SHELL", "curl -f http://localhost:8080/health"]
  interval: 30
  timeout: 5
  retries: 3
  startPeriod: 60
```

Task unhealthy → ECS stops/restarts.

ALB health check (separate): determines if task registers with LB.

## Common Mistakes

- EC2 launch when Fargate fits (extra ops work)
- No health check
- All-or-nothing deployment (no rolling config)
- Big Fargate task (limit hit; underutilized)
- Logs to file (use awslogs)

## Best Practices

- Fargate default for new
- Health checks (container + LB)
- Auto-scaling
- Container Insights
- Task role minimal
- Logs to CloudWatch
- ECR with scanning
- Spot for non-critical

## ECR

Container registry. Per-region:
```bash
aws ecr create-repository --repository-name myapp
docker login ...
docker push 123.dkr.ecr.us-east-1.amazonaws.com/myapp:v1
```

Image scanning (free basic):
- Vulnerabilities reported
- Block insecure deploys (policy)

Lifecycle:
- Keep last 10 versions
- Delete older
- Cost optimization

## ECS Anywhere

Run ECS on your hardware (on-prem). Control plane in AWS; data plane local.

For: hybrid; gradual cloud migration.

## Quick Refs

```bash
# Create cluster
aws ecs create-cluster --cluster-name mycluster

# Register task def
aws ecs register-task-definition --cli-input-json file://taskdef.json

# Create service
aws ecs create-service --cluster mycluster --service-name web --task-definition myapp:1 --desired-count 3 --launch-type FARGATE ...

# Update (rolling deploy)
aws ecs update-service --cluster mycluster --service web --task-definition myapp:2
```

## Interview Prep

**Mid**: "ECS Fargate vs EC2."

**Senior**: "ECS service deployment patterns."

**Staff**: "Migrate 50 services from VMs to ECS."

## Next Topic

→ [T02 — EKS Architecture & Control Plane](T02-EKS.md)
