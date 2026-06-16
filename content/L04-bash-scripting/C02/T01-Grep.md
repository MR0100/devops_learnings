# L04/C02/T01 — grep, egrep, fgrep, ripgrep

## Learning Objectives

- Use grep flags productively
- Apply regex patterns
- Choose ripgrep when faster

## Basics

```bash
grep "pattern" file
grep "pattern" file1 file2
grep -r "pattern" /path                # recursive
grep -i "pattern" file                 # case insensitive
grep -v "pattern" file                 # invert (lines NOT matching)
grep -n "pattern" file                 # show line numbers
grep -c "pattern" file                 # count matches
grep -l "pattern" *                    # files with matches (only names)
grep -L "pattern" *                    # files WITHOUT matches
grep -A 3 "pattern" file               # 3 lines after
grep -B 3 "pattern" file               # 3 lines before
grep -C 3 "pattern" file               # 3 lines both
grep -w "word" file                    # whole word only
grep -o "pattern" file                 # only print matched part
```

## Regex Modes

```bash
grep "pattern"        # BRE (basic regex; default)
grep -E "pattern"     # ERE (extended; like egrep)
grep -P "pattern"     # PCRE (Perl regex; GNU grep only)
grep -F "pattern"     # fixed string (like fgrep; fastest)
```

`egrep` and `fgrep` are aliases for `grep -E` and `grep -F`.

## Patterns

### Basic
```bash
grep "^Error" file               # at start
grep "$" file                    # at end
grep "[0-9]" file                # any digit
grep "[^0-9]" file               # non-digit
grep "a.b" file                  # a + any char + b
```

### Extended (-E)
```bash
grep -E "foo|bar" file           # foo or bar
grep -E "[0-9]+" file            # one or more digits
grep -E "[0-9]?" file            # zero or one
grep -E "[0-9]*" file            # zero or more
grep -E "(foo|bar) (baz|qux)" file  # alternation in groups
```

### PCRE (-P)
```bash
grep -P "\d+" file               # digit
grep -P "\w+" file               # word char
grep -P "\s+" file               # whitespace
grep -P "(?<=prefix)\d+" file    # lookbehind
grep -P "\d+(?=suffix)" file     # lookahead
```

## Multiple Patterns

```bash
grep -e "pattern1" -e "pattern2" file
grep -E "pattern1|pattern2" file
grep -f patterns.txt file        # one pattern per line in file
```

## Recursive Options

```bash
grep -r "pattern" .                            # all files
grep -r --include="*.py" "pattern" .            # only .py
grep -r --exclude="*.log" "pattern" .            # exclude
grep -r --exclude-dir=node_modules "pat" .
grep -r --binary-files=without-match "pat" .   # skip binaries
```

## Performance: Use ripgrep (rg)

10-100× faster than grep for large codebases:
```bash
rg "pattern"                     # respects .gitignore by default
rg -i "pattern"
rg -t py "pattern"               # type-filter (Python files)
rg -tnotest "pattern"            # exclude type
rg --files-with-matches "pat"    # like grep -l
rg -A 3 "pattern"
rg -e "p1" -e "p2"
```

Why so fast:
- Multi-threaded
- Memory-mapped I/O
- Smart `.gitignore` handling
- Compiled regex (Rust + DFA)

For DevOps: `rg` should be muscle memory.

## Common Patterns

### Find Errors in Logs
```bash
grep -i "error\|fail" /var/log/syslog | tail -20
grep -E "^\S+ \S+ ERROR" app.log
```

### IPs in Access Log
```bash
grep -oE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" access.log | sort | uniq -c | sort -rn | head
```

### Lines Without Pattern
```bash
grep -v "^#" config.txt | grep -v "^$"   # remove comments + blank
```

### Multi-line Match
grep doesn't do multi-line natively. Use `pcregrep -M` or `awk`:
```bash
pcregrep -M "begin.*?end" file
```

### Whole Word
```bash
grep -wn "TODO" file              # exact word; not "TODOnow"
```

## Color Output

```bash
grep --color=always "pattern" file | less -R
export GREP_OPTIONS='--color=auto'   # always color (some shells)
```

## Common Mistakes

- **Forgetting -F** for literal: `grep "1.2.3.4"` matches "1X2Y3Z4" (`.` is wildcard)
- **Word boundaries**: `grep "ip"` matches "skip"; use `-w`
- **Quoting**: `grep $pattern file` word-splits; use `grep "$pattern" file`
- **Including binaries**: large binary files slow grep; use `--binary-files=without-match`

## Pipe Patterns

```bash
# Process running with high CPU
ps aux | grep -i -- "100\.0"

# Listening ports by process
ss -tlnp | grep -v "users"

# Recent errors with timestamp
grep "ERROR" /var/log/app.log | grep "$(date +%Y-%m-%d)"

# Top errors
grep "ERROR" app.log | awk '{print $NF}' | sort | uniq -c | sort -rn | head -10
```

## Best Practices

- Use `-F` (fixed strings) whenever the pattern is a literal — it is faster and avoids accidental regex metacharacters (`.`, `*`, `[`).
- Quote patterns and variables: `grep -- "$pattern" file` (the `--` also protects against patterns starting with `-`).
- Prefer `rg` (ripgrep) for codebases: it is multithreaded, respects `.gitignore`, and skips binaries by default.
- Filter recursive searches with `--include`/`--exclude-dir` (or `rg -g`) instead of grepping `node_modules`/`.git`.
- Use `-w` for word matches and anchors (`^`, `$`) to avoid substring false positives.
- Choose the regex flavor deliberately: `-E` for ERE, `-P` only when you need PCRE features like lookaround (GNU grep only).
- Use exit status for control flow: `grep -q pattern file` returns 0/1 without printing.

## Quick Refs

```bash
# Core flags
grep -i pat f        # case-insensitive      grep -v pat f   # invert
grep -n pat f        # line numbers          grep -c pat f   # count
grep -o pat f        # print only the match  grep -w pat f   # whole word
grep -r pat dir/     # recursive             grep -l pat *   # names only
grep -A3 -B3 pat f   # 3 lines of context each side (or -C3)
grep -q pat f && echo "found"   # quiet, status-only

# Regex flavors
grep -E 'foo|bar' f          # extended regex (egrep)
grep -F '1.2.3.4' f          # literal string (fgrep, fast)
grep -P '(?<=id=)\d+' f      # PCRE lookbehind (GNU only)

# Scoped recursive search
grep -rn --include='*.py' --exclude-dir={.git,node_modules} pat .

# ripgrep equivalents
rg pat                 # honors .gitignore, multithreaded
rg -t py pat           # only Python files
rg -l pat              # files with matches
rg -F 'literal' .

# Extract & rank IPs from an access log
grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}' access.log | sort | uniq -c | sort -rn | head
```

## Interview Prep

**Junior**: "Find all lines containing X in a file."

**Mid**: "Show 3 lines context around each match."

**Senior**: "Match an IP address pattern."

**Staff**: "Search 10 GB of logs efficiently."

## Next Topic

→ [T02 — sed (Substitution, In-Place Editing)](T02-Sed.md)
