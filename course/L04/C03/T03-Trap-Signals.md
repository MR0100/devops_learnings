# L04/C03/T03 — Trap & Signal Handling

## Learning Objectives

- Trap signals for cleanup
- Implement graceful shutdown
- Use trap ERR for debugging

## Trap Basics

```bash
trap 'command' SIGNAL [SIGNAL ...]

trap 'echo cleanup' EXIT
trap 'echo got SIGTERM' TERM
trap '' INT            # ignore Ctrl-C
trap - INT             # restore default
```

## Common Signals

- `EXIT` — script exits (any reason)
- `INT` — Ctrl-C (SIGINT)
- `TERM` — SIGTERM (kill default)
- `HUP` — SIGHUP (terminal closed; config reload convention)
- `QUIT` — Ctrl-\ (SIGQUIT)
- `USR1` / `USR2` — app-defined
- `ERR` — any command exits nonzero (bash extension)
- `DEBUG` — before every command

## Cleanup Pattern

```bash
tmpfile=$(mktemp)
trap 'rm -f "$tmpfile"' EXIT

# Use tmpfile; auto-removed on exit
echo "data" > "$tmpfile"
```

`EXIT` fires regardless of how script ends: normal, error, signal.

## Multiple Cleanups

```bash
cleanups=()

add_cleanup() {
    cleanups+=("$1")
}

run_cleanups() {
    for c in "${cleanups[@]}"; do
        eval "$c" || true
    done
}

trap run_cleanups EXIT

tmpfile=$(mktemp)
add_cleanup "rm -f $tmpfile"

mkdir mydir
add_cleanup "rmdir mydir"

# work happens; cleanups run automatically
```

## ERR Trap

Catches any unhandled error.

```bash
on_err() {
    local rc=$? line=$1
    echo "ERROR at line $line, exit code $rc" >&2
    exit $rc
}
trap 'on_err $LINENO' ERR
```

Combine with `set -e` for robust error handling.

`-E` makes traps inherit into functions/subshells:
```bash
set -E
trap '...' ERR
```

## DEBUG Trap

Runs before every command. Use sparingly.

```bash
trap 'echo "DEBUG: $BASH_COMMAND"' DEBUG
# runs before each command echo'd
```

Useful for tracing complex scripts.

## Signal Handling Pattern

```bash
shutdown() {
    echo "shutting down..."
    kill -TERM "$child_pid" 2>/dev/null
    wait "$child_pid"
    exit 0
}

trap shutdown INT TERM

long_running_command &
child_pid=$!
wait "$child_pid"
```

Forwards signal to child. Useful for wrapping commands in containers.

## Real Example: PID 1 Wrapper

```bash
#!/bin/bash
# init.sh — minimal PID 1 in container

set -e

forward_signal() {
    kill -s "$1" "$child" 2>/dev/null
    wait "$child"
    exit $?
}

trap 'forward_signal TERM' TERM
trap 'forward_signal INT' INT
trap 'forward_signal QUIT' QUIT

"$@" &
child=$!
wait "$child"
```

Sets up signal forwarding so the actual process gets signals.

## Lock File via Trap

```bash
LOCK=/var/run/myscript.lock

acquire() {
    if ! ( set -o noclobber; echo $$ > "$LOCK" ) 2>/dev/null; then
        echo "Already running (PID $(cat "$LOCK"))"
        exit 1
    fi
    trap 'rm -f "$LOCK"' EXIT
}

acquire
# critical section
```

`set -o noclobber` makes `>` fail if file exists; atomic check-and-create.

## Subshell Considerations

Traps don't inherit by default:
```bash
trap 'echo parent EXIT' EXIT

(
    # subshell — own trap
    trap 'echo subshell EXIT' EXIT
    exit
)
# subshell EXIT printed; then parent EXIT
```

Use `set -E` for ERR inheritance.

## Reset Trap

```bash
trap - EXIT             # remove EXIT trap
trap '' INT             # ignore (still set)
```

## Trap Order

Multiple traps for same signal: latest replaces.
```bash
trap 'cleanup1' EXIT
trap 'cleanup2' EXIT     # only cleanup2 runs
```

To compose: chain them in one handler.

## Debugging

```bash
# What traps are set?
trap

# Detailed
trap -p
```

## Common Patterns

### Trap with State
```bash
running=true

stop() {
    running=false
}
trap stop INT TERM

while $running; do
    do_work
    sleep 1
done
```

Allows clean exit from infinite loop on signal.

### Graceful Shutdown
```bash
trap 'echo "Stopping..."; kill -TERM $child; wait $child; exit 0' TERM

slow_process &
child=$!
wait
```

## Signal Numbers

```bash
kill -9 PID            # SIGKILL (cannot trap)
kill -15 PID           # SIGTERM
kill -1 PID            # SIGHUP

# Show all
kill -l
```

`SIGKILL` (9) and `SIGSTOP` (19) cannot be caught.

## Real Use: Cleanup on Crash

```bash
#!/bin/bash
set -e
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

# work in $tmp; auto-cleaned
process "$tmp"
```

## Interview Prep

**Mid**: "Cleanup temp files even on error."

**Senior**: "Forward signals from wrapper to child."

**Staff**: "Lock file with PID; trap-based cleanup."

## Next Topic

→ [T04 — Background Jobs, Job Control](T04-Background-Jobs.md)
