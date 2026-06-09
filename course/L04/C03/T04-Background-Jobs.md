# L04/C03/T04 — Background Jobs, Job Control

## Learning Objectives

- Run jobs in background
- Wait for and manage jobs
- Use job control in scripts

## Background Execution

```bash
long_command &              # background; returns immediately
echo $!                     # PID of last background job
jobs                        # list jobs in current shell
fg %1                       # bring job 1 to foreground
bg %1                       # resume stopped job in background
disown %1                   # remove from job table (no SIGHUP on exit)
nohup cmd &                 # immune to SIGHUP; output to nohup.out
```

## wait

Block until background jobs complete.

```bash
cmd1 &
cmd2 &
cmd3 &

wait                        # wait for ALL
wait $PID                   # specific job
wait -n                     # wait for ANY one to finish (bash 4.3+)
```

`wait $!` waits for last backgrounded.

## Parallel Pattern

```bash
for url in "${urls[@]}"; do
    curl -O "$url" &
done
wait                        # wait for all downloads
echo "all done"
```

## Bounded Parallelism

Limit concurrent background jobs:

```bash
MAX=8
for item in "${items[@]}"; do
    while (( $(jobs -r | wc -l) >= MAX )); do
        wait -n              # wait for any one to finish
    done
    process "$item" &
done
wait                         # final wait
```

Maintains exactly `MAX` running.

## Wait with Exit Code

```bash
pids=()
for x in a b c; do
    cmd "$x" &
    pids+=("$!")
done

failed=0
for pid in "${pids[@]}"; do
    if ! wait "$pid"; then
        ((failed++))
    fi
done

echo "$failed failed"
```

Tracks per-job success.

## nohup

Decouple from terminal:
```bash
nohup long_running.sh > out.log 2>&1 &
```

Survives terminal close. Logs to nohup.out by default.

## Disown

Remove job from shell's job table. After `disown`, the shell won't send SIGHUP on exit.

```bash
cmd &
disown %1
exit                         # cmd keeps running
```

## Job Control in Scripts

`set -m` enables job control in scripts:
```bash
set -m       # enable job control
cmd &
jobs %1
```

Often not needed; scripts handle differently.

## Async / Sync Patterns

### Fire and Forget
```bash
fire_and_forget &
disown
```

### Parallel with Aggregated Result
```bash
results=()
pids=()

for x in "${items[@]}"; do
    (process "$x"; echo "result: $x") &
    pids+=("$!")
done

for pid in "${pids[@]}"; do
    wait "$pid"
done
```

### Timeout
```bash
timeout 30 long_cmd
timeout --kill-after=10 30 long_cmd    # SIGTERM at 30s; SIGKILL at 40s
```

## Stopping a Job

```bash
# Foreground: Ctrl-Z stops (SUSPENDED)
fg                         # resume in foreground
bg                         # resume in background

# Specific job
kill %1                    # SIGTERM
kill -9 %1                 # SIGKILL
```

## Process Substitution + Background

```bash
big_processing | tee >(grep -c ERROR > errors) > /dev/null
wait                       # wait for tee's children
```

## Real-World Patterns

### Parallel API Calls
```bash
for endpoint in "${endpoints[@]}"; do
    {
        result=$(curl -s "$endpoint")
        echo "$endpoint: $result" >> results.log
    } &
done
wait
```

### Parallel SSH
```bash
for host in "${hosts[@]}"; do
    ssh "$host" "uptime" >> outputs.log &
done
wait
```

For more hosts: use parallel-ssh, ansible, or GNU parallel.

### Background with Logging
```bash
long_task > /var/log/task.log 2>&1 &
echo $! > /var/run/task.pid
```

## Async Coordination

Use named FIFOs for inter-process communication:
```bash
mkfifo /tmp/queue
producer > /tmp/queue &
consumer < /tmp/queue &
wait
```

## Common Issues

- **Forgotten wait**: script exits while background jobs still running
- **Variables in background**: child can't modify parent's vars
- **PID reused**: race conditions in long-lived scripts
- **No error handling**: background failures silent without wait check
- **Output races**: multiple jobs writing to same file → interleaved garbage

## Output Buffering

When piping background output:
```bash
cmd1 &
cmd2 &
# Both write to stdout — may interleave
```

Mitigation: write to separate files; combine after.

## set -m vs Set +m

```bash
set +m       # disable job control (default in scripts)
set -m       # enable (gives interactive-style job tracking)
```

## Process Group / Session

Each backgrounded process gets:
- Its own process group
- Same session as parent (until disown / nohup)

`kill -TERM -PGID` kills entire group.

## Interview Prep

**Mid**: "Run 5 things in parallel and wait."

**Senior**: "Bounded parallelism — max 8 at a time."

**Staff**: "Track per-job success across 100 parallel SSHs."

## Next Topic

→ [T05 — Parallel Execution (xargs -P, GNU parallel)](T05-Parallel.md)
