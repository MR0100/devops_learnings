# L02/C02/T04 — Zombie, Orphan, Daemon Processes

## Learning Objectives

- Distinguish zombie, orphan, and daemon processes
- Recognize and fix accumulation issues
- Daemonize a process correctly

## Zombie Processes

A zombie is a process that has **exited** but has not been **reaped** by its parent via `wait()`.

- It occupies a PID slot but no other resources (no memory, no CPU)
- Shows in `ps` as `Z` state
- Cleanup happens when parent calls `wait()` or when parent exits (then init/systemd reaps)

### Why You'd Care
- A few zombies are harmless; thousands exhaust the PID table
- Symptoms: `fork: cannot allocate memory` even with free memory

### Diagnosing
```bash
ps -eo pid,ppid,state,cmd | awk '$3=="Z"'
```

### Fixing
- Parent should `wait()` after `fork()`
- Or `signal(SIGCHLD, SIG_IGN)` to tell kernel to auto-reap (Linux)
- In containers: use `tini` / `dumb-init` as PID 1

## Orphan Processes

An orphan is a process whose **parent died first**.

- The kernel reparents orphans to **PID 1** (init/systemd)
- PID 1 must reap them when they exit

### Why You'd Care
- Useful: daemonization technique uses orphaning
- Problem: if PID 1 doesn't reap (poorly-written entrypoint), orphans become zombies

## Daemon Processes

A daemon is a background process:
- Detached from a controlling terminal
- Re-parented to init
- Often runs services (sshd, nginx, postgresd)

### Old-School Daemonization (steps)
1. fork() → child
2. parent exits → child orphaned
3. setsid() → new session (detach from terminal)
4. fork() again (prevent acquiring a controlling terminal)
5. chdir("/") — don't hold a mount busy
6. umask(0) — control file creation mode
7. Close stdin/stdout/stderr, redirect to /dev/null or log file

### Modern Daemonization

**Don't.** Let systemd handle it:

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My Application

[Service]
ExecStart=/usr/local/bin/myapp
Restart=on-failure
User=myapp

[Install]
WantedBy=multi-user.target
```

The app stays in the foreground; systemd manages backgrounding.

## Containers Don't Daemonize

In a container, your app should run in the **foreground** as PID 1. The container runtime handles "backgrounding". Daemonizing inside a container breaks logging, signals, and the lifecycle.

## Common Production Issues

### Container PID 1 Not Reaping
Symptom: zombies pile up in a long-running container.
Cause: app at PID 1 doesn't reap zombies from subprocesses (e.g., `bash` doing pipes).
Fix: `tini` / `dumb-init`:

```dockerfile
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y tini
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["./myapp"]
```

### Java Subprocess Zombies
Java's `Runtime.exec()` returns a `Process` object; if you don't call `waitFor()` or close streams, you get zombies. Use `ProcessBuilder` and reap properly.

### Daemonization in Containers
Don't do it. Ensure your container's CMD/ENTRYPOINT keeps PID 1 in the foreground.

## Common Mistakes

- **Thinking zombies consume memory/CPU** — a zombie holds only a PID-table slot; the real risk is PID exhaustion, and the real bug is a parent that never reaps.
- **Forgetting that orphans re-parent to PID 1** — an orphan isn't "lost"; init adopts it and reaps it, which is exactly why a container's PID 1 must reap.
- **Daemonizing inside a container** — double-forking breaks logging, signal delivery, and the runtime's lifecycle; the app should stay in the foreground.
- **Using a non-reaping PID 1** — `bash` or a language runtime as PID 1 that doesn't reap lets zombies from subprocesses accumulate until `fork()` fails with ENOMEM (really EAGAIN/PID limit).
- **Calling `Runtime.exec()` / spawning subprocesses without waiting** — in Java, Python, etc., not consuming the child's exit status leaves zombies behind.

## Best Practices

- **Always reap children** — call `wait()`/`waitpid()`, use `ProcessBuilder` + `waitFor()` in Java, or `subprocess` with `.wait()`/context managers in Python.
- **Run a real init as container PID 1** — `tini`/`dumb-init` (or `docker run --init`) reaps orphaned zombies and forwards signals for you.
- **Keep the app in the foreground** — let the container runtime do the "backgrounding"; never daemonize.
- **Monitor PID-table health** — alert on zombie count and on `nr_threads` / PID usage approaching `kernel.pid_max`.
- **For classic daemons, prefer systemd** over hand-rolled double-fork — it handles forking, supervision, and reaping correctly (`Type=notify`/`forking`).

## Quick Refs

| Term | What it is | Reaped by |
|---|---|---|
| **Zombie (Z)** | Exited child whose status hasn't been collected | Parent calling `wait()` |
| **Orphan** | Child whose parent died first | PID 1 (re-parented + reaped) |
| **Daemon** | Detached background service | Its supervisor (systemd) |

```bash
ps -eo pid,ppid,stat,cmd | awk '$3 ~ /Z/'   # list zombies
ps -eo stat | grep -c '^Z'                  # count zombies
cat /proc/sys/kernel/pid_max                # PID ceiling

# Reap zombies in a container — run an init as PID 1
ENTRYPOINT ["/usr/bin/tini", "--"]          # Dockerfile
docker run --init myimage                   # or via the runtime flag
```

**Rule**: zombies waste PIDs, not RAM. A pile of them means PID 1 (or a parent) isn't reaping.

## Interview Prep

**Junior**: "What's a zombie process?"

**Mid**: "How do you reap zombies in a container?"

**Senior**: "Production fork() calls are failing with ENOMEM. We have 30 GB free. What's wrong?"
- Probably PID exhaustion. Check `/proc/sys/kernel/pid_max` and zombie count.

## Next Topic

→ [T05 — systemd Deep Dive](T05-Systemd.md)
