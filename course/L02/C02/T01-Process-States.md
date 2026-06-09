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

## Interview Prep

**Mid**: "What's the difference between PID and TGID?"

**Senior**: "We have a process stuck in D state and `kill -9` doesn't work. What now?"
- D state is uninterruptible — even SIGKILL won't dislodge it until the syscall completes. Investigate the I/O cause (stuck NFS, broken disk). Worst case: reboot.

**Staff**: "Walk me through the entire process tree on a typical Linux server — what owns what and why."

## Next Topic

→ [T02 — fork(), exec(), wait() System Calls](T02-Fork-Exec-Wait.md)
