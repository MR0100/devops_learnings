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

## Interview Prep

**Junior**: "What's a zombie process?"

**Mid**: "How do you reap zombies in a container?"

**Senior**: "Production fork() calls are failing with ENOMEM. We have 30 GB free. What's wrong?"
- Probably PID exhaustion. Check `/proc/sys/kernel/pid_max` and zombie count.

## Next Topic

→ [T05 — systemd Deep Dive](T05-Systemd.md)
