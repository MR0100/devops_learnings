# L06/C01/T02 — When Bash Isn't Enough

## Learning Objectives

- Recognize signals to move beyond bash
- Choose successor language

## Bash Limits

### Lines
- < 100 lines: bash fine
- 100-300: bash workable
- > 300: drag
- > 500: pain
- > 1000: stop

### Capabilities Bash Lacks
- Real data structures (records, nested maps)
- Type checking
- Error handling beyond exit codes
- Standard library (HTTP, JSON, datetime)
- Cross-platform (Windows)
- Real testing
- Memory safety

## Signs You've Hit the Wall

- Lots of `eval`
- Regex hell to parse JSON
- Multi-step error handling getting tangled
- Variables leaking across functions
- Same logic implemented N times
- Difficult to test
- Hard to onboard new engineers
- Hard to debug

## Python or Go?

### Python
- Pros: fast to write; great for data; massive library; APIs/automation
- Cons: deployment (venv complexity); slower execution; not single binary

### Go
- Pros: single binary; fast; concurrency easy; great for distributed
- Cons: slower to prototype; more verbose; less data ecosystem

### Quick Decision

| Need | Pick |
|---|---|
| Glue / automation / one-off | Python |
| Data manipulation / reporting | Python |
| ML / data science | Python |
| Internal CLI for team | Go |
| Daemon / service | Go |
| Distributed binary | Go |
| K8s operator | Go (required) |

## Migration Patterns

### Wrap First
```bash
# main.sh — bash entry stays; logic moves out
exec python3 ./main.py "$@"
```

Old callers still use `main.sh`. Internal Python.

### Incremental
- Keep bash for skeleton
- Move functions to Python one at a time
- Tests guide

### Shell Out from Python
```python
import subprocess
result = subprocess.run(["kubectl", "get", "pods"], capture_output=True, text=True)
```

Python orchestrates; subprocess for shell ops.

## Tools That Help

### Python
- subprocess for shell calls
- pathlib for files
- argparse / typer / click for CLI
- structlog for logging
- pytest for tests
- uv / poetry for deps

### Go
- exec.Command for shell
- cobra / urfave/cli for CLI
- zap / slog for logging
- testing (built-in)
- go.mod / vendor

## Common Migration Anti-Patterns

- Rewrite everything at once
- Python where bash is fine
- Bash function calling Python script calling bash
- Type checks added but ignored

## Real Examples

### Worth Moving to Python
- 400-line bash with JSON parsing and HTTP
- Multi-account AWS automation
- Report generators
- Data shuffling between systems

### Keep in Bash
- 50-line deploy script
- CI helper scripts
- Container ENTRYPOINTs
- Simple cron jobs

## Skills to Invest In

If new to Python:
- 2 weeks: comfortable for scripts
- 2 months: production-quality CLIs
- 6 months: complex tools

If new to Go:
- 2 weeks: simple programs
- 2 months: CLIs with Cobra
- 6 months: production services

Worth it.

## Hybrid Reality

Most teams have:
- Bash (50%): deploy, glue, ENTRYPOINTs
- Python (30%): tools, reports, automation
- Go (20%): operators, daemons, CLIs

Don't pick one for everything.

## Interview Prep

**Mid**: "When move to Python from bash?"

**Senior**: "Migrate a 500-line bash script."

**Staff**: "Choose between Python and Go for a new tool."

## Next Chapter

→ [C02 — Python for DevOps](../C02/README.md)
