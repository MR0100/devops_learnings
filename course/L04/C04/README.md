# L04/C04 — Production-Grade Scripts

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Argument-Parsing.md) | Argument Parsing (getopts, getopt) | 1 hr |
| [T02](T02-Logging.md) | Logging, Stderr vs Stdout, Tee | 0.5 hr |
| [T03](T03-Error-Handling.md) | Error Handling Patterns | 1 hr |
| [T04](T04-Dry-Run-Idempotency.md) | Dry-Run, Idempotency, Atomic Operations | 1 hr |
| [T05](T05-Shellcheck.md) | ShellCheck and Style Guides | 0.5 hr |

## The Production-Grade Template

```bash
#!/usr/bin/env bash
#
# myscript.sh — does X
# Usage: myscript.sh [-d] [-v] FILE
# Author: you
#
set -euo pipefail
IFS=$'\n\t'

# Constants
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_PREFIX="[$(basename "$0")]"

# Defaults
DRY_RUN=false
VERBOSE=false

# --- Helpers ---

log()   { echo "$LOG_PREFIX $*" >&2; }
err()   { echo "$LOG_PREFIX ERROR: $*" >&2; }
fatal() { err "$*"; exit 1; }
debug() { $VERBOSE && log "DEBUG: $*"; }

run() {
  log "$*"
  $DRY_RUN || "$@"
}

usage() {
  cat >&2 <<EOF
Usage: $(basename "$0") [-d] [-v] FILE

Options:
  -d  Dry-run mode (print commands, don't execute)
  -v  Verbose
  -h  Help
EOF
  exit 1
}

# --- Argument parsing ---
while getopts ":dvh" opt; do
  case $opt in
    d) DRY_RUN=true ;;
    v) VERBOSE=true ;;
    h|*) usage ;;
  esac
done
shift $((OPTIND - 1))

[[ $# -eq 1 ]] || usage
FILE="$1"

# --- Validation ---
[[ -f "$FILE" ]] || fatal "File not found: $FILE"

# --- Cleanup ---
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

# --- Main ---
log "Processing $FILE"
run cp "$FILE" "$TMPDIR/"

log "Done."
```

## Argument Parsing

### getopts (POSIX, single-letter)

```bash
while getopts ":d:v" opt; do
  case $opt in
    d) DIR="$OPTARG" ;;       # -d requires arg
    v) VERBOSE=true ;;
    :) fatal "Missing arg for -$OPTARG" ;;
    ?) fatal "Unknown option: -$OPTARG" ;;
  esac
done
shift $((OPTIND - 1))
```

### Long options (manual)

```bash
DIR=""
VERBOSE=false
while [[ $# -gt 0 ]]; do
  case $1 in
    --dir)   DIR="$2"; shift 2 ;;
    --dir=*) DIR="${1#*=}"; shift ;;
    -v|--verbose) VERBOSE=true; shift ;;
    -h|--help) usage ;;
    --) shift; break ;;
    -*) fatal "Unknown: $1" ;;
    *) ARGS+=("$1"); shift ;;
  esac
done
```

## Logging

### Stderr vs Stdout

- **Stdout**: program results (data the user/pipeline wants)
- **Stderr**: progress, warnings, errors

> Never write logs to stdout if your script also outputs data. Otherwise, pipelines break.

```bash
# Good
echo "result: $value"          # stdout (real output)
log "computed in $duration"    # stderr (info)

# Redirection
cmd >output.txt 2>errors.txt   # split
cmd >out 2>&1                  # both to out
cmd &> all.log                 # both to all.log
cmd >> append.log              # append

# Suppress
cmd >/dev/null 2>&1
```

### tee
```bash
cmd | tee log.txt              # see output AND save
cmd | tee -a log.txt           # append
cmd | tee /dev/tty | next      # show on terminal AND pipe
sudo tee /etc/sysctl.conf <<<"..."  # write privileged via tee
```

### Structured Logging
For production tools, log JSON:

```bash
jlog() {
  local level="$1" msg="$2"
  jq -nc --arg ts "$(date -uIs)" --arg lvl "$level" --arg m "$msg" \
    '{ts:$ts, level:$lvl, msg:$m}' >&2
}

jlog info "starting"
jlog error "failed connecting"
```

## Error Handling Patterns

### Bail on first error
```bash
set -euo pipefail
```

### Trap errors with line context (bash 4+)
```bash
on_err() {
  local code=$? line=$1
  err "Failed at line $line (exit $code)"
  exit $code
}
trap 'on_err $LINENO' ERR
```

### Try/catch pattern
```bash
if ! result=$(some_cmd 2>&1); then
  err "some_cmd failed: $result"
  exit 1
fi
```

### Per-iteration error handling
```bash
for item in "${items[@]}"; do
  if ! process "$item"; then
    err "Failed on $item; continuing"
    failed+=("$item")
  fi
done

[[ ${#failed[@]} -eq 0 ]] || {
  err "Some items failed: ${failed[*]}"
  exit 2
}
```

### set -e gotchas
`set -e` doesn't exit when:
- Failure is part of a conditional (`if`, `while`, `until`, `&&`, `||`)
- Inside command substitution: `x=$(failing_cmd)`
- Inside a function called inside `if` (the function loses -e effect)

```bash
# This won't trigger -e:
if some_cmd; then ...        # OK
some_cmd && other            # OK

# Use:
some_cmd || true             # explicit ignore
```

## Dry-Run

A dry-run mode prints commands without running them. Critical for destructive operations.

```bash
run() {
  if $DRY_RUN; then
    log "DRY-RUN: $*"
  else
    "$@"
  fi
}

run rm -rf "$DIR"
run kubectl delete pod foo
```

## Idempotency

Re-running the script should be safe.

```bash
# Bad
mkdir /opt/myapp                 # fails if exists

# Good
mkdir -p /opt/myapp              # idempotent

# Bad
echo "new content" >> /etc/conf  # appends every time

# Good (check first or use marker)
grep -qxF "new content" /etc/conf || echo "new content" >> /etc/conf
```

## Atomic Operations

A failed write should not leave a corrupt state.

```bash
# Atomic file replacement (same filesystem)
tmp=$(mktemp /tmp/data.XXXXXX)
generate_content > "$tmp"
mv "$tmp" /etc/data        # rename is atomic
```

## Locking (prevent concurrent runs)

```bash
exec 200>"$LOCKFILE"
flock -n 200 || fatal "Already running"
# work
# flock auto-released on FD 200 close
```

## ShellCheck

The linter for shell. Catches dozens of common bugs:

```bash
shellcheck myscript.sh
```

Common findings:
- SC2086: Quote variables to prevent word splitting
- SC2046: Quote `$(...)` to prevent word splitting
- SC2155: Declare and assign separately (return code masking)
- SC2128: Expanding array without index → first element only

Run in CI:
```yaml
- name: ShellCheck
  uses: ludeeus/action-shellcheck@master
```

## Style Guides

- Google Shell Style Guide
- Anthropic / your team's
- Mozilla SOP

Common conventions:
- 2-space indent
- Variable names: lowercase locals, UPPERCASE globals/env
- Functions: snake_case
- `readonly` for constants
- Always use `local` in functions

## Interview Themes

- "Write a production-grade deployment script"
- "Handle errors gracefully — show me how"
- "Why use set -euo pipefail?"
- "Make a script idempotent — what does that mean?"
- "Why is shellcheck important?"
