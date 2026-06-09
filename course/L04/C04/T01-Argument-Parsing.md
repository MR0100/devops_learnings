# L04/C04/T01 — Argument Parsing (getopts, getopt)

## Learning Objectives

- Parse arguments with getopts
- Handle long options manually
- Validate inputs

## getopts (POSIX, Single-Letter)

Built into bash. Handles single-letter flags.

```bash
#!/usr/bin/env bash

DRY_RUN=false
VERBOSE=false
COUNT=10

usage() {
    cat >&2 <<EOF
Usage: $0 [-d] [-v] [-c COUNT] FILE
  -d        dry-run
  -v        verbose
  -c COUNT  count (default 10)
EOF
    exit 1
}

while getopts ":dvc:h" opt; do
    case $opt in
        d) DRY_RUN=true ;;
        v) VERBOSE=true ;;
        c) COUNT="$OPTARG" ;;
        h) usage ;;
        :) echo "Option -$OPTARG requires argument" >&2; usage ;;
        \?) echo "Unknown option: -$OPTARG" >&2; usage ;;
    esac
done
shift $((OPTIND - 1))

# Now positional args available
FILE="$1"
[[ -z "$FILE" ]] && usage
```

### Notes
- `c:` after letter = requires argument
- Leading `:` enables silent error mode (you handle errors)
- `OPTIND` is the next argument index
- `shift $((OPTIND - 1))` moves past options

## getopts Limitations

- Single letters only (no `--long-option`)
- No "either or" between forms
- Manual long-option implementation needed

## Long Options (Manual)

```bash
DRY_RUN=false
VERBOSE=false
DIR=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run|-d)
            DRY_RUN=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --dir)
            DIR="$2"
            shift 2
            ;;
        --dir=*)
            DIR="${1#*=}"
            shift
            ;;
        -h|--help)
            usage
            ;;
        --)
            shift
            break
            ;;
        -*)
            echo "Unknown option: $1" >&2
            usage
            ;;
        *)
            ARGS+=("$1")
            shift
            ;;
    esac
done
```

Handles `--dir VALUE` and `--dir=VALUE` syntaxes.

## Validation After Parsing

```bash
[[ -z "$DIR" ]] && { echo "--dir required"; exit 1; }
[[ -d "$DIR" ]] || { echo "Not a directory: $DIR"; exit 1; }
[[ $COUNT =~ ^[0-9]+$ ]] || { echo "Count must be number"; exit 1; }
(( COUNT > 0 && COUNT <= 100 )) || { echo "Count out of range"; exit 1; }
```

## Complete Template

```bash
#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat >&2 <<EOF
Usage: $0 [OPTIONS] FILE

Options:
  -d, --dry-run       Print actions without executing
  -v, --verbose       Verbose output
  -c, --count N       Number of items (default: 10)
  -o, --output PATH   Output file
  -h, --help          Show this help

Examples:
  $0 -v input.txt
  $0 --dry-run --count 5 input.txt
EOF
    exit "${1:-1}"
}

DRY_RUN=false
VERBOSE=false
COUNT=10
OUTPUT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -d|--dry-run) DRY_RUN=true; shift ;;
        -v|--verbose) VERBOSE=true; shift ;;
        -c|--count) COUNT="$2"; shift 2 ;;
        --count=*) COUNT="${1#*=}"; shift ;;
        -o|--output) OUTPUT="$2"; shift 2 ;;
        --output=*) OUTPUT="${1#*=}"; shift ;;
        -h|--help) usage 0 ;;
        --) shift; break ;;
        -*) echo "Unknown: $1" >&2; usage ;;
        *) break ;;
    esac
done

[[ $# -eq 1 ]] || usage
FILE="$1"

[[ -f "$FILE" ]] || { echo "Not found: $FILE" >&2; exit 1; }
[[ $COUNT =~ ^[0-9]+$ ]] || { echo "Bad count" >&2; exit 1; }

$VERBOSE && echo "Processing $FILE..."
$DRY_RUN && echo "DRY-RUN: would do work"
```

## util-linux getopt

Different tool (note: getopt vs getopts). Enhanced. Supports long options.

```bash
PARSED=$(getopt -o dvc:h --long dry-run,verbose,count:,help -n "$0" -- "$@")
[[ $? -ne 0 ]] && exit 1

eval set -- "$PARSED"

while true; do
    case "$1" in
        -d|--dry-run) DRY_RUN=true; shift ;;
        -v|--verbose) VERBOSE=true; shift ;;
        -c|--count) COUNT="$2"; shift 2 ;;
        --) shift; break ;;
    esac
done
```

But `getopt` is GNU; not portable. Use manual parsing.

## Python's argparse (Better Choice)

If parsing complexity grows, switch to Python:
```python
import argparse

p = argparse.ArgumentParser()
p.add_argument("file")
p.add_argument("--dry-run", "-d", action="store_true")
p.add_argument("--count", "-c", type=int, default=10)
args = p.parse_args()
```

Easier than bash for complex CLIs.

## Common Patterns

### Required Args via Env Fallback
```bash
VAR="${1:-${MY_VAR:-default}}"
```

### Subcommands (git-style)
```bash
case "${1:-}" in
    start) shift; start_cmd "$@" ;;
    stop)  shift; stop_cmd "$@" ;;
    *) echo "Subcommand: start|stop"; exit 1 ;;
esac
```

### Pass-Through (--)
```bash
mycmd -v -- --option-to-inner-tool
# Anything after -- is verbatim to inner
```

## Interview Prep

**Junior**: "Parse `-v` flag."

**Mid**: "Parse `--dir PATH` and `--dir=PATH`."

**Senior**: "Subcommand-style CLI in bash."

## Next Topic

→ [T02 — Logging, Stderr vs Stdout, Tee](T02-Logging.md)
