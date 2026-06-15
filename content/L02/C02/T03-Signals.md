# L02/C02/T03 — Signals and Signal Handling

## Learning Objectives

- Master common signals and when to use each
- Understand how containers handle signals
- Write code that handles SIGTERM gracefully

## The Common Signals

| Signal | Num | Default | Catchable | Use |
|---|---|---|---|---|
| SIGHUP | 1 | Terminate | Yes | Config reload (convention) |
| SIGINT | 2 | Terminate | Yes | Ctrl-C |
| SIGQUIT | 3 | Core dump | Yes | Ctrl-\ |
| SIGKILL | 9 | Terminate | **No** | Force kill |
| SIGTERM | 15 | Terminate | Yes | Polite stop (default kill) |
| SIGSTOP | 19 | Stop | **No** | Pause process |
| SIGCONT | 18 | Resume | Yes | Resume stopped |
| SIGUSR1 | 10 | Terminate | Yes | App-defined |
| SIGUSR2 | 12 | Terminate | Yes | App-defined |
| SIGCHLD | 17 | Ignore | Yes | Child changed state |
| SIGPIPE | 13 | Terminate | Yes | Write to closed pipe |
| SIGSEGV | 11 | Core dump | Yes | Bad memory access |

`SIGKILL` (9) and `SIGSTOP` (19) cannot be caught, blocked, or ignored.

## Sending Signals

```bash
kill 1234              # SIGTERM (default)
kill -9 1234           # SIGKILL
kill -15 1234          # SIGTERM (explicit)
kill -HUP 1234         # SIGHUP
killall -HUP nginx     # by name
pkill -USR1 -f myapp   # by command pattern
```

## Handling Signals (C)

```c
#include <signal.h>
void handle_term(int sig) {
    // do cleanup
    exit(0);
}
int main() {
    signal(SIGTERM, handle_term);
    // ... main loop
}
```

## Handling Signals (Python)

```python
import signal, sys
def handle_term(signum, frame):
    print("Shutting down...")
    sys.exit(0)
signal.signal(signal.SIGTERM, handle_term)
```

## Handling Signals (Go)

```go
sig := make(chan os.Signal, 1)
signal.Notify(sig, syscall.SIGTERM, syscall.SIGINT)
go func() {
    <-sig
    cancelFunc()
}()
```

## Graceful Shutdown Pattern

```
Receive SIGTERM
    ↓
Stop accepting new requests (close listener)
    ↓
Wait for in-flight requests with timeout (e.g., 30s)
    ↓
Drain connections
    ↓
Close DB pools, flush metrics
    ↓
Exit 0
```

## Signals in Containers

### Docker
- `docker stop` sends SIGTERM, waits 10s (default), then SIGKILL
- `docker kill` sends SIGKILL by default
- `STOPSIGNAL` in Dockerfile changes the default

### Kubernetes
- `preStop` hook runs first (HTTP or exec)
- Then SIGTERM to PID 1
- `terminationGracePeriodSeconds` (default 30) before SIGKILL

### The PID 1 Problem

The first process in a container has PID 1. PID 1:
- Doesn't get default signal handlers from kernel — must explicitly handle SIGTERM
- Is responsible for reaping zombies

Common mistake: a shell wrapper script runs your app. Shell doesn't propagate signals to the child. Use `exec` in shell wrappers:

```bash
#!/bin/sh
# WRONG: shell stays alive, swallows signals
./myapp

# RIGHT: replace shell with myapp
exec ./myapp
```

Or use `tini` / `dumb-init` as PID 1:

```dockerfile
ENTRYPOINT ["tini", "--", "./myapp"]
```

## Signal-Driven Behaviors (Conventions)

- `nginx -s reload` → SIGHUP triggers graceful config reload
- `kill -USR1 dd` → progress report
- `kill -USR2 nginx` → upgrade binary (zero downtime)
- `kill -QUIT java` → thread dump

## Common Mistakes

- **Letting a shell wrapper be PID 1** — `sh -c './app'` doesn't forward SIGTERM, so the app never shuts down gracefully; use `exec ./app` or an init.
- **Forgetting PID 1 has no default handlers** — the kernel won't kill PID 1 on an unhandled SIGTERM, so an unprepared PID 1 just ignores `docker stop` until SIGKILL.
- **Doing real work inside a signal handler** — handlers run async; only async-signal-safe operations are allowed. Set a flag/pipe and act in the main loop.
- **Trapping SIGKILL or SIGSTOP** — they cannot be caught, blocked, or ignored; designing a "graceful" path around SIGKILL is futile.
- **Assuming the grace period is enough** — if shutdown takes longer than `terminationGracePeriodSeconds` (default 30s) or `docker stop`'s 10s, the process is SIGKILLed mid-flight.

## Best Practices

- **Handle SIGTERM explicitly** — drain in-flight requests, stop accepting new ones, flush, then exit; treat SIGTERM as "begin graceful shutdown."
- **Run an init as PID 1 in containers** (`tini`/`dumb-init`, or `--init`) so signals propagate and zombies are reaped.
- **Use `exec` in entrypoint scripts** so your app replaces the shell and receives signals directly.
- **Match grace periods to drain time** — set `terminationGracePeriodSeconds` / `docker stop -t` larger than your worst-case graceful shutdown.
- **Use a `preStop` hook for connection draining** in Kubernetes (e.g., sleep to let endpoints depropagate) before SIGTERM reaches the app.
- **Keep handlers tiny** — flip an atomic flag or write to a self-pipe; do the heavy lifting in normal code.

## Quick Refs

**Common signals**

| Signal | # | Default | Catchable? | Typical use |
|---|---|---|---|---|
| SIGHUP | 1 | terminate | yes | reload config (`nginx -s reload`) |
| SIGINT | 2 | terminate | yes | Ctrl-C |
| SIGQUIT | 3 | core dump | yes | thread dump (JVM) |
| SIGKILL | 9 | terminate | **no** | force kill, last resort |
| SIGTERM | 15 | terminate | yes | polite shutdown (default `kill`) |
| SIGSTOP | 19 | stop | **no** | pause process |
| SIGCONT | 18 | continue | yes | resume |
| SIGUSR1/2 | 10/12 | terminate | yes | app-defined |

```bash
kill -TERM <pid>        # or just: kill <pid>
kill -l                 # list signal names/numbers
pkill -HUP nginx        # by name
trap 'cleanup' TERM INT # shell handler

# container defaults
docker stop             # SIGTERM, 10s grace, then SIGKILL
# k8s: preStop -> SIGTERM -> terminationGracePeriodSeconds -> SIGKILL
```

**Rule**: SIGKILL(9) and SIGSTOP(19) are uncatchable. Always try SIGTERM first.

## Interview Prep

**Mid**: "What's the difference between SIGTERM and SIGKILL?"

**Senior**: "Your app doesn't shut down gracefully when K8s rolls it. What do you check?"
- PID 1 (shell wrapper), terminationGracePeriodSeconds, preStop hook, in-flight request handling.

**Staff**: "Design a graceful shutdown protocol for a long-lived WebSocket server with 10K connections."

## Next Topic

→ [T04 — Zombie, Orphan, Daemon Processes](T04-Zombie-Orphan-Daemon.md)
