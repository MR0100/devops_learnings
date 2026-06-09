# L08/C03/T02 — AMIs, Launch Templates, Auto Scaling Groups

## Learning Objectives

- Build AMIs reliably
- Use ASGs for self-healing fleets

## AMI

Amazon Machine Image: snapshot of OS + apps. Boot EC2 from it.

Types:
- AWS-owned (Amazon Linux, Ubuntu, etc.)
- Marketplace (vendor offerings)
- Custom (yours, built with Packer/etc.)

## Why Custom AMIs

Avoid per-boot install:
- Faster launch (everything pre-installed)
- Deterministic (golden image)
- Less external dependency at boot
- Validated build (CI tested)

Pattern: build AMI in CI → reference in ASG → roll out new AMIs as deploys.

## Packer

HashiCorp tool to build AMIs.

```hcl
source "amazon-ebs" "linux" {
  region       = "us-east-1"
  instance_type = "t3.micro"
  source_ami   = "ami-xxxxx"   # base AMI
  ssh_username = "ec2-user"
  ami_name     = "my-app-{{timestamp}}"
}

build {
  sources = ["source.amazon-ebs.linux"]
  
  provisioner "shell" {
    inline = [
      "sudo yum update -y",
      "sudo yum install -y nginx",
      "sudo systemctl enable nginx"
    ]
  }
}
```

```bash
packer build template.pkr.hcl
```

Produces new AMI ID.

## Launch Template

Reusable instance config:
- AMI ID
- Instance type
- Key pair
- Security groups
- User data
- IAM instance profile
- Block device mapping
- Tags

```bash
aws ec2 create-launch-template \
  --launch-template-name my-app \
  --launch-template-data '{
    "ImageId": "ami-xxx",
    "InstanceType": "m6i.large",
    "IamInstanceProfile": {"Name": "my-profile"},
    ...
  }'
```

Versioned: launch-template v1, v2, v3.

ASG references launch template + version.

## Auto Scaling Group (ASG)

Manages fleet:
- Min, max, desired count
- Across AZs (HA)
- Health checks (EC2 or ALB)
- Replaces unhealthy
- Scaling policies

```bash
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name my-asg \
  --launch-template "LaunchTemplateId=lt-xxx,Version=1" \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 3 \
  --vpc-zone-identifier "subnet-a,subnet-b,subnet-c" \
  --target-group-arns arn:aws:elasticloadbalancing:...
```

## Health Checks

### EC2 Health
Instance status (default). Replaces if hardware/network fails.

### ELB Health
Use target group health check. Replaces if app fails (port not responding).

Recommended: ELB.

### Grace Period
After launch: how long before health checks count. Typically 300s (boot time).

## Scaling Policies

### Target Tracking
"Keep average CPU at 50%":
```json
{
  "TargetValue": 50.0,
  "PredefinedMetricSpecification": {
    "PredefinedMetricType": "ASGAverageCPUUtilization"
  }
}
```

ASG auto-calculates scale up/down.

### Step Scaling
```
CPU 60-70% → +1
CPU 70-80% → +2
CPU 80%+ → +4
```

### Simple Scaling
Single threshold. Less control.

### Scheduled
"At 9 AM Mon-Fri, scale to 10. At 6 PM, scale to 2."

### Predictive
ML predicts load; pre-warms before known peaks.

## Cooldown

After scale event, wait period before next. Prevents flapping.

Default 300s.

## Lifecycle Hooks

Pause during launch / terminate for custom actions:
- Launching → run setup → continue
- Terminating → run cleanup → continue

For: deregister from external system, drain connections.

## Termination Policy

When scaling in, pick which to kill:
- Default (oldest launch config first)
- OldestInstance
- NewestInstance
- ClosestToNextInstanceHour (cost)
- AllocationStrategy

For mixed fleets: ASG picks intelligently.

## Mixed Instances Policy

ASG with multiple instance types + on-demand + spot:
```json
{
  "MixedInstancesPolicy": {
    "LaunchTemplate": {...},
    "InstancesDistribution": {
      "OnDemandPercentageAboveBaseCapacity": 25,
      "SpotAllocationStrategy": "capacity-optimized"
    },
    "Overrides": [
      {"InstanceType": "m6i.large"},
      {"InstanceType": "m6a.large"},
      {"InstanceType": "m7g.large"}
    ]
  }
}
```

Baseline: on-demand. Surge: spot. ASG diversifies.

## Suspend / Resume

```bash
aws autoscaling suspend-processes --auto-scaling-group-name my-asg --scaling-processes ReplaceUnhealthy
```

Useful during maintenance.

## Rolling Deploy

Update launch template; tell ASG to replace instances gradually.

CodeDeploy or:
```bash
aws autoscaling start-instance-refresh --auto-scaling-group-name my-asg
```

Replaces instances per `MinHealthyPercentage` setting.

## ASG + CloudFormation

```yaml
Resources:
  MyASG:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      LaunchTemplate:
        LaunchTemplateId: !Ref MyLT
        Version: !GetAtt MyLT.LatestVersionNumber
      MinSize: 2
      MaxSize: 10
      DesiredCapacity: 3
      TargetGroupARNs: [!Ref MyTG]
      VPCZoneIdentifier: [...]
    UpdatePolicy:
      AutoScalingRollingUpdate:
        MinInstancesInService: 1
        MaxBatchSize: 1
```

## Instance Refresh

Replace running instances with new AMI:
```bash
aws autoscaling start-instance-refresh \
  --auto-scaling-group-name my-asg \
  --strategy Rolling \
  --preferences MinHealthyPercentage=50
```

50% healthy at all times; gradual swap.

## Spot in ASG

```json
"SpotAllocationStrategy": "price-capacity-optimized"
```

ASG picks Spot pools likely to last (mix of capacity + price).

If interrupted: 2-min warning; ASG launches replacement.

## ASG Cost

ASG itself free. Charges for underlying EC2.

## ASG vs EC2 Fleet

EC2 Fleet: spot + on-demand mix without ASG abstraction. More flexible; less self-healing.

For most: ASG. Fleet for special cases.

## Cattle vs Pets

ASG = cattle approach:
- Numbered
- Replaceable
- No state on disk (or external state)
- Bootstrap via user data / AMI

Pet approach (named, hand-managed) doesn't scale.

## Common Mistakes

- ASG min 0 (everyone gone; manual fix needed)
- No ELB health check
- Per-instance state on local disk
- Long-running stateful instances in ASG (drift)
- Manual changes (replaced on next deploy)

## Best Practices

- ASG across 3+ AZs
- Target tracking with CPU 50-70%
- Instance refresh for AMI updates
- Mixed instances for cost
- Logs/metrics external
- Bootstrap via AMI (not boot-time install)

## Monitoring

CloudWatch ASG metrics:
- GroupDesiredCapacity
- GroupInServiceInstances
- GroupTotalInstances
- GroupPendingInstances

Alert if pending/terminating high (something wrong).

## Quick Refs

```bash
# Describe
aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names my-asg

# Scale
aws autoscaling set-desired-capacity --auto-scaling-group-name my-asg --desired-capacity 5

# Update instance refresh
aws autoscaling start-instance-refresh --auto-scaling-group-name my-asg
```

## Interview Prep

**Junior**: "Why ASG?"

**Mid**: "ASG with mixed Spot."

**Senior**: "Rolling deploy via instance refresh."

**Staff**: "ASG vs K8s for stateless service."

## Next Topic

→ [T03 — Placement Groups](T03-Placement-Groups.md)
