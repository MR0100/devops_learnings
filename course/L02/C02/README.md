# L02/C02 — Process Management

## Chapter Overview

Processes are how Linux runs everything. Understanding the lifecycle, signals, and systemd is foundational for debugging and operations.

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Process-States.md) | Process States, PID, PPID, Process Tree | 1 hr |
| [T02](T02-Fork-Exec-Wait.md) | fork(), exec(), wait() System Calls | 1.5 hr |
| [T03](T03-Signals.md) | Signals and Signal Handling | 1 hr |
| [T04](T04-Zombie-Orphan-Daemon.md) | Zombie, Orphan, Daemon Processes | 1 hr |
| [T05](T05-Systemd.md) | systemd Deep Dive (Units, Targets, Journal) | 2 hr |

## Learning Outcomes

- Diagram a process lifecycle from `fork()` to exit
- Explain what state each `ps` letter represents
- Write a signal handler in C
- Diagnose zombie processes
- Author a production-quality systemd unit file

## Key Diagrams

### Process Lifecycle

```
parent ──fork()──► child (copy of parent)
                    │
                    │ exec() — replace memory image
                    ▼
                  new program
                    │
                    │ exit()
                    ▼
                  zombie (waiting for parent to wait())
                    │
                    │ parent's wait() reaped
                    ▼
                  gone
```

### Process States

| State | Code | Meaning |
|---|---|---|
| Running | R | On CPU or ready to run |
| Sleeping (interruptible) | S | Waiting (can be woken by signal) |
| Uninterruptible sleep | D | Waiting on I/O, cannot be killed |
| Stopped | T | SIGSTOP'd or under tracer |
| Zombie | Z | Dead but not reaped |

### Process Tree

```
init/systemd (PID 1)
├── sshd
│   └── bash (yours)
│       └── vim
└── nginx (master)
    ├── nginx (worker 1)
    ├── nginx (worker 2)
    └── nginx (worker 3)
```

## Why systemd Matters

systemd isn't just an init system — it's a service manager, log aggregator (journald), DNS resolver (resolved), network manager (networkd), and more. Every Linux DevOps engineer needs deep systemd familiarity.

## Interview Themes

- Diagnose zombie processes
- Write a systemd unit for a Python web app
- Explain signal handling under load
- Describe what happens when PID 1 dies
