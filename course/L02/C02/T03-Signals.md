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

## Interview Prep

**Mid**: "What's the difference between SIGTERM and SIGKILL?"

**Senior**: "Your app doesn't shut down gracefully when K8s rolls it. What do you check?"
- PID 1 (shell wrapper), terminationGracePeriodSeconds, preStop hook, in-flight request handling.

**Staff**: "Design a graceful shutdown protocol for a long-lived WebSocket server with 10K connections."

## Next Topic

→ [T04 — Zombie, Orphan, Daemon Processes](T04-Zombie-Orphan-Daemon.md)
