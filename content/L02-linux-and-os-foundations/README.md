# L02 — Linux & Operating System Internals

## Overview

If L01 was the "why" of DevOps, L02 is the foundation under everything that follows. Every container, every VM, every pod ultimately runs on a Linux kernel. Engineers who only know the *surface* of Linux ("I use the shell sometimes") plateau at mid-level. Engineers who understand the *internals* — processes, namespaces, cgroups, memory management, the network stack — operate fluently at staff and principal levels.

This lecture has **10 chapters and 46 topics**.

## Learning Outcomes

After this lecture, you will:

1. Explain how a process is created, scheduled, and terminated at the kernel level
2. Diagram virtual memory and explain the OOM killer's decision algorithm
3. Tune CPU and I/O scheduling for production workloads
4. Build a "container" from scratch using `unshare` and cgroups
5. Diagnose Linux performance issues with `perf`, `strace`, `bpftrace`, and eBPF
6. Harden a Linux server to CIS benchmark
7. Understand systemd as a service manager *and* a system architecture
8. Operate filesystems (ext4, XFS, ZFS) under production failure modes

## Prerequisites

- Comfort with bash basics (we'll deepen this in L04)
- Basic understanding of OS concepts (processes, files)
- Access to a Linux environment (VM, container, WSL2, or native)

## Chapter Map

| # | Chapter | Topics | Hours |
|---|---|---|---|
| [C01](C01/) | Linux Fundamentals | 4 | 4 |
| [C02](C02/) | Process Management | 5 | 6 |
| [C03](C03/) | Memory Management | 5 | 5 |
| [C04](C04/) | CPU & Scheduling | 4 | 4 |
| [C05](C05/) | Filesystems & Storage | 5 | 6 |
| [C06](C06/) | Linux Networking Stack | 5 | 7 |
| [C07](C07/) | Cgroups & Namespaces (Container Foundations) | 4 | 6 |
| [C08](C08/) | Performance & Observability | 5 | 6 |
| [C09](C09/) | Linux Security | 5 | 5 |
| [C10](C10/) | Boot Process & Kernel | 4 | 3 |
| **Total** | | **46** | **52** |

## Key References

- *Linux Performance and Tuning Guidelines* (Red Hat / IBM)
- *The Linux Programming Interface* — Michael Kerrisk
- *Systems Performance: Enterprise and the Cloud* — Brendan Gregg
- *BPF Performance Tools* — Brendan Gregg
- *Linux Kernel Development* — Robert Love
- `kernel.org` documentation
- `man 7` pages (the conceptual ones — `signal`, `pipe`, `epoll`, `unix`, `socket`)

## Interview Relevance

Linux internals questions feature heavily in:
- **Google SRE/SWE interviews** — expect deep questions on memory, scheduling, syscalls
- **Meta Production Engineer** — expect kernel and networking depth
- **Amazon SDE** — expect process management and IPC questions
- **All FAANGM debugging interviews** — "this server is slow, debug it"

## How to Practice

1. Spin up a fresh Linux VM
2. For each topic, replicate the demonstrations
3. Break things on purpose (`stress`, `tc`, `iptables`) and observe
4. Use `strace`, `perf`, `bpftrace` against the breakage

## Next

→ [L03 — Networking Deep Dive](../L03-networking/README.md)
