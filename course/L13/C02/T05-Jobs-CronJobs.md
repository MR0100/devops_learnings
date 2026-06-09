# L13/C02/T05 — Jobs & CronJobs

## Learning Objectives

- Run batch tasks in K8s
- Schedule recurring jobs

## Job

Run pod(s) to completion:
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: import-data
spec:
  template:
    spec:
      restartPolicy: OnFailure
      containers:
      - name: import
        image: my-importer:v1
        command: ["python", "import.py"]
  backoffLimit: 4
```

For one-shot tasks: migration, batch processing, ad-hoc.

## restartPolicy

For Job pods:
- `OnFailure`: container restarts on non-zero exit
- `Never`: container doesn't restart; Job controller creates new pod

`Never` better for: detect failures, count retries.

## Completion

Default: 1 pod succeeds = Job complete.

```yaml
spec:
  completions: 5    # 5 pods must succeed
  parallelism: 2    # 2 at a time
```

For: batch process N items.

## Parallelism

```yaml
parallelism: 4
```

Up to 4 concurrent pods. Others wait or fill in as ones complete.

## Failure

```yaml
backoffLimit: 6
```

After 6 failed pods: Job marked Failed.

`activeDeadlineSeconds`: max total runtime (regardless of completions):
```yaml
activeDeadlineSeconds: 600
```

## Patterns

### Single Run
- One pod
- Idempotent task
- E.g., migrate data, send email batch

### Parallel Fixed Count
```yaml
completions: 100
parallelism: 10
```

Process 100 items, 10 at a time.

### Work Queue
```yaml
parallelism: 5
# No completions; pods exit 0 when queue empty
```

5 workers pull from queue (Redis, SQS, etc.); exit when done.

### Indexed
```yaml
completionMode: Indexed
completions: 10
```

Each pod gets `JOB_COMPLETION_INDEX` (0-9). Use to partition work.

## Cleanup

After completion:
```yaml
ttlSecondsAfterFinished: 3600
```

Job + pods garbage collected after 1 hour.

Without: accumulate; clutter.

## Job Retries

Retry pod on failure:
- `restartPolicy: OnFailure`: same container restarts
- `restartPolicy: Never`: new pod created

`backoffLimit` controls total tries.

Exponential backoff: 10s, 20s, 40s, ...

## Suspend / Resume

```yaml
spec:
  suspend: true
```

Job pauses. To resume:
```bash
kubectl patch job/myjob -p '{"spec":{"suspend":false}}'
```

For: pause batch during maintenance.

## CronJob

Scheduled Jobs:
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: daily-report
spec:
  schedule: "0 9 * * *"     # 9 AM daily
  timeZone: "America/Los_Angeles"   # 1.27+
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: report
            image: report-generator:v1
```

## Cron Syntax

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday=0)
│ │ │ │ │
* * * * *
```

Examples:
- `0 * * * *`: hourly
- `*/15 * * * *`: every 15 min
- `0 0 * * 0`: weekly Sunday midnight
- `0 6 1 * *`: 6 AM on the 1st
- `@daily`: equiv to `0 0 * * *`
- `@hourly`: equiv to `0 * * * *`

## Concurrency Policy

```yaml
spec:
  concurrencyPolicy: Allow   # default
  # Forbid: skip if previous running
  # Replace: kill previous, run new
```

For long-running jobs: `Forbid` (don't double-run).

## startingDeadlineSeconds

If CronJob missed (controller down): how late can it start?
```yaml
startingDeadlineSeconds: 120
```

After 2 min late: skip.

Without: many missed runs at once on recovery.

## History

```yaml
successfulJobsHistoryLimit: 3
failedJobsHistoryLimit: 1
```

Keep last 3 successful + 1 failed Job. Old ones removed.

For audit; debugging.

## Time Zone

Default UTC. `timeZone` field (1.27+) sets specific.

For older: convert your schedule to UTC.

## Failure Handling

If Job fails:
- CronJob notices (failedJobsHistoryLimit retains)
- Next scheduled run still fires

For: alerting on failures, use job monitoring.

Tools:
- Datadog / Prometheus → alert on Job failure
- Slack notification
- DLQ pattern for jobs producing data

## Idempotency

Run twice → same result.

For DB migrations: idempotent ("CREATE IF NOT EXISTS").

For email send: track sent (DB); skip if already.

## Long-Running

Jobs > 1 hr typically. Issues:
- Eviction during node maintenance
- Restart on failure → re-do work?

Mitigate:
- Checkpointing
- Resume on restart
- PDB to prevent eviction
- PVC for state

## Init Container for Setup

```yaml
spec:
  template:
    spec:
      initContainers:
      - name: setup
        image: setup-tool
        command: ["sh", "-c", "fetch-data && verify"]
      containers:
      - name: process
        image: processor
```

Init runs first; main only on init success.

## Parallel Patterns

### Indexed Job
Each pod knows its index; processes its partition:
```yaml
completionMode: Indexed
completions: 10
parallelism: 5
```

Pod gets `JOB_COMPLETION_INDEX=0..9`. Worker code:
```python
import os
index = int(os.environ["JOB_COMPLETION_INDEX"])
process_partition(index)
```

### Work Queue
- Pods pull from queue
- Exit on empty
- No completions

Pod:
```python
while True:
    msg = queue.pop()
    if not msg:
        sys.exit(0)
    process(msg)
```

## Cleanup TTL

```yaml
ttlSecondsAfterFinished: 3600
```

Job + pods deleted 1 hour after completion. Logs lost (if not shipped).

For: production. Without, clutter accumulates.

## Logs

```bash
# Job logs (latest pod)
kubectl logs job/import-data

# All pods of job
kubectl logs -l job-name=import-data

# Pod by index
kubectl logs job/import-data-0
```

## Failure Investigation

```bash
kubectl describe job/import-data
# Status: Failed
# Reason: BackoffLimitExceeded

kubectl get pods -l job-name=import-data
# Show all pod attempts

kubectl logs <failed-pod>
```

## Resources

Jobs use Pod resources:
```yaml
containers:
- name: job
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 1
      memory: 2Gi
```

For batch: often higher than user-facing.

## Best Practices

- Idempotent code
- Probes (for long-running)
- Resource requests + limits
- ttlSecondsAfterFinished
- backoffLimit reasonable
- Alert on failure
- Logs shipped externally

## Common Mistakes

- No idempotency (retries cause duplicates)
- No backoffLimit (infinite retries)
- Missed deadline (no startingDeadlineSeconds)
- Concurrency Allow + long job (overlap)
- No cleanup (accumulate)

## CronJob vs External Scheduler

Alternatives:
- Argo Workflows: DAG-based; richer
- Tekton Pipelines: CI/CD pipelines as K8s
- Airflow: orchestration (often runs outside K8s)
- AWS EventBridge → K8s Job

For simple cron: CronJob.
For complex DAG: Argo Workflows.

## Quick Refs

```bash
# Run Job
kubectl create job hello --image=busybox -- /bin/sh -c "echo hello"

# Manual trigger CronJob
kubectl create job manual-1 --from=cronjob/daily-report

# CronJob status
kubectl get cronjob
kubectl get jobs --selector=jobName=daily-report

# Suspend CronJob
kubectl patch cronjob/daily-report -p '{"spec":{"suspend":true}}'
```

## Interview Prep

**Junior**: "Job vs Deployment."

**Mid**: "CronJob design."

**Senior**: "Job idempotency."

**Staff**: "Batch processing 1M items."

## Next Topic

→ Move to [L13/C03 — Configuration](../C03/README.md)
