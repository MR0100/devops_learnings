# L02/C02/T02 — fork(), exec(), wait() System Calls

## Learning Objectives

- Understand how every new process on Linux is created from `fork` + `exec`
- Distinguish process *creation* (fork) from program *replacement* (exec)
- Explain copy-on-write and why `fork()` is cheap even for huge processes
- Diagnose zombies, ENOMEM-on-fork, and fork-bomb conditions in production

## The Trio

### fork()
- Clones the calling process; the child is a near-exact copy
- Returns **0 in the child**, the **child's PID in the parent**, and **-1 on failure**
- Child inherits: copy of memory (via copy-on-write), open file descriptors, environment, cwd, signal dispositions
- Child gets a *new PID*; `getppid()` returns the parent's PID
- After `fork()`, two processes diverge and run concurrently

### exec()
- Replaces the current process image with a new program — *same PID*, brand-new code/data/stack/heap
- Canonical form: `execve(path, argv[], envp[])`; libc wrappers `execl`, `execvp`, etc. resolve `$PATH`
- File descriptors survive exec unless marked close-on-exec (`O_CLOEXEC` / `FD_CLOEXEC`)
- The old code is gone on success — lines after a successful `execve` never run

### wait() / waitpid()
- Parent reaps a finished child and retrieves its exit status
- `waitpid(pid, &status, 0)` blocks; `WNOHANG` polls without blocking
- Decode status with `WIFEXITED(status)`/`WEXITSTATUS(status)` and `WIFSIGNALED(status)`/`WTERMSIG(status)`
- Until reaped, the dead child is a **zombie** holding only its PID + exit status in the process table

## The Canonical Pattern

```c
pid_t pid = fork();
if (pid == 0) {                          // ---- child ----
    char *argv[] = { "ls", "-l", NULL };
    execve("/usr/bin/ls", argv, environ);
    perror("execve");                    // only reached if exec FAILED
    _exit(127);                          // _exit, not exit: skip parent's atexit/flush
} else if (pid > 0) {                     // ---- parent ----
    int status;
    waitpid(pid, &status, 0);
    if (WIFEXITED(status))
        printf("child exited %d\n", WEXITSTATUS(status));
} else {                                  // ---- fork failed ----
    perror("fork");                       // EAGAIN (rlimit) or ENOMEM (overcommit)
}
```

Note `_exit()` in the child-after-failed-exec path: calling `exit()` would run the parent's `atexit` handlers and flush its stdio buffers a second time, double-writing output.

## Copy-on-Write (COW)

Linux does **not** physically copy memory at `fork()`. Instead it marks all the parent's pages read-only and shares them with the child. The first time *either* process writes a page, a page fault traps into the kernel, which copies just that one page and makes it writable. This means:

```
parent pages (RW) ──fork()──►  both processes share pages, now marked RO
                                        │
                               child writes page X
                                        ▼
                          page fault → kernel copies page X only
                          parent: page X (RW)   child: page X' (RW)
                          all other pages still shared
```

Consequence: forking a process using 16 GB of RAM takes microseconds and touches almost no memory — only the page tables are copied. The cost shows up later, lazily, as pages diverge.

## vfork(), posix_spawn(), clone()

| Call | Behavior | When |
|---|---|---|
| `fork()` | full COW clone | general purpose |
| `vfork()` | child borrows parent's address space, parent suspended until exec/exit | legacy micro-optimization; dangerous, rarely needed |
| `posix_spawn()` | fork+exec combined atomically (uses `clone`+`vfork` semantics internally) | launching a helper from a *huge* process to dodge overcommit failures |
| `clone()` | the real syscall under all of these; tunable sharing flags (`CLONE_VM`, `CLONE_FILES`, `CLONE_NEWNS`…) | threads and container namespaces are built on this |

Threads are just `clone()` with shared VM/files/signals. Container runtimes call `clone()` with `CLONE_NEW*` flags to create new namespaces — fork/exec and containers are the same primitive with different flags.

## Common Issues

### Fork Bomb
The classic `:(){ :|:& };:` recursively forks until PIDs and memory are exhausted, wedging the box.
- Defense: `ulimit -u <n>` (per-user process limit) and cgroup v2 `pids.max` to cap a container/slice

### Zombie Accumulation
Parent never calls `wait()`, so dead children pile up as zombies, eventually exhausting the PID table.
- Solution 1: install a `SIGCHLD` handler that loops `waitpid(-1, &st, WNOHANG)` to reap all ready children
- Solution 2: double-fork — parent waits on the first child which immediately exits, orphaning the grandchild to PID 1 (init reaps it)
- Solution 3: `signal(SIGCHLD, SIG_IGN)` — a Linux extension that auto-reaps children (they never become zombies)
- In containers, run a proper init (`tini`, `--init`) as PID 1 so orphaned children get reaped

### ENOMEM on fork from a large process
A 12 GB-heap JVM that forks to run a tiny subprocess can fail with `ENOMEM` even though COW means no copy happens. The kernel's overcommit accounting (`vm.overcommit_memory`) may *reserve* the parent's full committed size for the child and refuse the fork.
- Fixes: `posix_spawn`/`vfork` (no full address-space duplication), a tiny pre-forked helper process that does the launching, or `vm.overcommit_memory=1` (overcommit always — accept the tradeoff)

## Languages Hide This

Every "run a program" API is fork+exec underneath:

| Language / shell | API | Underlying |
|---|---|---|
| Python | `subprocess.Popen` | `posix_spawn` (3.8+) / fork+exec |
| Go | `exec.Command().Start()` | `clone`/fork + exec (with vfork-like path) |
| Node | `child_process.spawn` | `posix_spawn`/fork+exec |
| Shell | `cmd &` or `$(cmd)` | fork + execve |

Knowing the primitive explains the failure modes: leaked fds across exec (missing `O_CLOEXEC`), zombies from un-waited children, and ENOMEM from forking a giant parent.

## Common Mistakes

- Calling `exit()` instead of `_exit()` in the child after a failed exec, double-flushing stdio
- Forgetting `O_CLOEXEC`, leaking sensitive file descriptors into spawned children
- Assuming `fork()` copies memory and "optimizing" by not forking — it's already cheap via COW
- Not reaping children, accumulating zombies until PID exhaustion
- Forking from a multi-threaded process and calling non-async-signal-safe functions before exec (only `exec`/`_exit`-class calls are safe in the child)

## Best Practices

- Reap children: handle `SIGCHLD` with a `WNOHANG` reap loop, or use `posix_spawn` which integrates cleanly
- Run an init reaper (`tini`/`--init`) as PID 1 in containers
- Prefer `posix_spawn` over manual fork+exec for launching from large or multi-threaded processes
- Set `pids.max` (cgroup) and `ulimit -u` to bound fork-bomb blast radius
- Always mark fds `O_CLOEXEC` unless you intentionally pass them to the child

## Quick Refs

```bash
strace -f -e trace=clone,execve,wait4 ./myprog   # watch fork/exec/wait live
ulimit -u                                         # current per-user process cap
cat /proc/<pid>/status | grep -i threads          # thread count (clone children)
ps -eo pid,ppid,stat,cmd | awk '$3 ~ /Z/'         # list zombies (STAT contains Z)
cat /sys/fs/cgroup/<slice>/pids.max               # cgroup process limit
```

## Interview Prep

**Junior**: "What does `fork()` return?"
- 0 in the child, the child's PID in the parent, and -1 on failure — that's how each process knows which one it is.

**Mid**: "What's the difference between fork and exec?"
- `fork` creates a new process (a COW copy with a new PID); `exec` replaces the current process's program image while keeping the same PID. The shell pattern is fork to make a child, then exec to become the target program.

**Senior**: "A Java app with a 12 GB heap fails with ENOMEM when launching a small Python subprocess. Why?"
- Even with COW, the kernel's overcommit accounting can reserve the parent's full committed size for the forked child and refuse it; use `posix_spawn`/`vfork`, a small pre-forked helper, or relax `vm.overcommit_memory`.

**Staff**: "Trace exactly what happens when you type `ls` in bash."
- Bash parses the line, `fork()`s a child, the child `execve("/usr/bin/ls", ...)`, the kernel maps the ELF and hands off to `ld-linux`, which resolves and maps shared libs; `ls` runs and `exit()`s, becoming a zombie, and bash's `wait4()` reaps it and reads `$?`.

## Next Topic

→ [T03 — Signals and Signal Handling](T03-Signals.md)
