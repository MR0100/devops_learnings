# L04/C03 — Advanced Bash

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Arrays.md) | Arrays, Associative Arrays | 1 hr |
| [T02](T02-Process-Substitution-Heredocs.md) | Process Substitution, Heredocs | 0.5 hr |
| [T03](T03-Trap-Signals.md) | Trap & Signal Handling | 1 hr |
| [T04](T04-Background-Jobs.md) | Background Jobs, Job Control | 0.5 hr |
| [T05](T05-Parallel.md) | Parallel Execution (xargs -P, GNU parallel) | 1 hr |

## Arrays

```bash
# Indexed array
arr=(apple banana cherry)
echo "${arr[0]}"            # apple
echo "${arr[@]}"            # all elements
echo "${#arr[@]}"           # count
echo "${arr[@]:1:2}"        # slice from index 1, length 2

arr+=(date)                 # append
unset 'arr[1]'              # remove element

# Iterate
for item in "${arr[@]}"; do echo "$item"; done

# Read into array
mapfile -t lines < file.txt
readarray -t lines < file.txt        # same thing

# From command output
mapfile -t pods < <(kubectl get pods -o name)
```

## Associative Arrays (bash 4+)

```bash
declare -A map
map[alice]=30
map[bob]=25
echo "${map[alice]}"
echo "${!map[@]}"           # keys
echo "${map[@]}"            # values

for key in "${!map[@]}"; do
  echo "$key -> ${map[$key]}"
done
```

## Process Substitution

```bash
# Treat command output as a file
diff <(sort a.txt) <(sort b.txt)

# Capture into array
mapfile -t nodes < <(kubectl get nodes -o name)

# Two streams in one command
join <(sort users.txt) <(sort orders.txt)

# Tee multiple processes
echo "data" | tee >(grep error) >(grep warn) >/dev/null
```

## Heredocs

```bash
# Standard
cat <<EOF
Hello $USER
$(date)
EOF

# No expansion
cat <<'EOF'
Hello $USER       # literal
EOF

# Strip leading tabs (note dash)
cat <<-EOF
    indented
    text
    EOF

# To a command
ssh host <<EOF
  cd /opt/app
  ./deploy.sh
EOF
```

## Trap (Signal Handling)

```bash
cleanup() {
  echo "Cleaning up..."
  rm -f /tmp/lockfile
}

trap cleanup EXIT          # always run on exit
trap cleanup INT TERM      # specific signals
trap '' INT                # ignore Ctrl-C
trap - INT                 # restore default

# Reset trap on certain signal
trap 'echo "Got HUP"; reload_config' HUP
```

### Common Use: Lock Files / Cleanup
```bash
#!/usr/bin/env bash
set -euo pipefail

LOCKFILE=/tmp/myscript.lock

acquire_lock() {
  if ! ( set -o noclobber; echo $$ > "$LOCKFILE" ) 2>/dev/null; then
    echo "Already running (PID $(cat "$LOCKFILE"))"
    exit 1
  fi
  trap 'rm -f "$LOCKFILE"' EXIT
}

acquire_lock
# ... do work
```

## Background Jobs

```bash
long_running &           # background
echo $!                  # PID of last bg job

jobs                     # current shell's jobs
fg %1                    # bring job 1 to foreground
bg %1                    # send to background
disown %1                # remove from shell's job table
nohup cmd &              # immune to HUP, output to nohup.out

wait                     # wait for all background jobs
wait $PID                # specific PID
wait -n                  # wait for any one to finish (bash 4.3+)
```

## Parallel Execution

### xargs -P
```bash
# Process up to 8 in parallel
cat urls.txt | xargs -n 1 -P 8 curl -s

# With placeholder
find . -name "*.gz" | xargs -P 8 -I {} gunzip {}

# NUL-delimited for safety
find . -name "*.jpg" -print0 | xargs -0 -P 4 -I {} convert {} {}.png
```

### GNU parallel
More powerful than xargs:

```bash
parallel echo {} ::: a b c                # 3 jobs
parallel -j 8 'process {}' ::: file*.txt
parallel --xargs ...                      # batch many args per invocation
parallel --joblog log.txt ...
parallel --eta ...                        # progress
parallel --colsep ',' "echo a={1} b={2}" :::: data.csv
```

### Wait/concurrency pattern
```bash
MAX_JOBS=8
for item in "${items[@]}"; do
  (( $(jobs -r | wc -l) >= MAX_JOBS )) && wait -n
  process "$item" &
done
wait
```

## Coprocesses (bash 4+)

```bash
coproc PROC { bc; }                       # run bc in coprocess
echo "2+2" >&"${PROC[1]}"
read result <&"${PROC[0]}"
echo "$result"
```

Useful for two-way communication with a long-running process.

## Common Patterns

### Retry with backoff
```bash
max=5; attempt=0; delay=1
until cmd; do
  ((attempt++))
  (( attempt >= max )) && { echo failed; exit 1; }
  sleep $delay
  delay=$((delay * 2))
done
```

### Timeout
```bash
timeout 10s long_running_cmd
timeout --kill-after=5s 10s cmd       # SIGTERM after 10s, SIGKILL after 15s
```

### Atomic write
```bash
tmpfile=$(mktemp)
trap 'rm -f "$tmpfile"' EXIT
generate_content > "$tmpfile"
mv "$tmpfile" "$target"      # rename is atomic on same FS
```

## Interview Themes

- "Process 1000 files in parallel"
- "Write a script that retries with exponential backoff"
- "Handle Ctrl-C gracefully"
- "Read lines from a file safely"
- "Wait for any of N background jobs"
