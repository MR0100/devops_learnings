# L04/C01/T02 — Variables, Quoting, Expansion

## Learning Objectives

- Quote variables correctly to prevent word splitting
- Use parameter expansion fluently
- Avoid common bash gotchas

## Variables

```bash
name=alice              # no spaces around =
echo "$name"            # quote when using
readonly NAME=alice     # immutable
local x=1               # function-scoped
unset name              # remove
```

## Quoting Rules

| | Effect |
|---|---|
| `"$var"` | Expand value, preserve as one arg |
| `'$var'` | Literal string `$var` (no expansion) |
| `$var` | Expand + word split + glob (DANGEROUS) |
| `"$@"` | All args, each one preserved as separate |
| `"$*"` | All args joined into one |
| `$@` | All args, each split (avoid) |

### The Big Rule
> **Always double-quote variables in commands** unless you have a specific reason not to.

```bash
file="my file.txt"

cp $file backup/           # FAILS — tries to copy 2 files: "my" and "file.txt"
cp "$file" backup/         # WORKS
```

## Parameter Expansion

```bash
# Defaults
${var:-default}            # default if unset/empty (doesn't assign)
${var:=default}            # default + assign
${var:?error msg}          # exit with error if unset
${var:+other}              # use 'other' if var IS set

# Substring
${var:0:5}                 # substring offset 0 length 5
${var: -5}                 # last 5 chars (note leading space)
${#var}                    # length

# Case
${var^^}                   # uppercase all
${var,,}                   # lowercase all
${var^}                    # uppercase first
${var,}                    # lowercase first

# Replace
${var/old/new}             # replace first
${var//old/new}            # replace all
${var/#prefix/replacement} # at start
${var/%suffix/replacement} # at end

# Trim
${var#prefix}              # remove shortest prefix
${var##prefix}             # remove longest prefix
${var%suffix}              # remove shortest suffix
${var%%suffix}             # remove longest suffix

# Examples
file="path/to/file.tar.gz"
echo "${file##*/}"         # file.tar.gz (basename)
echo "${file%/*}"          # path/to (dirname)
echo "${file%.*}"          # path/to/file.tar (no ext)
echo "${file##*.}"         # gz (extension)
```

## Command Substitution

```bash
result=$(command)          # PREFERRED
result=`command`           # backticks; avoid (nested escape pain)
```

```bash
files=$(ls *.txt)          # captures stdout
count=$(echo "$files" | wc -l)
```

## Arithmetic

```bash
n=$((2 + 3))               # 5
(( i++ ))                  # increment (no $)
((x = 5 * 2))              # set
if (( x > 10 )); then ... fi   # numeric comparison

# vs string compare
if [ "$x" = "10" ]; then ... fi
```

## Brace Expansion

```bash
mkdir -p dir/{a,b,c}       # dir/a dir/b dir/c
echo {1..10}               # 1 2 3 4 5 6 7 8 9 10
echo {a..e}                # a b c d e
echo {01..05}              # 01 02 03 04 05 (zero-padded)
echo {2..10..2}            # 2 4 6 8 10 (step)
cp file.txt{,.bak}         # cp file.txt file.txt.bak
```

Happens BEFORE variable expansion. Common gotcha:
```bash
n=5
echo {1..$n}               # literal "{1..5}" — not what you want
```

Use `seq` or `for ((i=1; i<=n; i++))` for variable ranges.

## Glob Expansion

```bash
ls *.log                   # all .log files
ls log_*                   # starting with log_
ls log_[0-9]*              # log_ then digit then anything
ls log_{a,b}.txt           # log_a.txt log_b.txt (brace, not glob)

# Extended globbing (shopt)
shopt -s extglob
ls !(*.log)                # everything NOT .log
ls *.@(jpg|png)            # jpg or png

# Recursive (bash 4+)
shopt -s globstar
ls **/*.log                # all .log files recursively
```

If no matches: glob remains literal (unless `shopt -s nullglob`).

## Environment Variables

```bash
export MY_VAR=value        # child processes see it
unset MY_VAR

# In one line
MY_VAR=value command       # set for this command only
```

`env` shows current environment.

## Common Mistakes

### Unquoted variables with spaces
```bash
file="my report.txt"
rm $file                   # tries: rm my report.txt → wrong files removed
rm "$file"                 # correct
```

### Assuming `$@` and `$*` are same
```bash
"$@"                       # each arg quoted separately (preserves word boundaries)
"$*"                       # all args joined as one
```

For looping: `for arg in "$@"`.

### Equal sign spacing
```bash
x = 5                      # WRONG: tries to run command 'x' with args = 5
x=5                        # CORRECT
```

### IFS Issues
```bash
str="a:b:c"
IFS=':'
for x in $str; do echo "$x"; done   # works
# but: $str is unquoted; only works because we changed IFS
```

## Tools

- **shellcheck**: catches quoting bugs
- **bash -n script.sh**: syntax check without running
- **bash -x script.sh**: debug trace (each command echoed)

## Interview Prep

**Junior**: "Why quote variables?"

**Mid**: "Explain `${var:-default}`."

**Senior**: "`$@` vs `$*` — when each?"

**Staff**: "Debug a script that fails on filenames with spaces."

## Next Topic

→ [T03 — Conditionals, Loops, Functions](T03-Conditionals-Loops.md)
