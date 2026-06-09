# L06/C05/T02 — Idempotency, Dry-run, Confirmations

## Learning Objectives

- Design for safe retries
- Implement dry-run that actually catches issues

## Idempotency

Same input → same end state, regardless of how many times you run.

```bash
mytool create-user alice    # creates
mytool create-user alice    # no-op (already exists; OK)
mytool create-user alice    # no-op
```

Not idempotent:
```
mytool send-email --to alice@x.com    # sends EVERY time
```

## Why It Matters

- Retries safe (network blip = re-run)
- Partial failures recoverable
- CI/CD pipelines re-run
- Distributed: many runners may try same op

## Patterns

### Check Then Act
```python
existing = get_user("alice")
if not existing:
    create_user("alice")
else:
    logger.info("User exists, skipping")
```

Race condition: two runs check at same time, both create. Mitigations:
- Unique constraint at DB level → second fails gracefully
- Distributed lock
- Idempotency token

### Upsert
```sql
INSERT INTO users (name) VALUES ('alice') ON CONFLICT DO NOTHING;
```

K8s:
```yaml
kubectl apply -f deployment.yaml    # creates or updates
```

### Idempotency Key
```
POST /payments
Idempotency-Key: my-request-abc
{"amount": 100}
```

Server: if seen `my-request-abc` before, return cached result. Else process; cache.

Used by Stripe, AWS, etc.

## Hard Cases

- "Send email" (not idempotent inherently)
  - Solution: track sent emails by ID; check before send
- "Charge credit card"
  - Solution: idempotency key
- "Delete and recreate"
  - Solution: just "update" with apply

## Dry-Run

Show what would happen; don't do it.

```bash
mytool deploy myapp --dry-run
# Output:
# Would update deployment myapp from v1.2.2 to v1.2.3
# Would scale replicas from 3 to 5
# No changes will be made
```

### Why
- Verify before production
- Code review (paste diff in PR)
- CI can show changes
- Trust building

### Two Levels

**Plan**: full simulation; outputs concrete diff (Terraform plan).

**Preview**: best-effort; shows API calls (kubectl diff).

### Anti-Pattern
```bash
$ mytool delete-all --dry-run
✓ Done
```

Did nothing. Useless. Real dry-run shows what WOULD have been deleted:
```bash
$ mytool delete-all --dry-run
Would delete:
- pod/web-1
- pod/web-2
- pod/web-3
3 resources affected
```

## Implementation

```python
def deploy(service: str, dry_run: bool = False):
    current = get_deployment(service)
    desired = build_desired(service)
    diff = compute_diff(current, desired)
    
    if not diff:
        print("No changes")
        return
    
    print_diff(diff)
    
    if dry_run:
        print("Dry-run; no changes made")
        return
    
    apply(desired)
    print("Deployed")
```

```go
type DeployOptions struct {
    Service string
    DryRun  bool
}

func Deploy(opts DeployOptions) error {
    current := getDeployment(opts.Service)
    desired := buildDesired(opts.Service)
    diff := computeDiff(current, desired)
    
    printDiff(diff)
    
    if opts.DryRun {
        fmt.Println("Dry-run; no changes")
        return nil
    }
    
    return apply(desired)
}
```

## Confirmations

For destructive ops, prompt unless `--yes` / `-y`:
```python
@app.command()
def delete_all(yes: bool = typer.Option(False, "--yes", "-y")):
    items = find_items()
    print(f"Will delete {len(items)} items")
    
    if not yes:
        confirm = input("Type 'yes' to confirm: ")
        if confirm != "yes":
            print("Aborted")
            return
    
    for item in items:
        delete(item)
```

### When To Prompt

- Deletes
- Mass updates
- Cross-environment ops
- Production changes

### When NOT

- Scripts (use `-y`)
- Read-only ops

### Strong Confirmations

For VERY dangerous:
```
$ mytool nuke-cluster prod
You are about to DELETE production cluster.
This includes 47 deployments and 12 databases.
This action is IRREVERSIBLE.

Type "DELETE PROD" to confirm: _
```

Force user to type something specific (not just "y").

## Force Flag

For when user knows what they want:
```bash
mytool deploy myapp --force         # skip safety checks
mytool delete-pod web-1 --force     # skip grace period
```

Document well; never default.

## Auto-Approve Flags

For CI:
```bash
mytool plan -auto-approve        # apply without confirm
```

Be EXTREMELY careful here. CI runs without human review = blast radius.

## Diff Display

```
$ mytool deploy myapp --dry-run

  Deployment: myapp
~ Replicas:    3 → 5
~ Image:       myapp:v1.2.2 → myapp:v1.2.3
+ Env: NEW_VAR=foo
- Env: OLD_VAR=bar

2 modifications, 1 addition, 1 deletion
```

Color: red (-), green (+), yellow (~). 

Use existing libraries:
- Go: `github.com/sergi/go-diff`
- Python: `difflib`

## Plan File (Terraform-Style)

```bash
mytool plan -out=plan.tfplan       # plan only
mytool apply plan.tfplan           # apply specific plan
```

Two phases:
1. Plan reviewed by humans
2. Apply runs exactly the planned changes (no re-plan)

Critical: prevents drift between plan time and apply time.

## Retry Strategies

For non-idempotent:
- Idempotency key on every call
- Track operation state
- Resume from last successful step

For idempotent:
- Just retry with backoff

## Common Mistakes

- `--dry-run` that does nothing useful
- Operations that aren't idempotent → repeat = damage
- No confirmation on destructive
- Confirmation everywhere (annoying)
- Plan/apply gap (state changes between)

## Real Examples

- Terraform: plan + apply, idempotent
- Ansible: idempotent (most modules)
- kubectl: apply is idempotent
- Helm: install vs upgrade vs upgrade-install

## Interview Prep

**Mid**: "Make this script idempotent: [non-idempotent example]."

**Senior**: "Design dry-run for tool that modifies DB."

**Staff**: "Plan/apply gap — how to mitigate."

## Next Topic

→ [T03 — Logging, Tracing, Metrics in Tools](T03-Logging-Tracing.md)
