# L10/C03/T03 — State Locking & Concurrency

## Learning Objectives

- Understand locking
- Resolve lock issues

## Locking

Prevents concurrent state writes.

Without: two terraform apply at same time → corrupt state.

## DynamoDB Lock (S3 Backend)

```hcl
backend "s3" {
  bucket         = "tfstate"
  key            = "prod.tfstate"
  region         = "us-east-1"
  dynamodb_table = "tflock"
  encrypt        = true
}
```

Apply:
1. Acquire lock in DDB (PutItem with condition: not exists)
2. Read state
3. Modify
4. Write state
5. Release lock (DeleteItem)

If lock held: error:
```
Error: Error acquiring the state lock
Lock Info:
  ID:        abc123
  Path:      tfstate/prod.tfstate
  Operation: OperationTypeApply
  Who:       alice@host
  Version:   1.7.0
```

## Lock Item

DDB table schema:
- LockID (Hash key): "<bucket>/<key>" 
- Info: JSON with who, when, etc.

```bash
aws dynamodb get-item --table-name tflock --key '{"LockID":{"S":"tfstate/prod.tfstate"}}'
```

## When Locks Stuck

Process killed mid-apply. Lock not released.

Diagnosis:
- See "lock acquired by ..."
- Check who; can they confirm done?

Fix:
```bash
terraform force-unlock LOCK_ID
```

Removes lock. Use ONLY if confident no apply in progress.

## TFC / HCP

Workspace locked during runs:
- Native locking
- UI shows lock state
- Can manually unlock with appropriate permissions

## Other Backends

| Backend | Lock |
|---|---|
| S3 + DDB | DDB conditional write |
| Azure | Blob lease |
| GCS | Cloud Storage objects |
| Consul | Consul session |
| TFC | Native |
| Local | None (single user assumed) |

## Concurrency

Terraform itself parallel by default:
- Reads / plans: 10 concurrent operations
- Tune: `-parallelism=20`

For provider-side rate limits: reduce.

## Plan Parallelism

```bash
terraform plan -parallelism=10    # default
terraform apply -parallelism=20
```

For: faster apply (many independent resources).
Against: AWS API rate limits.

For very large states: balance.

## Read-Only Operations

`terraform refresh`, `terraform plan` (without changing): still acquires lock briefly (to read consistent state).

`terraform plan -lock=false` skips (rare; risk).

## CI Patterns

CI applies:
- Pull state (acquires lock)
- Plan
- (await approval)
- Apply
- Release

If approval takes long: lock held during, blocking others.

Alternative:
- Plan: get plan; no lock
- Approve
- Apply: lock, apply, release

For minimal contention.

## TFC Run Triggers

PR opened → TFC plans
Approve → TFC applies

State locked during apply only.

## Multiple Workspaces / States

Different state files = different locks. No contention between.

Why split state: parallel work; smaller blast.

## Anti-Patterns

- Skipping lock (-lock=false)
- Local state for team (no lock)
- One state for everything (always locked)
- force-unlock without checking

## Detection

`terraform plan` errors quickly if locked. Message tells who.

Slack notification?
- Wrap CI: if lock fail → alert with info.

## Best Practices

- Locking always (don't disable)
- DDB / equivalent backend
- Document lock policy
- Train team on force-unlock cautions
- Split state for parallelism

## Force Unlock Procedure

1. Confirm no apply running (Slack / dashboard)
2. Get lock ID from error
3. `terraform force-unlock LOCK_ID`
4. Retry your operation

## Lock Timeout

Lock has no inherent timeout. Held until released.

If process killed: lock orphaned.

## Diagnostic

```bash
# DDB
aws dynamodb scan --table-name tflock

# S3 state
aws s3 ls s3://tfstate/

# TFC
# Use UI / API
```

## Race Conditions

Even with lock: race if:
- Manual change in console mid-apply (drift)
- External system changes resource

State locking doesn't lock cloud-side. Just Terraform's state.

For external race: prevent via SCP / IAM lockdown.

## TFC Runs Queuing

TFC queues runs in workspace:
- Apply 1 → Apply 2 waits
- Plan 1 + Plan 2 may run parallel (no state write)

For: ordered changes.

## Multi-State Locking

Two states (vpc.tfstate + app.tfstate):
- Independent locks
- Can apply both concurrently
- Cross-state dependencies via data source

App's state plan reads vpc's state (data source). vpc lock not affected.

## Pipelines

GitHub Actions:
```yaml
- run: terraform init
- run: terraform plan -out=plan
- uses: approval action
- run: terraform apply plan
```

Lock acquired in apply step.

## Common Mistakes

- Force-unlock while apply running (corruption!)
- No DDB table (S3 backend without lock)
- Local state in CI
- Long-held lock during approval window

## Best Practices

- Lock always
- Quick approval (don't hold)
- Plan separate from apply
- Document procedures
- Alert on lock failure

## Long-Running Workloads

If apply takes 30 min:
- Lock held 30 min
- Other developers wait
- Mitigate: split state into smaller

## Distributed Locks (Beyond Terraform)

For app-level coordination: Redis SET NX EX, ZooKeeper, etcd, DynamoDB.

Concept same; just Terraform's specific impl.

## Quick Refs

```bash
terraform apply
# Error: Lock failed
# Use force-unlock cautiously

terraform force-unlock LOCK_ID

# Check DDB
aws dynamodb get-item --table-name tflock --key '{"LockID":{"S":"..."}}'

# Skip lock (don't)
terraform apply -lock=false
```

## Interview Prep

**Mid**: "Why state lock."

**Senior**: "Stuck lock — resolve."

**Staff**: "Multi-team Terraform without contention."

## Next Topic

→ [T04 — terraform state Commands](T04-State-Commands.md)
