# L25/C02/T05 — AWS Fault Injection Simulator (FIS)

## Learning Objectives

- Use AWS FIS
- Native chaos

## FIS

AWS-native chaos:
- EC2 stop/reboot/terminate
- ECS task stop
- EKS pod
- RDS failover
- API throttle
- Network blackhole

## Setup

```bash
aws fis create-experiment-template \
  --description "Stop EC2 instances" \
  --targets '...' \
  --actions '...' \
  --role-arn arn:aws:iam::ACCT:role/FIS-role
```

## Template

```json
{
  "targets": {
    "instances": {
      "resourceType": "aws:ec2:instance",
      "resourceTags": { "env": "chaos" },
      "selectionMode": "COUNT(1)"
    }
  },
  "actions": {
    "stop-instances": {
      "actionId": "aws:ec2:stop-instances",
      "targets": { "Instances": "instances" }
    }
  }
}
```

## Run

```bash
aws fis start-experiment --experiment-template-id ...
```

## Stop Conditions

```json
"stopConditions": [
  {
    "source": "aws:cloudwatch:alarm",
    "value": "arn:aws:cloudwatch:..."
  }
]
```

Auto-abort if alarm.

## Action Types

- aws:ec2:stop-instances / reboot / terminate
- aws:ecs:stop-task
- aws:eks:terminate-nodegroup-instances
- aws:rds:reboot-db-instances / failover-db-cluster
- aws:fis:wait
- aws:fis:inject-api-internal-error

## IAM

Role with permissions to:
- Take actions
- Read CloudWatch alarms

## Pros

- AWS-native
- Pay-per-use
- Audit (CloudTrail)
- Integrated alarms

## Cons

- AWS-only
- Limited K8s deep

## When FIS

- AWS-heavy
- Want native
- Simple infrastructure chaos

## When OSS

- K8s deep chaos
- Multi-cloud
- Custom

## Best Practices

- Stop conditions on
- Tags for targeting
- Audit logs
- Pre-prod test

## Quick Refs

```bash
aws fis create-experiment-template
aws fis start-experiment
aws fis stop-experiment
aws fis list-experiment-templates
```

## Interview Prep

**Mid**: "What's FIS."

**Senior**: "AWS chaos."

## Next Topic

→ Move to [L25/C03 — Common Experiments](../C03/README.md)
