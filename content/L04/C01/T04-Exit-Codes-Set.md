# L04/C01/T04 — Exit Codes, set -euo pipefail

## Learning Objectives

- Use strict mode for safer scripts
- Handle exit codes correctly
- Recognize the gotchas of `set -e`

## Exit Codes

Every command returns an exit code:
- `0` = success
- `1-125` = generic errors
- `126` = found but not executable
- `127` = command not found
- `128 + N` = killed by signal N (e.g., 130 = SIGINT/Ctrl-C, 137 = SIGKILL)
- `>255` = wraps (avoid)

```bash
command
echo $?           # last exit code

if cmd; then echo ok; else echo fail; fi
cmd || echo "failed"
cmd && echo "succeeded"
```

## Strict Mode

The opening of every serious bash script:
```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
```

### `set -e`
Exit on any unhandled error.

```bash
set -e
do_something    # if this fails, script exits
do_next         # only runs if previous succeeded
```

### `set -u`
Error on undefined variable.

```bash
set -u
echo "$undefined"   # error: unbound variable
```

Prevents typos:
```bash
rm -rf "$DEST_DIR/"   # typo "DEST_DR" without -u → rm -rf /
```

### `set -o pipefail`
Pipeline returns first nonzero exit code (not just last).

```bash
# Without pipefail: this exits 0 (grep succeeded even if curl failed)
curl bad-url | grep error

# With pipefail: exits nonzero from curl failure
set -o pipefail
curl bad-url | grep error
```

### `IFS=$'\n\t'`
Restricts word splitting to newlines and tabs (not spaces). Avoids issues with filenames containing spaces.

## Gotchas of `set -e`

`set -e` doesn't catch everything:

### Inside Conditionals
```bash
set -e

if failing_cmd; then ...   # OK; doesn't exit
fi

failing_cmd || true        # OK; explicit ignore
```

### Inside `&&` / `||`
```bash
cmd1 && cmd2     # cmd1 fail doesn't trigger -e
cmd1 || cmd2     # cmd1 fail doesn't trigger -e
```

### Inside Command Substitution (varies)
```bash
x=$(failing_cmd)   # bash <4.4: NO exit; >= 4.4: depends on shopt
```

### Inside Functions Called in `if`
```bash
set -e
myfunc() {
    failing_cmd
    echo "still here"    # runs! set -e doesn't apply
}

if myfunc; then ...
fi
```

When a function is called in a conditional context, `set -e` is suspended inside it.

## Trap

Run code on signals / exit.

```bash
cleanup() {
    rm -f "$tmpfile"
    echo "cleaning up"
}

trap cleanup EXIT          # always
trap cleanup INT TERM      # on Ctrl-C or kill

tmpfile=$(mktemp)
# script runs; cleanup auto-called on exit
```

### Errors with Line Number
```bash
on_err() {
    local rc=$? line=$1
    echo "ERROR: line $line, exit $rc" >&2
    exit $rc
}
trap 'on_err $LINENO' ERR
```

## Useful Exit Codes Convention

```bash
# In your script
exit 0    # success
exit 1    # generic error
exit 2    # usage error (bad arguments)
exit 64   # data format error
exit 78   # configuration error
```

Use higher numbers (64+) for specific meanings. /usr/include/sysexits.h has BSD conventions.

## Exit Code Propagation

```bash
main() {
    do_work
    return $?
}

main "$@"
exit $?
```

Final exit code matches what main returned.

## Best Pattern: Production Script Header

```bash
#!/usr/bin/env bash
#
# script.sh — does X
#
set -Eeuo pipefail
IFS=$'\n\t'

# Constants
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Helpers
log()   { echo "[$(date +%H:%M:%S)] $*" >&2; }
err()   { echo "[ERR] $*" >&2; }
fatal() { err "$*"; exit 1; }

# Cleanup
cleanup() {
    [[ -n "${tmpfile:-}" ]] && rm -f "$tmpfile"
}
trap cleanup EXIT

# Error trap
on_err() {
    err "Failed at line $1 (exit $?)"
}
trap 'on_err $LINENO' ERR
```

Note: `-E` makes `trap ERR` inherit into functions.

## When NOT to Use Strict Mode

Some scripts intentionally continue on errors:
- Best-effort cleanup
- Optional probes
- Parallel jobs

In those: handle errors explicitly.

## Operations

```bash
# Verify script syntax (no execution)
bash -n script.sh

# Debug with tracing
bash -x script.sh

# Combine
bash -nx script.sh

# Per-command tracing
set -x
problematic_line
set +x
```

## Common Mistakes

- Forgetting `set -e`
- Using `set -e` and assuming it catches all errors
- `cmd1 | cmd2 | cmd3` without pipefail (only last cmd's exit checked)
- `local var=$(failing_cmd)` — `local` masks the exit code!
  ```bash
  # WRONG
  local x=$(may_fail)    # exit code of `local` (always 0), not may_fail
  
  # RIGHT
  local x
  x=$(may_fail)          # now exit code is may_fail's
  ```

## Best Practices

- Start serious scripts with `set -Eeuo pipefail` — the `-E` makes the `ERR` trap fire inside functions and subshells.
- Pair strict mode with a cleanup `trap ... EXIT` so temp files and locks are removed on success, error, or Ctrl-C alike.
- Declare-then-assign command output (`local x; x=$(cmd)`) so the command's exit code isn't masked by `local`/`declare`.
- Make "expected" failures explicit with `cmd || true` or an `if`, so readers know the non-zero exit was intentional.
- Use meaningful exit codes (2 for usage errors, 64+ per sysexits.h) and document them; `main "$@"; exit $?` to propagate cleanly.
- Don't lean on `set -e` alone — it is suspended in conditionals, `&&`/`||` chains, and functions called as a condition; add explicit checks at critical points.

## Quick Refs

```bash
# Strict-mode header
#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

# Inspecting status
cmd; echo "$?"          # exit code of last command
echo "${PIPESTATUS[@]}" # per-stage codes of the last pipeline

# Common exit codes
# 0 ok | 1 generic | 2 usage | 126 not executable | 127 not found
# 128+N killed by signal N (130=SIGINT, 137=SIGKILL, 143=SIGTERM)

# Toggle/relax strict mode locally
set +e; risky_probe; rc=$?; set -e   # allow one command to fail
x=$(may_fail) || rc=$?               # capture instead of aborting

# Traps for cleanup and error reporting
trap 'rm -f "$tmp"' EXIT
trap 'echo "ERR line $LINENO (rc=$?)" >&2' ERR

# Debugging
bash -n script.sh        # syntax check, no run
bash -x script.sh        # trace every command
PS4='+ ${BASH_SOURCE}:${LINENO}: '   # richer xtrace prefix
```

## Interview Prep

**Junior**: "What's `set -e`?"

**Mid**: "Why use `set -euo pipefail`?"

**Senior**: "When does `set -e` NOT catch errors?"

**Staff**: "Cleanup on Ctrl-C — design."

## Next Chapter

→ [C02 — Text Processing](../C02/README.md)
