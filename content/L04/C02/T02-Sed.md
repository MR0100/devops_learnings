# L04/C02/T02 — sed (Substitution, In-Place Editing)

## Learning Objectives

- Apply sed for text transformation
- Use in-place editing correctly
- Combine commands

## Basic Substitution

```bash
sed 's/old/new/' file              # first occurrence per line
sed 's/old/new/g' file             # all occurrences (global)
sed 's/old/new/3' file             # 3rd occurrence per line
sed 's/old/new/gI' file            # case insensitive (GNU only)
```

Default: writes to stdout. Doesn't modify file.

## In-Place Editing

```bash
sed -i 's/old/new/g' file          # GNU sed
sed -i '' 's/old/new/g' file       # BSD/macOS sed
sed -i.bak 's/old/new/g' file      # backup to file.bak
```

GNU vs BSD: this is the most common cross-platform issue. macOS uses BSD; Linux uses GNU. Different `-i` syntax.

For portable: use `-i.bak` (works on both); remove .bak after.

## Delete Lines

```bash
sed '/pattern/d' file              # delete matching
sed '5d' file                      # delete line 5
sed '5,10d' file                   # lines 5-10
sed '$d' file                      # last line
sed '/^#/d' file                   # remove comments
sed '/^$/d' file                   # remove blank lines
```

## Print Specific Lines

```bash
sed -n '5p' file                   # only print line 5
sed -n '5,10p' file                # lines 5-10
sed -n '/pattern/p' file           # matching lines only
sed -n '$p' file                   # last line
```

`-n` suppresses default print; `p` prints explicitly.

## Insert / Append

```bash
sed '5i\new line' file             # insert BEFORE line 5
sed '5a\new line' file             # append AFTER line 5
sed '/pattern/i\new line' file     # before matching line
sed '/pattern/a\new line' file     # after matching line
```

## Replace Whole Line

```bash
sed '5c\New content' file          # replace line 5
sed '/pattern/c\replacement' file  # replace matching
```

## Multiple Commands

```bash
sed -e 's/a/A/' -e 's/b/B/' file
sed 's/a/A/; s/b/B/' file
sed '/^#/d; /^$/d' file           # remove comments + blank lines
```

## Address Ranges

```bash
sed '5,$ s/old/new/' file          # lines 5 to end
sed '/^BEGIN/,/^END/ s/x/y/' file  # between BEGIN and END markers
sed '/^#/,/^$/d' file              # from # to next blank
```

## Capture Groups

```bash
sed -E 's/([a-z]+) ([0-9]+)/\2 \1/' file   # swap word and number
echo "John 25" | sed -E 's/([a-z]+) ([0-9]+)/\2 \1/i'   # "25 John"
```

GNU sed: also `\(...\)` for capture in BRE; or `-E` for ERE.

## Delimiter Choice

```bash
sed 's|/old/path|/new/path|g' file    # use | as delimiter (no escape needed)
sed 's#/old/#/new/#g' file            # use #
sed 's,a,b,g' file                     # comma
```

Useful when pattern contains `/`.

## Backreferences

```bash
sed 's/\(.*\) is \(.*\)/\2 is \1/' file
# "x is y" → "y is x"
```

`\1`, `\2` etc.

## Holdspace (advanced)

sed has two buffers:
- **pattern space**: current line being processed
- **hold space**: persistent across lines

```bash
# Print every other line
sed -n 'h;n;G;p' file
```

Rarely used in DevOps; awk is friendlier for complex logic.

## Common Patterns

### Replace in Many Files
```bash
find . -name "*.yaml" -exec sed -i 's/oldval/newval/g' {} +
```

### Comment Out Lines Matching Pattern
```bash
sed -i '/pattern/s/^/# /' file
```

### Uncomment
```bash
sed -i 's/^# //' file
```

### Add Header to File
```bash
sed -i '1i\#!/usr/bin/env bash\nset -e' script.sh
```

### Remove Trailing Whitespace
```bash
sed -i 's/[ \t]*$//' file
```

### CRLF to LF (Windows → Unix)
```bash
sed -i 's/\r$//' file
# or: dos2unix
```

### Replace Only on Matching Lines
```bash
sed '/pattern/s/old/new/g' file
```

### Multi-line Substitute (limited)
sed processes line by line. For across-line patterns, use perl or awk.

## Useful sed Tricks

### Extract a Section
```bash
sed -n '/^BEGIN_SECTION/,/^END_SECTION/p' file
```

### Number Lines
```bash
sed = file | sed 'N;s/\n/\t/'
```

(Or just `cat -n file` / `nl file`.)

### Print Filename Headers
```bash
sed 's|^|prefix: |' file
```

## Limits

- One line at a time (no easy multi-line)
- Less powerful than awk for column processing
- Regex syntax differs slightly between BRE and ERE

## Common Mistakes

- **GNU vs BSD `-i`**: scripts fail on macOS / non-GNU
- **Forgetting `g`**: only first match replaced per line
- **Special chars in pattern**: `/` `.` `*` need escaping or different delimiter
- **Quoting**: `sed "s/$var/x/"` expands; safer with `'...'`
- **Backup file**: `sed -i ''` on macOS overwrites silently; use `-i.bak`

## Operations

```bash
# Big file: don't read whole file into memory
# sed streams; fine for huge files
sed 's/old/new/g' huge.log

# Multiple files; in place
find . -type f -exec sed -i 's/old/new/g' {} +

# Preview before applying
diff <(sed 's/old/new/' file) file
```

## Best Practices

- Write portable in-place edits as `sed -i.bak 's/.../.../' file` (works on both GNU and BSD/macOS), then delete the `.bak` once verified.
- Pick a delimiter that isn't in your data: `sed 's#/old/path#/new/path#'` avoids escaping every `/`.
- Preview before mutating: `diff <(sed 's/old/new/g' file) file` or just run without `-i` first.
- Use `-E` for extended regex so groups are `(...)` not `\(...\)`, and remember `\1`, `\2` for backreferences.
- Reach for `awk` (or a real language) once logic spans multiple lines or needs field math — sed is line-at-a-time.
- Prefer single quotes around scripts so the shell doesn't expand `$` and backticks; pass shell values via `-e` with care.

## Quick Refs

```bash
# Substitute
sed 's/old/new/'      file   # first match per line
sed 's/old/new/g'     file   # all matches
sed 's/old/new/2'     file   # 2nd match per line
sed 's/old/new/gI'    file   # global, case-insensitive (GNU)
sed '/only-here/s/a/b/g' f   # substitute only on matching lines

# In-place (portable)
sed -i.bak 's/old/new/g' file && rm file.bak

# Print / delete by address
sed -n '5,10p' file          # print lines 5-10  (-n = quiet)
sed -n '/START/,/END/p' file # print a marked block
sed '/^#/d; /^$/d' file      # drop comments and blank lines
sed '$d' file                # drop last line

# Insert / append / change
sed '1i\#!/usr/bin/env bash' file   # insert before line 1
sed '/anchor/a\added line' file     # append after a match
sed '3c\replacement' file           # replace line 3

# Capture groups (ERE)
sed -E 's/([a-z]+) ([0-9]+)/\2 \1/' file   # swap word and number

# Common fixups
sed -i.bak 's/[ \t]*$//' file   # strip trailing whitespace
sed -i.bak 's/\r$//' file       # CRLF -> LF
```

## Interview Prep

**Junior**: "Replace 'foo' with 'bar' in file."

**Mid**: "In place but with backup."

**Senior**: "Remove comments + blank lines."

**Staff**: "Cross-platform `-i` — solve."

## Next Topic

→ [T03 — awk (Programming with awk)](T03-Awk.md)
