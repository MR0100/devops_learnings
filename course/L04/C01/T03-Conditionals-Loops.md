# L04/C01/T03 — Conditionals, Loops, Functions

## Learning Objectives

- Use bash conditional constructs correctly
- Write idiomatic loops
- Structure functions

## Conditionals

### Single Bracket `[`
POSIX-compatible. Less powerful.
```bash
if [ "$x" = "1" ]; then ... fi          # string equal
if [ "$x" != "1" ]; then ... fi
if [ "$n" -eq 5 ]; then ... fi          # numeric
if [ -f /etc/hosts ]; then ... fi       # file exists
if [ -d /var/log ]; then ... fi         # directory
if [ -z "$var" ]; then ... fi           # zero length
if [ -n "$var" ]; then ... fi           # non-zero length
```

### Double Bracket `[[ ]]` (bash extension)
Preferred for new scripts. Smarter.
```bash
if [[ "$x" == "1" ]]; then ... fi
if [[ "$x" == *.log ]]; then ... fi     # glob match
if [[ "$x" =~ ^[0-9]+$ ]]; then ... fi  # regex match
if [[ -f /etc/hosts && -r /etc/hosts ]]; then ... fi
```

Differences:
- No word splitting inside `[[ ]]`
- `<` `>` for string compare (no escape)
- `=~` for regex
- `&&` `||` for logic

### Arithmetic `(( ))`
```bash
if (( x > 10 )); then ... fi
if (( x == y )); then ... fi
```

No `$` needed inside.

## Test Operators

### File
- `-e` exists (file/dir/anything)
- `-f` regular file
- `-d` directory
- `-r` readable
- `-w` writable
- `-x` executable
- `-s` non-empty
- `-L` symlink

### String
- `=` equal (single `[`); `==` (double `[[`)
- `!=` not equal
- `<` less than (lex order)
- `-z` zero length
- `-n` non-zero length

### Numeric
- `-eq`, `-ne`, `-lt`, `-le`, `-gt`, `-ge`

### File Comparison
- `-nt` newer than
- `-ot` older than
- `-ef` same file (same inode)

## Loops

### for (list)
```bash
for x in a b c; do echo "$x"; done

# From array
arr=(a b c)
for item in "${arr[@]}"; do echo "$item"; done

# Files
for f in /tmp/*.log; do
    process "$f"
done

# Range
for i in {1..10}; do echo "$i"; done
```

### for (C-style)
```bash
for ((i=0; i<10; i++)); do echo "$i"; done
```

### while
```bash
while [[ $count -lt 10 ]]; do
    echo "$count"
    ((count++))
done

# Read file line-by-line (CORRECT way)
while IFS= read -r line; do
    echo "$line"
done < file.txt
```

`IFS=` and `-r` prevent whitespace stripping and backslash interpretation.

### until
```bash
until ping -c1 -W1 host >/dev/null 2>&1; do
    sleep 1
done
echo "host is up"
```

### Loop Control
```bash
for x in *; do
    [[ -d "$x" ]] || continue       # skip non-dirs
    [[ "$x" == "stop" ]] && break   # bail out
    process "$x"
done
```

## Reading Command Output

```bash
# This loses subshell vars
ls | while read f; do
    count=$((count + 1))
done
echo "$count"   # always 0!

# Use process substitution instead
count=0
while IFS= read -r f; do
    count=$((count + 1))
done < <(ls)
echo "$count"   # correct
```

## Functions

```bash
greet() {
    local name="$1"
    echo "Hello, $name"
}

greet "Alice"

# Return value (echo + capture)
square() {
    echo $(( $1 * $1 ))
}

result=$(square 5)
echo "$result"  # 25

# Exit code (return)
is_even() {
    (( $1 % 2 == 0 ))
}

if is_even 4; then echo even; fi
```

### Local Variables
**Always** use `local` in functions. Without it, variables leak to caller.

```bash
bad_func() {
    x=5
}
x=10
bad_func
echo "$x"   # 5 — x got clobbered!

good_func() {
    local x=5
}
x=10
good_func
echo "$x"   # 10 — preserved
```

### Returning Multiple Values
- Echo joined; caller parses
- Use globals (with care)
- Use nameref (bash 4.3+)

```bash
# nameref
get_user() {
    local -n out=$1   # nameref
    out[name]=Alice
    out[age]=30
}

declare -A user
get_user user
echo "${user[name]}"
```

## case Statement

```bash
case "$action" in
    start)   start_service ;;
    stop)    stop_service ;;
    restart) stop_service; start_service ;;
    *)       echo "Unknown: $action"; exit 1 ;;
esac
```

Patterns can be globs:
```bash
case "$file" in
    *.log)   process_log "$file" ;;
    *.gz)    gunzip "$file" ;;
    *)       echo "skip" ;;
esac
```

## select (Interactive Menu)

```bash
PS3="Choose: "
select option in "Start" "Stop" "Quit"; do
    case $option in
        Start) ... ;;
        Stop)  ... ;;
        Quit)  break ;;
    esac
done
```

## Common Patterns

### Retry
```bash
attempts=0
until cmd; do
    ((attempts++))
    [[ $attempts -ge 5 ]] && { echo "failed"; exit 1; }
    sleep $((2 ** attempts))   # exponential backoff
done
```

### Check Required Commands
```bash
for cmd in curl jq aws; do
    command -v "$cmd" >/dev/null || { echo "missing: $cmd"; exit 1; }
done
```

### Validate Input
```bash
[[ $# -eq 2 ]] || { echo "Usage: $0 SOURCE DEST"; exit 1; }
[[ -f "$1" ]] || { echo "Not a file: $1"; exit 1; }
```

## Interview Prep

**Junior**: "When use single vs double bracket?"

**Mid**: "Why use `local` in functions?"

**Senior**: "while-read in subshell loses variables — explain."

## Next Topic

→ [T04 — Exit Codes, set -euo pipefail](T04-Exit-Codes-Set.md)
