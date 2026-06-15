# L25/C02/T05 — AWS Fault Injection Simulator (FIS)

## Learning Objectives

- Build and run an FIS experiment template with targets and actions
- Wire CloudWatch-alarm stop conditions for automatic abort
- Decide when FIS is the right tool versus OSS chaos platforms

## FIS

AWS Fault Injection Service (formerly Simulator) is AWS-native, managed chaos.
You describe an experiment as a **template** (targets + actions + stop
conditions), AWS executes it against your resources, and every step is audited
in CloudTrail. The headline feature is **stop conditions** bound to CloudWatch
alarms: if your SLO breaches mid-experiment, FIS halts and rolls back
automatically — the safety rail is built into the platform.

Native faults span:

- EC2 stop / reboot / terminate
- ECS task stop, EKS node-group instance termination
- RDS reboot / Aurora cluster failover
- Network: latency, packet loss, blackhole (via SSM on instances)
- API: throttling and injected internal errors for select services

## Experiment Template Anatomy

An FIS template is JSON/HCL with four parts: **targets** (what), **actions**
(do what, in what order), **stopConditions** (when to abort), and a **roleArn**
(permission to act).

```bash
aws fis create-experiment-template --cli-input-json file://template.json
```

```json
{
  "description": "Stop one tagged EC2 instance, abort on SLO breach",
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
      "parameters": { "startInstancesAfterDuration": "PT5M" },
      "targets": { "Instances": "instances" }
    }
  },
  "stopConditions": [
    { "source": "aws:cloudwatch:alarm",
      "value": "arn:aws:cloudwatch:us-east-1:ACCT:alarm:HighErrorRate" }
  ],
  "roleArn": "arn:aws:iam::ACCT:role/FIS-role"
}
```

`selectionMode: COUNT(1)` is the blast-radius control — target one instance,
not the whole tagged fleet. `startInstancesAfterDuration` makes the fault
self-reverting: the instance comes back after 5 minutes even if nobody acts.

## Targeting

Targets are selected by resource type plus filters/tags, then narrowed by
`selectionMode`:

- `COUNT(n)` — exactly n resources
- `PERCENT(n)` — n% of matching resources
- `ALL` — everything matching (rarely the right first choice)

Tag-based selection (`resourceTags`) is the safe default: you opt resources in
to chaos with a tag (`env: chaos`) rather than risk matching production
broadly.

## Stop Conditions (the safety rail)

```json
"stopConditions": [
  { "source": "aws:cloudwatch:alarm",
    "value": "arn:aws:cloudwatch:...:alarm:p99-latency" }
]
```

If any referenced alarm enters `ALARM` state while the experiment runs, FIS
**stops the experiment and reverses its actions**. This is the difference
between FIS and rolling your own: the abort is automatic, tied to your real
SLO, and doesn't depend on a human watching a dashboard. An experiment with no
stop condition is running without a seatbelt.

## Running and Stopping

```bash
aws fis start-experiment --experiment-template-id EXT-xxxx \
  --tags Name=chaos-run-2026-06
aws fis stop-experiment  --id EXP-xxxx     # manual abort
aws fis get-experiment   --id EXP-xxxx     # state + per-action status
```

## Action Catalog (common)

- `aws:ec2:stop-instances` / `reboot-instances` / `terminate-instances`
- `aws:ecs:stop-task`
- `aws:eks:terminate-nodegroup-instances`
- `aws:rds:reboot-db-instances` / `aws:rds:failover-db-cluster`
- `aws:ssm:send-command` — run network/IO faults *inside* instances via SSM
- `aws:fis:inject-api-internal-error` / `inject-api-throttle-error`
- `aws:fis:wait` — sequence/pause between actions to model staged failures

Network and host-level faults (latency, packet loss, disk fill) run through the
**SSM agent** on the instance, so targets need SSM connectivity and the agent
installed — a frequent source of "the action did nothing."

## IAM

FIS assumes the `roleArn` to act. That role needs permissions to:

- Perform each action (e.g. `ec2:StopInstances`, `rds:FailoverDBCluster`)
- Read the CloudWatch alarms referenced in stop conditions
- Use SSM if the experiment includes SSM-based network/IO faults

Scope it tightly — this role can break production by design, so least privilege
and tag-condition guards matter.

## FIS vs OSS

| Dimension     | AWS FIS                          | Chaos Mesh / Litmus / Gremlin   |
|---------------|----------------------------------|---------------------------------|
| Scope         | AWS infra (EC2/ECS/EKS/RDS/API)  | Deep K8s / multi-platform       |
| Safety        | Built-in CloudWatch stop conditions | Roll your own (Gremlin built-in) |
| Audit         | First-class (CloudTrail)         | DIY                             |
| Cost          | Pay-per-action-minute            | Free OSS / paid Gremlin         |
| Lock-in       | AWS-only                         | Portable (OSS) / vendor (Gremlin) |

### Choose FIS when
- You're AWS-heavy and want infra-level faults (instance/AZ/RDS/API)
- You want native CloudWatch-driven auto-abort and CloudTrail audit
- You'd rather not run/maintain chaos tooling yourself

### Choose OSS when
- You need **deep Kubernetes** faults (pod/network/IO/kernel) — FIS is shallow there
- You're multi-cloud or need custom faults FIS doesn't offer
- You want experiments as portable, Git-versioned manifests

## Common Mistakes

- No stop condition → the experiment can't auto-abort on an SLO breach
- `selectionMode: ALL`/broad tags on the first run → blast radius far too wide
- Forgetting SSM agent/connectivity for network/IO actions → action silently no-ops
- An over-broad or under-privileged `roleArn` → unsafe blast radius or failed actions
- Running against untagged prod resources instead of an opted-in `env: chaos` set
- Reading results with no steady-state baseline or dashboards in place

## Best Practices

- Always attach a CloudWatch-alarm stop condition tied to a real SLO
- Target by tag with `COUNT(1)`/`PERCENT(small)`; widen only across runs
- Use self-reverting actions (`startInstancesAfterDuration`) and an `aws:fis:wait` for staged faults
- Keep the FIS role least-privilege with tag-condition guards; review it
- Ensure SSM is healthy on targets before host-level network/IO experiments
- Test templates in a non-prod account first; keep templates in source control

## Quick Refs

```bash
aws fis create-experiment-template --cli-input-json file://template.json
aws fis start-experiment --experiment-template-id EXT-xxxx
aws fis stop-experiment  --id EXP-xxxx        # manual abort
aws fis get-experiment   --id EXP-xxxx        # status
aws fis list-experiment-templates
# Template = targets + actions + stopConditions(CloudWatch alarm) + roleArn
# selectionMode: COUNT(n) | PERCENT(n) | ALL
```

## Interview Prep

**Junior**: "What is AWS FIS?" — AWS's managed chaos service. You define an experiment template (targets, actions, stop conditions), AWS injects the fault against your resources, and CloudTrail audits every step.

**Mid**: "How does FIS abort safely?" — Stop conditions reference CloudWatch alarms; if an alarm trips during the run, FIS automatically stops the experiment and reverses its actions, so the abort is tied to your real SLO rather than a human watching.

**Senior**: "FIS vs OSS chaos tools — trade-offs?" — FIS is AWS-native with built-in CloudWatch stop conditions and CloudTrail audit, ideal for infra-level faults (EC2/AZ/RDS/API), but shallow on deep Kubernetes chaos and AWS-locked. Chaos Mesh/Litmus give deep K8s faults and portable manifests but you build your own safety; Gremlin buys managed multi-platform safety at a cost.

**Staff**: "Design a region-failover drill with FIS." — Tag the target fleet `env: chaos`, build a staged template: blackhole/stop an AZ's instances with `COUNT`/`PERCENT` and `aws:fis:wait` between steps, optionally `aws:rds:failover-db-cluster`, bind stop conditions to p99-latency and error-rate alarms for auto-abort, run the FIS role least-privilege, validate in a non-prod account, then execute in a Game Day with dashboards and a tested manual `stop-experiment` fallback.

## Next Topic

→ Move to [L25/C03 — Common Experiments](../C03/README.md)
