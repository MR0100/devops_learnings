# L04/C03/T05 — Parallel Execution (xargs -P, GNU parallel)

## Learning Objectives

- Use xargs -P for parallelism
- Compare GNU parallel
- Choose right tool

## xargs -P

xargs runs commands with arguments from stdin. `-P N` runs up to N in parallel.

```bash
# Sequential (default)
ls *.log | xargs gzip

# 8 parallel
ls *.log | xargs -n 1 -P 8 gzip

# One arg per call, 4 parallel
find . -name "*.json" | xargs -n 1 -P 4 jq .
```

`-n 1` ensures one arg per invocation (not batched).

## NUL Delimiter (Safe for Spaces)

Always for filenames:
```bash
find . -name "*.log" -print0 | xargs -0 -P 8 -I {} gzip {}
```

`-print0` + `-0` use NUL separator. Survives filenames with spaces, quotes, newlines.

## Placeholders

```bash
# -I {} replaces {} with each arg
ls *.txt | xargs -I {} cp {} backup/{}.bak

# Default: appends arg at end of command
ls *.txt | xargs ls -la       # arg at end
```

## GNU parallel

More flexible; sometimes pre-installed.

```bash
# Same as xargs -P
ls *.log | parallel -j 8 gzip

# With placeholder
parallel -j 8 gzip ::: *.log

# Multiple input sources
parallel echo {1} {2} ::: a b c ::: 1 2 3
# Outputs: a 1, a 2, a 3, b 1, b 2, b 3, c 1, c 2, c 3
```

## Real Examples

### Convert Images
```bash
find . -name "*.png" -print0 | xargs -0 -P 4 -I {} convert {} {}.jpg
```

### Test Many Endpoints
```bash
cat urls.txt | xargs -n 1 -P 16 -I {} curl -s -o /dev/null -w '%{http_code} {}\n' {}
```

### Parallel Tar
```bash
ls dir-*/ | xargs -n 1 -P 4 -I {} tar czf {}.tar.gz {}
```

### Find and Process
```bash
find /var/log -name "*.gz" -print0 | xargs -0 -P 8 -I {} zgrep -l "ERROR" {}
```

## GNU parallel Features

### Progress Bar
```bash
parallel --bar -j 8 process ::: "${items[@]}"
```

### ETA
```bash
parallel --eta -j 8 ...
```

### Job Log
```bash
parallel --joblog jobs.log -j 8 ...
```

Records: start time, run time, exit code per job. Resume failed:
```bash
parallel --joblog jobs.log --resume-failed -j 8 ...
```

### Different Args per Call
```bash
parallel echo {1} {2} :::: hosts.txt :::: actions.txt
```

### Distributed (Multi-Machine)
```bash
parallel --slf hosts.txt --workdir /tmp 'process {}' ::: files/*
```

`--slf` (slot list file) distributes across SSH machines.

## When Which Tool

| Need | Tool |
|---|---|
| Simple parallel xargs | `xargs -P` (ubiquitous) |
| Many args + complex placeholders | GNU parallel |
| Distributed across machines | parallel `--slf` |
| Progress + logging | parallel |
| Most portable / minimal deps | xargs (built-in) |

## Bash Native (No Tools)

```bash
MAX=8
for x in "${items[@]}"; do
    while (( $(jobs -r | wc -l) >= MAX )); do
        wait -n
    done
    process "$x" &
done
wait
```

Useful when xargs / parallel not available.

## Common Patterns

### Compile Many Files
```bash
ls *.c | xargs -n 1 -P "$(nproc)" gcc -c
```

`$(nproc)` gives CPU count.

### Parallel API Health Checks
```bash
cat services.txt | xargs -n 1 -P 20 -I {} sh -c 'curl -s -o /dev/null -w "%{http_code} {}\n" "{}"'
```

### Process Pool with Limit
```bash
# 4 workers, queue from list
parallel -j 4 -a tasks.txt 'process {}'
```

## Output Ordering

By default, output may interleave (multiple workers writing to same stdout).

GNU parallel preserves order with `--keep-order`:
```bash
parallel -j 8 --keep-order curl {} ::: "${urls[@]}"
```

xargs doesn't have this; pipe to sort if needed.

## Limits

### CPU
Number of parallel workers ≈ CPU cores. More doesn't help CPU-bound.

### I/O
For I/O-bound (network, disk): more parallel can help (up to 4-8× cores).

### Memory
Each worker uses memory. Watch total.

## Error Handling

xargs continues by default on individual failures:
```bash
xargs -P 8 ... | tee log.txt
echo "Exit: $?"            # may be 0 even if some failed
```

For strict mode:
```bash
xargs -P 8 ... || echo "some failed"
```

GNU parallel:
```bash
parallel --halt soon,fail=1 ...      # stop on first failure
parallel --halt now,fail=10% ...     # stop if 10% fail
```

## Performance Tips

- `LC_ALL=C` for ASCII-only locale (faster string ops)
- Avoid spawning shell per task: use `-I {}` carefully
- For lots of small tasks: bundle work into bigger chunks

## Operations

```bash
# Process count
nproc

# Available memory
free -m

# Watch system load while running
watch -n 1 'uptime; jobs | wc -l'
```

## Interview Prep

**Junior**: "Process 1000 files in parallel."

**Mid**: "Test 100 URLs and collect HTTP codes."

**Senior**: "Bounded parallelism with retry on failure."

**Staff**: "Distribute work across 10 SSH machines."

## Next Chapter

→ [C04 — Production-Grade Scripts](../C04/README.md)
