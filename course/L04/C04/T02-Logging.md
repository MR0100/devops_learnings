# L04/C04/T02 — Logging, Stderr vs Stdout, Tee

## Learning Objectives

- Separate logs from program output
- Structure logs in scripts
- Use tee effectively

## Stdout vs Stderr

- **stdout (FD 1)**: program output (data the caller wants)
- **stderr (FD 2)**: progress, warnings, errors (logs)

```bash
echo "result"           # stdout
echo "[INFO] working" >&2   # stderr
```

### Rule
> Never log to stdout. If the script also outputs data, mixing breaks pipelines.

## Redirection

```bash
cmd > output.txt           # stdout to file
cmd 2> errors.txt          # stderr to file
cmd > out 2>&1             # stdout AND stderr to out
cmd &> all.log             # both (bash shorthand)
cmd >> append.log          # append
cmd > /dev/null            # discard stdout
cmd 2> /dev/null           # discard stderr
cmd > /dev/null 2>&1       # discard all
```

## Order Matters!

```bash
cmd > out 2>&1             # first stdout to out; then stderr → same fd → out
cmd 2>&1 > out             # stderr to original stdout (terminal); stdout to out
```

`2>&1` duplicates current stdout target. Order matters.

## tee

Write to file AND stdout.

```bash
cmd | tee log.txt          # see + save
cmd | tee -a log.txt       # append
cmd 2>&1 | tee log.txt     # capture both
cmd |& tee log.txt         # bash 4: same as above

# Multiple files
cmd | tee log1.txt log2.txt

# Write privileged
echo "data" | sudo tee /etc/file
```

## Logging Helpers

```bash
log()   { echo "[$(date +%H:%M:%S)] $*" >&2; }
info()  { echo "[INFO]  $*" >&2; }
warn()  { echo "[WARN]  $*" >&2; }
err()   { echo "[ERROR] $*" >&2; }
fatal() { err "$*"; exit 1; }

log "starting"
warn "disk getting full"
err "could not connect"
```

## With Levels

```bash
LOG_LEVEL=${LOG_LEVEL:-INFO}

debug() {
    [[ "$LOG_LEVEL" == "DEBUG" ]] && echo "[DEBUG] $*" >&2
}
info() {
    [[ "$LOG_LEVEL" =~ ^(DEBUG|INFO)$ ]] && echo "[INFO]  $*" >&2
}
warn() { echo "[WARN]  $*" >&2; }
err()  { echo "[ERROR] $*" >&2; }
```

## Structured JSON Logging

For machine processing (e.g., shipped to log aggregator):
```bash
jlog() {
    local level="$1" msg="$2"
    jq -nc \
        --arg ts "$(date -uIs)" \
        --arg lvl "$level" \
        --arg m "$msg" \
        '{ts:$ts, level:$lvl, msg:$m}' >&2
}

jlog info "starting"
jlog error "connection failed"
```

## Timestamped

```bash
log() {
    local ts; ts=$(date '+%Y-%m-%d %H:%M:%S')
    echo "$ts $*" >&2
}
```

For UTC:
```bash
ts=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
```

## Pipeline-Friendly Pattern

```bash
# Stdout = data; stderr = logs
fetch_data() {
    log "fetching from $1"
    curl -s "$1"        # data goes to stdout
}

# Use with pipe; logs go to terminal/captured separately
data=$(fetch_data "https://api.example.com")
```

## Logging to File + Terminal

```bash
# Tee within script
exec > >(tee -a /var/log/myapp.log) 2>&1
log "now everything is logged"
```

This redirects ALL output from now on through tee.

## Logger (syslog)

```bash
logger "Something happened"
logger -t myscript "Error in script"
logger -p user.warn "Disk full"
```

Sent to syslog → /var/log/syslog (or journald).

## Per-Run Log File

```bash
LOG_FILE="/var/log/myscript-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$LOG_FILE") 2>&1
```

## Common Patterns

### Capture STDOUT, Show STDERR
```bash
result=$(some_cmd 2>&1 >&3) 3>&1
# Output to terminal; capture stderr in result
```

Tricky but useful.

### Don't Color in Logs
Detect TTY:
```bash
if [[ -t 1 ]]; then
    RED='\033[31m'; RESET='\033[0m'
else
    RED=''; RESET=''
fi

echo -e "${RED}error${RESET}"
```

When piped or in log file, no escape codes.

### Progress Bar to Stderr
```bash
for i in {1..100}; do
    echo -ne "\rProcessing $i/100" >&2
    work
done
echo "" >&2
```

Doesn't pollute stdout pipeline.

## Common Mistakes

- **Mixing logs into pipeline**: breaks `... | jq`
- **Echoing without `>&2`**: hard to separate
- **No timestamps**: hard to correlate with other logs
- **No log level**: can't filter
- **Logging passwords/tokens**: accidentally exposed

## Production Script Pattern

```bash
#!/usr/bin/env bash
set -euo pipefail

readonly LOG_FILE="${LOG_FILE:-/var/log/$(basename "$0" .sh).log}"
exec > >(tee -a "$LOG_FILE") 2>&1

log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }

log "starting"
# ... work
log "complete"
```

## Operations

```bash
# Watch log live
tail -f /var/log/myscript.log

# Filter
grep "ERROR" /var/log/myscript.log
journalctl -u myscript

# With color in pager
tail -f log | grep --color=always ERROR | less -R
```

## Interview Prep

**Junior**: "Why log to stderr?"

**Mid**: "Tee — what's it for?"

**Senior**: "Structured logging in bash."

**Staff**: "Script outputs JSON data + has progress logs. Design."

## Next Topic

→ [T03 — Error Handling Patterns](T03-Error-Handling.md)
