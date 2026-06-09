# L04/C04/T03 — Error Handling Patterns

## Learning Objectives

- Handle errors gracefully
- Distinguish recoverable vs fatal
- Use trap ERR for debugging

## Bail on First Error

```bash
set -euo pipefail
```

Already covered (T04 in C01). Foundation of safe scripts.

## Per-Command Handling

```bash
if ! cmd; then
    err "cmd failed"
    cleanup
    exit 1
fi
```

Or:
```bash
cmd || { err "cmd failed"; exit 1; }
```

## Try / Catch Pattern

```bash
result=$(some_cmd 2>&1) || {
    err "some_cmd failed: $result"
    exit 1
}
echo "$result"
```

Captures stderr; use in error message.

## ERR Trap

```bash
on_err() {
    local rc=$? line=$1
    err "FAILED at line $line (exit $rc)"
    cleanup
    exit $rc
}
trap 'on_err $LINENO' ERR
```

With `-E` propagates into functions.

## Per-Iteration Error Handling

```bash
failed=()
for item in "${items[@]}"; do
    if ! process "$item"; then
        warn "failed: $item; continuing"
        failed+=("$item")
    fi
done

if [[ ${#failed[@]} -gt 0 ]]; then
    err "${#failed[@]} items failed: ${failed[*]}"
    exit 2
fi
```

Continue past individual failures; report at end.

## Retry with Backoff

```bash
retry() {
    local max=${1:-5} delay=${2:-1}
    shift 2
    local attempt=0
    
    until "$@"; do
        ((attempt++))
        if (( attempt >= max )); then
            err "Failed after $max attempts: $*"
            return 1
        fi
        sleep $delay
        delay=$((delay * 2))
    done
}

retry 5 1 curl -f https://api.example.com
```

## Block / Rescue / Always

Bash doesn't have try/finally directly. Use trap + functions:

```bash
work() {
    setup
    do_work
    do_more
}

cleanup() {
    rm -f "$tmpfile"
    release_lock
}

trap cleanup EXIT
work || {
    err "work failed"
    exit 1
}
```

Even on error, EXIT trap runs cleanup.

## Distinguishing Errors

Check exit codes:
```bash
some_cmd
case $? in
    0) info "ok" ;;
    1) warn "expected failure mode" ;;
    2) err "config error" ;;
    *) err "unexpected" ;;
esac
```

Document your script's exit codes.

## set -e Gotchas (Important!)

Doesn't trigger in:
- `if cmd; then` (conditional context)
- `cmd1 && cmd2 || cmd3` chains
- Inside command substitution (varies)
- Inside functions called in conditional context

Mitigation: explicit `||` checks where critical.

## Robust Production Pattern

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

# Globals
TMPDIR=
LOCK=

# Cleanup
cleanup() {
    [[ -n "$TMPDIR" ]] && rm -rf "$TMPDIR"
    [[ -n "$LOCK" ]] && rm -f "$LOCK"
}
trap cleanup EXIT

# Error reporting
on_err() {
    local rc=$? line=$1 func=$2 src=$3
    echo "[ERROR] $src:$line in $func: exit $rc" >&2
    # Stack trace
    local i=0
    while caller $i; do ((i++)); done >&2
}
trap 'on_err $LINENO ${FUNCNAME[0]:-MAIN} ${BASH_SOURCE[0]}' ERR

# Lock
acquire_lock() {
    LOCK="${1:-/var/run/$(basename "$0").lock}"
    if ! ( set -o noclobber; echo $$ > "$LOCK" ) 2>/dev/null; then
        echo "Already running (PID $(cat "$LOCK"))" >&2
        exit 1
    fi
}

# Setup workspace
mkworkspace() {
    TMPDIR=$(mktemp -d)
    info "workspace: $TMPDIR"
}

acquire_lock
mkworkspace
# ... actual work
```

## Functions Returning Success/Fail

```bash
is_valid() {
    [[ -n "$1" ]] || return 1
    [[ "$1" =~ ^[a-z]+$ ]] || return 1
    return 0
}

if is_valid "$name"; then ...
```

## Timeout

```bash
if ! timeout 30 long_cmd; then
    err "timed out"
fi
```

`timeout` returns 124 on timeout.

## Critical Section Pattern

```bash
safe_operation() {
    local backup
    backup=$(mktemp)
    cp -p "$target" "$backup"
    
    if modify "$target"; then
        rm "$backup"
    else
        warn "modification failed; restoring backup"
        mv "$backup" "$target"
        return 1
    fi
}
```

## Common Patterns

### Validate Then Act
```bash
[[ -d "$DEST" ]] || fatal "Not a dir: $DEST"
[[ -w "$DEST" ]] || fatal "Not writable: $DEST"
do_work "$DEST"
```

### Dry-Run First
```bash
$DRY_RUN && {
    info "DRY-RUN: would run: $cmd"
    return 0
}
eval "$cmd" || fatal "command failed"
```

### Confirm Destructive
```bash
read -p "Really delete? [y/N] " ans
[[ "$ans" =~ ^[Yy]$ ]] || { echo "Aborted"; exit 0; }
```

## Debugging Aids

```bash
# Verbose tracing
bash -x script.sh

# Trace specific section
set -x
critical_section
set +x

# PS4 prefix for trace
PS4='+ ${BASH_SOURCE}:${LINENO}: ${FUNCNAME[0]:-main}: '
```

## Common Mistakes

- **Ignoring exit codes**: bug-hiding
- **Catching too broadly**: hides distinctly different failures
- **No cleanup on error**: leaves temp files
- **Generic error messages**: hard to diagnose
- **Continuing on critical errors**: e.g., backup failed → still delete original

## Interview Prep

**Junior**: "Exit on first error."

**Mid**: "Retry with exponential backoff."

**Senior**: "Cleanup runs even on Ctrl-C."

**Staff**: "Robust script with stack traces on error."

## Next Topic

→ [T04 — Dry-Run, Idempotency, Atomic Operations](T04-Dry-Run-Idempotency.md)
