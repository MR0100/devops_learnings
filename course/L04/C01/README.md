# L04/C01 — Bash Fundamentals

## Chapter Overview

The shell is the single tool you'll use most across your DevOps career. Strong bash fundamentals make every command line faster, every script safer, and every debugging session shorter.

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Shells.md) | Shells: bash, zsh, fish, sh, dash | 0.5 hr |
| [T02](T02-Variables-Quoting.md) | Variables, Quoting, Expansion | 1.5 hr |
| [T03](T03-Conditionals-Loops.md) | Conditionals, Loops, Functions | 1.5 hr |
| [T04](T04-Exit-Codes-Set.md) | Exit Codes, set -euo pipefail | 1 hr |

## Shells Compared

| Shell | Used As | Notes |
|---|---|---|
| bash | Default Linux interactive + scripting | Most common; v5+ widely deployed |
| zsh | macOS default since Catalina | Better interactive UX (oh-my-zsh) |
| fish | User-friendly | Not POSIX; not for scripts |
| sh / dash | POSIX scripting | Minimal; what `#!/bin/sh` resolves to in Debian |
| ash | Alpine default | Minimal; bash differs |

**Scripting recommendation**: use bash explicitly (`#!/usr/bin/env bash`) unless you need POSIX portability.

## Quoting (The Trap)

```bash
# These behave VERY differently
echo $var           # word-splits and globs
echo "$var"         # literal value, spaces preserved
echo '$var'         # literal string "$var"
echo "\$var"        # backslash escape inside double quotes
```

### Rule
> Always double-quote variables in commands unless you have a specific reason not to.

### Expansions

```bash
# Parameter expansion
${var}                  # explicit boundaries
${var:-default}         # use default if unset/empty
${var:=default}         # set var to default if unset/empty
${var:?error msg}       # exit with error if unset
${var:+other}           # use 'other' if var IS set
${var:0:5}              # substring
${var^^}                # uppercase
${var,,}                # lowercase
${var/pattern/replace}  # replace first
${var//pattern/replace} # replace all
${#var}                 # length
${var#prefix}           # remove shortest prefix match
${var##prefix}          # remove longest prefix match
${var%suffix}           # remove shortest suffix
${var%%suffix}          # remove longest suffix

# Command substitution
result=$(command)         # preferred
result=`command`          # backticks; avoid

# Arithmetic
n=$(( a + b ))
(( i++ ))

# Glob
ls *.log
ls /etc/*/conf.d/*.conf

# Brace expansion
mkdir -p dir/{a,b,c}
echo {1..10}
echo {a..f}
echo {01..05}              # 01 02 03 04 05
```

## Conditionals

```bash
# Single bracket [ ] — POSIX, also called `test`
if [ "$x" = "1" ]; then ... fi
if [ -f /etc/foo ]; then ... fi   # file exists
if [ -d /var/log ]; then ... fi   # directory
if [ -z "$var" ]; then ... fi     # zero length
if [ -n "$var" ]; then ... fi     # non-zero length
if [ "$a" -eq "$b" ]; then ... fi # numeric equal

# Double bracket [[ ]] — bash extension, smarter
if [[ "$x" == "1" ]]; then ... fi
if [[ "$x" == *.log ]]; then ... fi    # glob match
if [[ "$x" =~ ^[0-9]+$ ]]; then ... fi # regex match
if [[ -f /etc/foo && -r /etc/foo ]]; then ... fi  # logical &&
```

### Comparison Cheat
| Numeric | String |
|---|---|
| `-eq` | `=` (or `==` in `[[ ]]`) |
| `-ne` | `!=` |
| `-lt` | `<` (in `[[ ]]` only) |
| `-le` | `<=` |
| `-gt` | `>` |
| `-ge` | `>=` |

## Loops

```bash
# C-style
for ((i=0; i<10; i++)); do ... done

# Iterate items
for item in "${arr[@]}"; do ... done
for f in /tmp/*.log; do ... done

# Range
for i in {1..10}; do ... done

# While
while read -r line; do ... done < file
while [[ $count -lt 10 ]]; do ((count++)); done

# Until
until ping -c1 host >/dev/null; do sleep 1; done

# Read lines from file (safely)
while IFS= read -r line; do
  echo "$line"
done < file.txt
```

## Functions

```bash
my_func() {
  local var="$1"     # local to function
  local var2="$2"
  echo "got $var $var2"
  return 0           # exit code
}

my_func "hello" "world"
result=$(my_func "hello" "world")
```

### Local Variables
Without `local`, variables leak to caller. Always use `local` for function-scoped vars.

## Exit Codes & Strict Mode

```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# -e: exit on any error
# -u: error on undefined variable
# -o pipefail: pipe fails if any stage fails
# IFS: tabs and newlines only (avoid space-splitting)
```

### Why strict mode matters

Without `-e`:
```bash
rm /important/file
do_something_else        # runs even if rm failed
```

Without `-o pipefail`:
```bash
broken_command | grep foo     # exit code 0 if grep succeeded
```

Without `-u`:
```bash
rm -rf "$DEST_DIR/sub"   # if DEST_DIR is empty → rm -rf /sub
```

## Exit Codes Convention

- `0` = success
- `1-125` = generic errors
- `126` = command not executable
- `127` = command not found
- `128 + N` = killed by signal N (e.g., 137 = SIGKILL)
- `255` = exit code outside 0-255

```bash
command
if [[ $? -ne 0 ]]; then echo failed; fi

# Or:
if ! command; then echo failed; fi
```

## Process Substitution

```bash
diff <(sort a) <(sort b)        # treat command output as a file
while read l; do ...; done < <(some_command)
```

## Subshells vs Current Shell

```bash
(cd /tmp && ls)         # subshell; doesn't change parent's cwd
{ cd /tmp; ls; }        # current shell; does change cwd
```

## Heredoc

```bash
cat <<EOF > /etc/myconf
key=value
host=$(hostname)            # expansion happens
EOF

cat <<'EOF' > /etc/myconf
key=value
host=$(hostname)            # literal — no expansion
EOF
```

## Common Mistakes

- Not quoting variables
- Forgetting `local` in functions
- Using `==` in single brackets (works in bash, but not POSIX)
- Not setting strict mode
- Using `set -e` and assuming it catches everything (it doesn't, in many cases)
- `cmd1 || cmd2` not noticing cmd2 ran on error

## Interview Themes

- "Write a script that processes files in /tmp/*.log and reports lines containing 'error'"
- "Why use set -euo pipefail?"
- "Difference between [ ] and [[ ]]"
- "How does parameter expansion's `${var:-default}` work?"
- "When does set -e NOT catch errors?"
