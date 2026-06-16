# L04/C05/T01 — When to Move to Python/Go

## Learning Objectives

- Recognize bash's limits
- Choose appropriate language
- Migrate complex scripts

## Bash Sweet Spot

Bash excels at:
- Glue between CLI tools
- Quick automation
- Up to a few hundred lines
- One-off tasks
- Production deploy scripts (simple ones)
- Wrappers around other tools

## Switch When

### > 300 Lines
Maintenance burden grows nonlinearly. Functions help but bash gets unwieldy.

### Complex Data Structures
- Bash arrays are limited (1D)
- No real types
- Associative arrays clunky
- JSON manipulation painful past simple jq

### Multi-Threaded I/O at Scale
- Background jobs work but limited
- Real concurrency: Go goroutines

### Cross-Platform (Windows)
Bash needs WSL or Git Bash. Python/Go run natively.

### Production Tool for Many Users
- Distribution: bash → must have bash; Python → must have venv; Go → single binary
- Single binary wins

### Need Unit Tests
- bats exists but limited
- Python pytest / Go testing are much richer

### Network Operations
- Bash + curl + jq works for simple
- Beyond: SDK in Python/Go

## Python Wins

Python is great for:
- Glue scripts
- API integrations
- Data processing
- Reports
- Config generation
- Small CLIs

```python
# What was 30 lines of bash with awk/grep/sed:
import json
data = json.load(open('data.json'))
errors = [r for r in data['records'] if r['status'] == 'error']
print(f"{len(errors)} errors")
```

## Go Wins

Go is great for:
- CLI tools (single binary)
- Daemons (controllers, exporters)
- Performance matters
- K8s operators
- Network services

```go
// Distributed as single binary; no runtime needed
package main
func main() {
    // ...
}
```

## Migration Strategy

### Wrap First, Replace Later
```bash
# main.sh
exec python3 ./main.py "$@"
```

Users use `main.sh`; internal is Python.

### Incremental
- New features in Python
- Old bash kept until replaced
- Tests guide migration

### Shell-Out from Python
Python can still run bash commands:
```python
import subprocess
result = subprocess.run(["kubectl", "get", "pods"], capture_output=True, text=True)
```

For simple shell tasks: still subprocess. For data: parse + manipulate in Python.

## Examples

### When Bash Is Fine
```bash
#!/usr/bin/env bash
set -e
docker build -t myapp:latest .
docker push myorg/myapp:latest
kubectl rollout restart deployment/myapp
```

20 lines; clear; bash is right.

### When Bash Hurts
```bash
# 500 lines parsing CSV, grouping by category, sending HTTP, aggregating
# This needs Python
```

## Performance Comparison

| Task | Bash | Python | Go |
|---|---|---|---|
| Start up | 5ms | 50ms (CPython) | 5ms |
| HTTP request | curl 100ms | requests 100ms | net/http 100ms |
| Parse 100K JSON entries | painful | ~1s | ~0.1s |
| 1000 concurrent connections | painful | OK with asyncio | trivial |

For network/data workloads: Python/Go are much faster to develop AND run.

## Tooling Comparison

| | Bash | Python | Go |
|---|---|---|---|
| Lint | shellcheck | ruff, pylint | golangci-lint |
| Format | shfmt | black, ruff | gofmt (built-in) |
| Test | bats | pytest | go test |
| Type check | none | mypy | built-in |
| Dependencies | yum/apt | pip + venv | go.mod |
| Distribution | source | wheel + venv | single binary |

## Distribution

Bash: target machine must have bash + tools you use.
Python: pyinstaller / PEX / Nuitka can make standalone (large).
Go: `go build` → single binary. Distribution wins.

## What to Pick

| Task | Pick |
|---|---|
| < 100 lines, glue | Bash |
| Glue + light logic | Bash |
| Data manipulation | Python |
| API integration | Python |
| K8s controller | Go |
| Distributable CLI | Go |
| Daemon | Go (or Rust) |
| ML / data science | Python |
| One-off ad-hoc | Bash or Python |

## Common Mistakes

- **"Rewrite everything"**: a big-bang port stalls for months with no incremental benefit; migrate the painful parts first.
- **Wrong language for the task**: reaching for Python/Go where a 20-line bash glue script is clearer and faster to ship.
- **Mixing Python and bash at random**: two runtimes, two toolchains, two sets of bugs to maintain.
- **Staying in bash past its limits**: 500-line scripts juggling CSV/JSON/HTTP become unmaintainable — that pain is the signal to switch.
- **Ignoring distribution cost**: shipping a bash script that assumes `jq`, `yq`, GNU coreutils, and bash 5 to machines that have none of them.
- **No tests during migration**: rewriting behavior without a test harness means you can't prove the new version matches the old.

## Honest Truth

Most DevOps engineers underuse Python. Tasks that should be Python get done in bash + duct tape.

Investing 1 week to get fluent in Python pays off years.

## Best Practices

- Keep bash for what it's great at: gluing CLI tools, short deploy/build scripts, wrappers — roughly up to a few hundred lines.
- Switch to Python when you hit real data structures, JSON beyond simple jq, API integrations, or a need for unit tests.
- Switch to Go (or Rust) when you need a single static binary, true concurrency, performance, or a long-lived daemon/controller.
- Migrate incrementally: wrap the existing entrypoint (`exec python3 main.py "$@"`) so callers don't change while internals move.
- Let tests drive the port — write characterization tests against the old script, then make the rewrite pass them.
- Match distribution to audience: source-bash needs the same tools everywhere; a Go binary needs nothing; a Python tool needs a managed venv.

## Quick Refs

```bash
# Decision heuristics
# < ~100 lines, glue only ............ bash
# data structures / JSON / APIs ...... Python
# single binary / daemon / perf ...... Go (or Rust)

# Wrap-then-replace: keep the bash entrypoint, run new code underneath
#!/usr/bin/env bash
exec python3 "$(dirname "$0")/main.py" "$@"

# Shell out from Python when a CLI tool is still the right call
# import subprocess
# out = subprocess.run(["kubectl","get","pods"], capture_output=True, text=True).stdout

# Toolchain parity to look for before/after migrating
#            lint            format   test     distribute
# bash       shellcheck      shfmt    bats     source + tools
# python     ruff/pylint     ruff     pytest   wheel + venv
# go         golangci-lint   gofmt    go test  single binary

# Smell checks on an existing script
wc -l script.sh                      # length pressure
grep -c 'eval' script.sh             # eval count (refactor target)
grep -cE 'awk|sed|jq' script.sh      # heavy text munging -> consider Python
```

## Interview Prep

**Mid**: "When move from bash to Python?"

**Senior**: "Migration story for legacy script."

**Staff**: "Pick a language for a new internal CLI."

## Next Topic

→ [T02 — Makefile for Automation](T02-Makefile.md)
