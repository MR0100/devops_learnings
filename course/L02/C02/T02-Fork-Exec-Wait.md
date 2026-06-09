# L02/C02/T02 — fork(), exec(), wait() System Calls

## Learning Objectives

- Understand how new processes are created
- Distinguish fork from exec
- Recognize copy-on-write efficiency

## The Trio

### fork()
- Creates a copy of the calling process
- Returns 0 in child, child's PID in parent
- Child gets a copy of memory (via copy-on-write), open FDs, etc.
- After fork, two processes diverge

### exec()
- Replaces the current process image with a new program
- Same PID, new memory image, new code
- Common form: `execve(path, argv, envp)`
- The original code is gone; this is "become the new program"

### wait() / waitpid()
- Parent uses this to reap a finished child
- Returns child's exit status
- Until reaped, child is a zombie

## The Pattern

Most program-launching code in Unix is:

```c
pid_t pid = fork();
if (pid == 0) {
    // child
    execve("/usr/bin/ls", argv, envp);
    perror("exec failed");  // only reached on failure
    _exit(1);
} else if (pid > 0) {
    // parent
    int status;
    waitpid(pid, &status, 0);
} else {
    // fork failed
}
```

## Copy-on-Write (COW)

Modern Linux doesn't actually copy memory at fork. Pages are marked read-only and shared; only when a page is written does a real copy happen.

This means `fork()` is **cheap** — even for a process using 4 GB of RAM, fork takes microseconds (no actual copying).

## vfork() and posix_spawn()

- `vfork()` is older optimization; child runs in parent's address space until exec. Rarely needed now.
- `posix_spawn()` combines fork+exec atomically — useful in real-time contexts.

## Common Issues

### Too Many Forks (Fork Bomb)
The classic `:(){ :|:& };:` — recursive forks consume PIDs and memory. Defense: `ulimit -u`, cgroup pid limits.

### Zombie Accumulation
Parent forgets to wait → zombies accumulate.
- Solution 1: handle SIGCHLD, call wait
- Solution 2: double-fork (parent waits on first child, who exits, leaving grandchild orphaned to init)
- Solution 3: `signal(SIGCHLD, SIG_IGN)` — kernel auto-reaps (Linux extension)

### Memory Pressure from Fork
A 16 GB Java process forking to run a small subprocess can fail under low memory due to overcommit settings (even with COW, kernel may refuse). Use `posix_spawn` or pre-fork helper process.

## Languages Hide This

- Python `subprocess.Popen` → fork+exec
- Go `exec.Command().Start()` → fork+exec
- Shell `&` → fork+exec
- Node `child_process.spawn` → fork+exec

But knowing the underlying call helps when debugging.

## Interview Prep

**Mid**: "What does fork() return?"

**Senior**: "We have a Java app with 12 GB heap. It needs to launch a small Python subprocess but fails with ENOMEM. Why?"
- Even COW fork temporarily commits the heap size. Overcommit settings or `posix_spawn` fix this.

**Staff**: "Trace what happens when you type `ls` in bash."
- Shell parses → fork → child execve("/usr/bin/ls") → kernel loads ELF → ld-linux maps libs → ls runs → exits → parent's wait reaps.

## Next Topic

→ [T03 — Signals and Signal Handling](T03-Signals.md)
