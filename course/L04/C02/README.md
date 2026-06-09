# L04/C02 — Text Processing

## Chapter Overview

The Unix philosophy: small tools that compose. Mastery of `grep`, `sed`, `awk`, and `jq` is a productivity multiplier.

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Grep.md) | grep, egrep, fgrep, ripgrep | 1 hr |
| [T02](T02-Sed.md) | sed (Substitution, In-Place Editing) | 1 hr |
| [T03](T03-Awk.md) | awk (Programming with awk) | 2 hr |
| [T04](T04-Cut-Sort-Uniq.md) | cut, sort, uniq, tr, paste, join | 1 hr |
| [T05](T05-Jq-Yq.md) | jq for JSON, yq for YAML | 1.5 hr |

## grep Essentials

```bash
grep "pattern" file
grep -i "pattern" file              # case insensitive
grep -v "pattern" file              # invert
grep -n "pattern" file              # line numbers
grep -c "pattern" file              # count matches
grep -l "pattern" *                 # files only
grep -r "pattern" /path             # recursive
grep -A 3 "pattern" file            # 3 lines after
grep -B 3 "pattern" file            # 3 lines before
grep -C 3 "pattern" file            # 3 lines context

# Extended regex
grep -E "foo|bar" file
grep -E "^[0-9]+$" file
grep -P "perl regex" file           # PCRE (GNU only)

# Fixed string (no regex)
grep -F "literal.string[" file
```

`ripgrep` (`rg`) — 10-100× faster, respects `.gitignore`, smart defaults. Drop-in for most uses.

## sed

```bash
# Substitution
sed 's/old/new/' file           # first per line
sed 's/old/new/g' file          # all
sed 's/old/new/3' file          # third match per line

# In-place edit
sed -i 's/old/new/g' file       # GNU
sed -i '' 's/old/new/g' file    # macOS (BSD)

# Delete lines
sed '/pattern/d' file
sed '5d' file                   # line 5
sed '5,10d' file                # lines 5-10
sed '$d' file                   # last line

# Insert/append
sed '5i\new line' file          # insert before line 5
sed '5a\new line' file          # append after line 5

# Multiple commands
sed -e 's/a/b/' -e 's/c/d/' file
sed '/^#/d; /^$/d' file         # remove comments + blank lines

# Print specific lines
sed -n '5,10p' file             # lines 5-10
sed -n '/pattern/p' file        # matching lines
```

### Common Pitfalls
- BSD vs GNU sed differ (`-i` syntax especially)
- Forgetting `g` flag for all-occurrences
- Special chars in patterns (use `|` as delimiter to avoid escaping `/`)

```bash
sed 's|/old/path|/new/path|g' file
```

## awk

A complete programming language. Worth learning.

```bash
# Basic
awk '{print $1}' file                  # column 1 (whitespace-delimited)
awk -F: '{print $1}' /etc/passwd       # custom delimiter
awk '/pattern/ {print}' file           # matching lines
awk 'NR==5' file                       # line 5
awk 'NR>=5 && NR<=10' file             # range
awk 'NF>3' file                        # rows with >3 fields

# Sum a column
awk '{sum += $1} END {print sum}' file

# Average
awk '{sum += $1; count++} END {print sum/count}' file

# Unique values in column
awk '{print $1}' file | sort | uniq

# Top 10 IPs in log (classic)
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10

# Print multiple columns reformatted
awk '{print $3, $1}' file

# Conditional
awk '$3 > 100 {print $1}' file

# Format
awk '{printf "%-20s %s\n", $1, $2}' file

# Multi-line scripts (BEGIN, END)
awk 'BEGIN {sum=0} {sum += $1} END {print "Total:", sum}' file
```

### Built-in Variables
- `NR` — current line number
- `NF` — number of fields
- `$0` — whole line
- `$1, $2, ...` — fields
- `FS` — field separator
- `OFS` — output field separator
- `RS` — record separator

## cut, sort, uniq, tr

```bash
cut -d: -f1,3 /etc/passwd          # delimited fields
cut -c1-10 file                    # characters 1-10

sort file
sort -r file                       # reverse
sort -n file                       # numeric
sort -k2 file                      # sort by column 2
sort -t: -k3 -n /etc/passwd        # delimited, numeric, col 3
sort -u file                       # unique while sorting

uniq file                          # remove ADJACENT duplicates (sort first!)
sort file | uniq                   # truly unique
sort file | uniq -c                # with counts
sort file | uniq -c | sort -rn     # sorted by count desc

tr 'a-z' 'A-Z' < file              # lowercase to upper
tr -d '\r' < file                  # strip CRs (DOS to Unix)
tr -s ' ' < file                   # squeeze repeated spaces

paste a b                          # side-by-side merge
paste -d, a b                      # comma-separated
join -t: -1 1 -2 1 a b             # SQL-style join
```

## jq for JSON

```bash
# Pretty-print
echo '{"a":1}' | jq

# Extract value
jq '.name' data.json
jq '.users[0].name' data.json
jq '.users[].name' data.json       # all names

# Filter
jq '.users[] | select(.age > 30)' data.json
jq '.[] | select(.status == "active")' data.json

# Transform
jq '.users | map({id: .id, name: .name})' data.json
jq '{count: length}' data.json

# Multiple output (raw)
jq -r '.users[].name' data.json    # no JSON quotes

# Conditional output
jq 'if .x > 0 then "pos" else "neg" end' data.json

# K8s practical examples
kubectl get pods -o json | jq '.items[] | {name: .metadata.name, status: .status.phase}'
kubectl get nodes -o json | jq '.items[] | {name: .metadata.name, cpu: .status.allocatable.cpu}'

# AWS CLI integration
aws ec2 describe-instances | jq '.Reservations[].Instances[] | {id: .InstanceId, state: .State.Name}'
```

## yq for YAML

Mike Farah's yq (Go-based) — the dominant version:

```bash
yq '.metadata.name' deployment.yaml
yq '.spec.containers[].image' pod.yaml
yq '.spec.replicas = 5' deployment.yaml    # set
yq -i '.spec.replicas = 5' deployment.yaml # in-place
yq -o json deployment.yaml > deployment.json
```

## Composing the Tools

```bash
# Top 10 client IPs from nginx access log
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10

# Find errors per service from JSON logs
jq -r 'select(.level=="error") | .service' logs.json | sort | uniq -c | sort -rn

# Lines containing pattern, plus their timestamp
grep "5xx" access.log | awk '{print $4, $7, $9}' | sort | uniq -c

# K8s: pods using > 80% memory
kubectl top pods --no-headers | awk '{
  gsub("Mi","",$3); gsub("Mi","",$4);
  pct = ($3/$4)*100;
  if (pct > 80) printf "%-30s %5.1f%%\n", $1, pct
}'

# Find files modified in last hour and what changed
find . -mmin -60 -type f | xargs -I{} sh -c 'echo "--- {} ---"; ls -la {}'
```

## Interview Themes

- "Find the top 10 IPs in this log file" (awk + sort + uniq)
- "Replace all occurrences of X with Y in 1000 files" (sed + find/xargs)
- "Parse this JSON and extract Y" (jq)
- "What's the difference between cut, awk, sed for column extraction?"
- "Why use ripgrep over grep?"
