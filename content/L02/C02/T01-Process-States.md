# L02/C02/T01 — Process States, PID, PPID, Process Tree

## Learning Objectives

- Identify process states from `ps` and `top`
- Use PID and PPID to navigate the process tree
- Understand the cost of context switches

## Key Concepts

### Process Identifiers
- **PID** (Process ID): unique identifier; allocated by the kernel
- **PPID** (Parent PID): the parent that forked this process
- **PGID** (Process Group ID): for job control
- **SID** (Session ID): for terminal sessions
- **TGID** (Thread Group ID): the "PID" of the main thread; multi-threaded processes share TGID

```bash
ps -eo pid,ppid,pgid,sid,user,cmd
```

### Process States (from `man ps`)

| Code | State | Notes |
|---|---|---|
| R | Running or runnable | On CPU or in run queue |
| S | Interruptible sleep | Most common; waiting for event |
| D | Uninterruptible sleep | Usually I/O wait; cannot be killed |
| T | Stopped | SIGSTOP/SIGTSTP or under ptrace |
| Z | Zombie | Dead, awaiting parent's wait() |
| X | Dead | Should never be seen |
| I | Idle kernel thread | Newer state |

Modifiers:
- `<` high priority
- `N` low priority (nice)
- `L` has pages locked in memory
- `s` session leader
- `l` multi-threaded
- `+` in foreground process group

### Process Tree

```bash
pstree                          # tree of all processes
pstree -p                       # with PIDs
pstree -pT 1234                 # tree rooted at PID 1234
ps -ejH                         # tree-like ps
ps auxf                         # tree-like ps, alt
```

## Common Tools

### `ps`
```bash
ps aux                          # BSD style
ps -ef                          # SysV style
ps -eo pid,ppid,user,%cpu,%mem,cmd  # custom columns
ps -eL                          # threads visible
ps -p 1234                      # specific PID
ps --forest                     # tree-like
```

### `top` / `htop` / `btop`
- `top` is universal; learn its keybindings (`P` cpu sort, `M` memory, `1` per-CPU)
- `htop` is more pleasant; supports filtering, killing, tree mode (`F5`)
- `btop` adds I/O and network panels

### Inspecting a Process

```bash
ls -l /proc/<pid>/exe          # the executable
cat /proc/<pid>/cmdline        # command line (NUL separated)
cat /proc/<pid>/status         # human-readable status
cat /proc/<pid>/limits         # ulimit values
ls /proc/<pid>/fd/             # open file descriptors
cat /proc/<pid>/maps           # memory map
cat /proc/<pid>/environ        # environment variables
```

## Context Switch Cost

Each context switch involves:
1. Save current process state to PCB
2. Switch page tables
3. Flush TLB (partially)
4. Load new process state
5. Resume

Cost: ~1–5 microseconds on modern CPUs. Excessive context switching (>100K/sec/CPU) suggests thread contention or scheduler thrash.

Check:
```bash
vmstat 1                       # cs column shows context switches
pidstat -w 1                   # per-process context switches
```

## Common Issues

### Lots of D-state Processes
Symptom: `top` shows many processes in `D`. Iowait high.
Cause: storage saturated, NFS hang, or runaway disk I/O.
Investigate: `iotop`, `iostat`, `dmesg`.

### High CPU With Few Processes
Likely thread contention or kernel work. Use `top -H` to see threads, `perf top` to find hot kernel functions.

### Lots of Threads
Java apps especially. Check `nproc-per-process` against system limits (`ulimit -u`, `/proc/sys/kernel/threads-max`).

## Common Mistakes

- **Reading load average as a CPU-busy gauge** — on Linux it counts runnable *and* uninterruptible (D-state) tasks, so a high load can mean stuck I/O, not a busy CPU.
- **Trying to `kill -9` a D-state process** — uninterruptible sleep ignores all signals until the syscall returns; the fix is the underlying I/O, not a bigger hammer.
- **Confusing R "running" with "on-CPU"** — R means runnable (running *or* waiting in the run queue); a high R count can just be run-queue contention.
- **Treating zombies (Z) as resource leaks** — a zombie holds only a PID slot, not memory/CPU; the bug is the parent not calling `wait()`, not the zombie itself.
- **Ignoring TGID vs PID** — tools that show threads (e.g. `top -H`, `ps -L`) inflate "process" counts; one multi-threaded process is one TGID with many PIDs.

## Best Practices

- **Start triage with state, not CPU%** — `ps -eo pid,stat,cmd` (or `top`); the STAT column tells you *why* a process isn't progressing.
- **Correlate D-state with iowait** — when D-state piles up, jump straight to `iostat -xz 1` / `iotop` and `dmesg` for the storage cause.
- **Use `top -H` / `ps -L` to see threads** before concluding "too many processes," especially for JVM and Go workloads.
- **Watch the run queue, not just utilization** — sustained `r` in `vmstat 1` greater than CPU count signals scheduling pressure even at modest CPU%.
- **Reap children** — ensure long-lived parents `wait()` (or run an init like `tini` as PID 1 in containers) so zombies never accumulate.

## Quick Refs

**Process states (the STAT letters)**

| Code | State | Note |
|---|---|---|
| `R` | Running / runnable | On CPU or in run queue |
| `S` | Interruptible sleep | Waiting on event, wakes on signal |
| `D` | Uninterruptible sleep | Usually disk/NFS; ignores signals |
| `T` | Stopped | SIGSTOP / under debugger |
| `Z` | Zombie | Exited, awaiting parent `wait()` |
| `I` | Idle kernel thread | (kernel workers) |

STAT suffixes: `<` high-priority · `N` low-priority (nice) · `s` session leader · `l` multi-threaded · `+` foreground group.

```bash
ps -eo pid,ppid,stat,etime,cmd      # states + age
top -H                              # per-thread view
vmstat 1                            # r (run queue) and b (blocked/D)
ps -eo stat | grep -c '^D'          # count D-state tasks
```

## Interview Prep

**Mid**: "What's the difference between PID and TGID?"

**Senior**: "We have a process stuck in D state and `kill -9` doesn't work. What now?"
- D state is uninterruptible — even SIGKILL won't dislodge it until the syscall completes. Investigate the I/O cause (stuck NFS, broken disk). Worst case: reboot.

**Staff**: "Walk me through the entire process tree on a typical Linux server — what owns what and why."

## Next Topic

→ [T02 — fork(), exec(), wait() System Calls](T02-Fork-Exec-Wait.md)
