# L06/C05/T01 — Anatomy of a Production Tool

## Learning Objectives

- Understand what makes a tool production-grade
- Audit your own tools

## What "Production-Grade" Means

Not just "it works on my machine." A production tool is one that:
- Other engineers trust to use
- Works in CI/CD pipelines
- Handles edge cases gracefully
- Is observable
- Can be safely deployed everywhere

## Anatomy Checklist

### 1. Idempotent
Run twice → same end state. Critical for retries.
```
deploy v1.0   # creates resources
deploy v1.0   # no-op (already there)
```

### 2. Dry-Run Mode
Show what WOULD happen; don't actually do it.
```bash
mytool deploy myapp --dry-run
# Would scale myapp to 5 replicas
# Would update image to v1.2.3
```

### 3. Help Text
`--help` for every command; with examples.
```
$ mytool deploy --help
Usage: mytool deploy [OPTIONS] SERVICE

  Deploy SERVICE to staging environment

Options:
  --version TEXT      Image version  [default: latest]
  --dry-run           Don't actually deploy
  --help              Show this message

Examples:
  mytool deploy myapp
  mytool deploy myapp --version=v1.2.3
```

### 4. Sensible Defaults
Common cases work without flags. Power users override.

### 5. Exit Codes
0 = success; non-zero = failure (specific codes preferred):
```
0  success
1  generic error
2  usage error
3  config error
4  permission denied
5  not found
```

CI / scripts depend on this.

### 6. Configurable Verbosity
```bash
mytool deploy myapp           # info
mytool deploy myapp -v        # debug
mytool deploy myapp -vv       # trace
mytool deploy myapp --quiet   # only errors
```

### 7. Structured Logging
JSON to stdout/stderr; parseable.
```json
{"level":"info","msg":"deploying","service":"myapp","version":"v1.2.3","time":"2026-06-09T10:00:00Z"}
```

### 8. Output Formats
Default: human (table). Optional: JSON, YAML.
```bash
mytool get pods                 # table
mytool get pods -o json         # for scripts
mytool get pods -o yaml         # editing
```

### 9. Versioning
```bash
$ mytool --version
mytool v1.2.3 (commit abc123, built 2026-06-09)
```

### 10. Config File + Env + Flag
Precedence: flag > env > config > default.

```bash
# config file
$ cat ~/.mytool.yaml
region: us-east-1

# env
$ export MYTOOL_REGION=us-west-2

# flag
$ mytool deploy --region=eu-west-1
# Uses eu-west-1
```

### 11. Authentication
- Use existing creds (aws CLI, kubectl, gcloud)
- Or accept explicit credentials
- Never hardcode

### 12. Network Resilience
- Timeouts on ALL network calls
- Retries with backoff
- Circuit breaker for repeated failures

### 13. Concurrency Control
For destructive ops: limit blast radius.
```bash
mytool delete-pods --parallel=5      # not 1000 at once
```

### 14. Progress Indication
For long ops:
```
[=====     ] 50% (5/10)
deploy 5 of 10...
```

### 15. Confirmation for Destructive
```
$ mytool delete-all-prod
This will delete 47 resources in production. Type "yes" to confirm:
```

### 16. Tested
Unit + integration. CI runs on every commit.

### 17. Documented
README, examples, runbook for failure scenarios.

### 18. Distributed
Easy install:
- Homebrew tap
- apt/yum
- Docker image
- Standalone binary
- pip install

### 19. Backwards Compatible (Versioned API)
v1 commands keep working in v2. Or version explicitly:
```bash
mytool v1 deploy ...
mytool v2 deploy ...
```

### 20. Observable
Tool itself emits metrics/traces if possible.

## Common Mistakes

### Black Box
```
$ mytool deploy myapp
✓ Done
```
Engineer can't tell what happened. Add `-v`:
```
$ mytool deploy myapp -v
> connecting to cluster prod
> fetching current deployment
> current image: v1.2.2
> updating to v1.2.3
> rolling update started
> waiting for rollout (timeout 5m)
> rollout complete
✓ Done
```

### Silent Failures
```python
try:
    deploy()
except:
    pass
```
Logs every failure. Returns non-zero. Tells user what happened.

### Hard Coded
```python
ENV = "prod"
```
Make it config-driven.

### Required Manual Steps
Tool that says "now SSH to box X and run Y" → not a tool.

### Surprising Side Effects
`mytool list-pods` shouldn't write to a cache file unless documented.

### Tight Coupling
Tool that ONLY works with v1.21 of K8s; or ONLY your-company's setup.

## Example: Real Tool

GitHub CLI (`gh`):
- Idempotent: `gh pr create` on existing PR fails clearly
- Help: `gh --help`, `gh pr --help`, `gh pr create --help`
- Defaults: detects repo from cwd; uses current branch
- Exit codes: 0 success, 1 user error, etc.
- Verbose: `--verbose`
- Output: `--json`
- Versioned: `gh --version`
- Config: `~/.config/gh/config.yml` + env + flags
- Auth: `gh auth login`
- Network: retries
- Confirmation: prompts before destructive ops
- Tested
- Documented
- Multi-platform binaries

Excellent model.

## Iteration

Tools start simple. As use grows, add:
- Better errors (when users hit them)
- New flags (when use cases arise)
- Performance (when slow)
- New formats (when needed)

Don't pre-build features.

## Audit Your Tool

Ask:
- Could a new engineer use it?
- What happens if it fails halfway?
- What if network blips?
- What if input is bad?
- How do I tell what it's doing?
- How do I rollback?

## Best Practices

- Make every mutating tool idempotent and ship `--dry-run` first; users should be able to preview before committing.
- Read config with clear precedence (flags > env > file > defaults) and validate it at startup, failing fast with an actionable message.
- Emit structured logs to stderr and machine-readable results (`--output json`) to stdout so the tool composes in pipelines.
- Return meaningful exit codes (0 success, distinct non-zero per failure class) so CI and wrappers can branch on them.
- Confirm destructive actions by default, with `--yes/--force` to bypass for automation.
- Embed a `--version`, write a real `--help`, and keep the tool small — add features when users hit the need, not preemptively.

## Quick Refs

```text
PRODUCTION-TOOL ANATOMY CHECKLIST
  [ ] idempotent (run twice -> same state)
  [ ] --dry-run preview
  [ ] config precedence: flag > env > file > default, validated at startup
  [ ] structured logs to stderr, results to stdout (--output json)
  [ ] meaningful exit codes (0 ok; non-zero per failure class)
  [ ] confirmation on destructive ops (+ --yes/--force)
  [ ] --version (build-injected) and --help
  [ ] retries with backoff on transient failures
  [ ] observable: request IDs / audit log
```

```bash
# Compose-friendly invocation
mytool deploy web --dry-run            # preview
mytool deploy web --output json | jq .status
mytool deploy web --yes && echo ok || echo "exit $?"
```

```python
import sys, logging
log = logging.getLogger("mytool")
logging.basicConfig(stream=sys.stderr, level=logging.INFO,
                    format='{"ts":"%(asctime)s","lvl":"%(levelname)s","msg":"%(message)s"}')

EXIT_OK, EXIT_VALIDATION, EXIT_RUNTIME = 0, 2, 1
def main() -> int:
    if not valid_config():
        log.error("invalid config")          # diagnostics -> stderr
        return EXIT_VALIDATION
    print(result_json)                        # result -> stdout
    return EXIT_OK

if __name__ == "__main__":
    sys.exit(main())
```

## Interview Prep

**Mid**: "What makes a CLI good?"

**Senior**: "Design a deploy tool from scratch."

**Staff**: "When tool grows complex; what next?"

## Next Topic

→ [T02 — Idempotency, Dry-run, Confirmations](T02-Idempotency-Dryrun.md)
