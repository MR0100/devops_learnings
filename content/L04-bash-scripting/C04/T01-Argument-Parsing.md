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

## Common Mistakes

- **Confusing `getopts` (bash builtin) with `getopt` (external)**: only `getopts` is portable; the GNU `getopt` that supports long options isn't on macOS/BSD by default.
- **Forgetting `shift $((OPTIND - 1))`**: positional arguments stay tangled with flags, so `"$1"` isn't what you expect after the loop.
- **No leading `:` in the optstring**: `getopts ":ab:"` enables silent error handling so you can emit your own usage; without it getopts prints its own messages.
- **`--flag=value` not handled**: manual loops that only match `--flag value` silently drop the `--flag=value` form unless you add a `--flag=*` case.
- **No `--` end-of-options sentinel**: filenames beginning with `-` get parsed as options; honor `--` to stop option processing.
- **Validating too late**: reading `$OPTARG` into a variable but never checking it's a number/path/in-range lets bad input reach the work.

## Best Practices

- Use `getopts` for short flags in portable scripts; only reach for manual `while [[ $# ]]` parsing when you need long options.
- Always provide a `usage()` that writes to stderr and exits non-zero, wired to `-h`/`--help` and to every parse error.
- Support both `--opt value` and `--opt=value`, and honor `--` to terminate option parsing.
- Validate every input immediately after parsing (required-set, file exists, numeric, in-range) and fail fast with a clear message.
- Default flags to safe values (`DRY_RUN=false`, sensible counts) and make destructive behavior opt-in.
- When parsing grows complex (subcommands, types, mutually-exclusive flags), switch to Python `argparse` rather than fighting bash.

## Quick Refs

```bash
# getopts: short flags (':' = silent errors; trailing ':' = takes an arg)
while getopts ":dvc:h" opt; do
  case $opt in
    d) DRY_RUN=true ;;
    v) VERBOSE=true ;;
    c) COUNT=$OPTARG ;;
    h) usage 0 ;;
    :)  echo "-$OPTARG needs an argument" >&2; usage 1 ;;
    \?) echo "unknown option -$OPTARG" >&2; usage 1 ;;
  esac
done
shift $((OPTIND - 1))   # drop parsed options, leave positionals

# Manual long-option loop (handles --opt val, --opt=val, --)
while [[ $# -gt 0 ]]; do
  case "$1" in
    -d|--dry-run) DRY_RUN=true; shift ;;
    -o|--output)  OUTPUT=$2; shift 2 ;;
    --output=*)   OUTPUT=${1#*=}; shift ;;
    -h|--help)    usage 0 ;;
    --)           shift; break ;;
    -*)           echo "unknown: $1" >&2; usage 1 ;;
    *)            ARGS+=("$1"); shift ;;
  esac
done

# Validation after parsing
[[ -n "${DIR:-}" ]] || { echo "--dir required" >&2; exit 2; }
[[ -d "$DIR" ]]     || { echo "not a dir: $DIR" >&2; exit 1; }
[[ $COUNT =~ ^[0-9]+$ ]] || { echo "count must be a number" >&2; exit 2; }

# Usage helper
usage() { cat >&2 <<EOF
Usage: $0 [-d] [-v] [-c COUNT] FILE
EOF
  exit "${1:-1}"; }
```

## Interview Prep

**Junior**: "Parse `-v` flag."

**Mid**: "Parse `--dir PATH` and `--dir=PATH`."

**Senior**: "Subcommand-style CLI in bash."

## Next Topic

→ [T02 — Logging, Stderr vs Stdout, Tee](T02-Logging.md)
