# L04/C02/T03 — awk (Programming with awk)

## Learning Objectives

- Process columns of data
- Aggregate with awk
- Use BEGIN / END blocks

## Basic Structure

```bash
awk 'pattern { action }' file
```

If pattern omitted: action runs for every line. If action omitted: print matching lines.

## Fields

Each line split into fields by FS (default: whitespace).
- `$0` = whole line
- `$1`, `$2`, ... = fields
- `NF` = number of fields
- `$NF` = last field

```bash
awk '{print $1}' file              # first column
awk '{print $1, $3}' file          # 1st and 3rd
awk '{print $NF}' file             # last
awk '{print $(NF-1)}' file         # second-to-last
```

## Field Separator

```bash
awk -F: '{print $1}' /etc/passwd
awk -F'\t' '{print $1}' file       # tab
awk 'BEGIN{FS=","} {print $1}' file
```

## Conditions

```bash
awk '/pattern/ {print}' file        # matching lines
awk 'NR==5' file                    # line 5
awk 'NR>=5 && NR<=10' file          # range
awk 'NF==3' file                    # exactly 3 fields
awk 'NF>3' file                     # more than 3
awk '$3 > 100' file                 # column 3 > 100
awk '$1 == "Alice"' file            # column 1 equals
awk '$1 ~ /^A/' file                # column 1 starts with A
```

## BEGIN and END

```bash
awk 'BEGIN {print "start"} {print} END {print "end"}' file
```

- BEGIN: before any line
- END: after all lines

Useful for headers + totals.

## Built-in Variables

- `NR`: record number (line)
- `NF`: number of fields
- `FS`: field separator (input)
- `OFS`: output field separator (default " ")
- `RS`: record separator (default newline)
- `ORS`: output record separator
- `FILENAME`: current file
- `FNR`: line in current file (when multiple files)

## Common Patterns

### Sum a Column
```bash
awk '{sum += $1} END {print sum}' file
```

### Average
```bash
awk '{sum += $1; count++} END {print sum/count}' file
```

### Max / Min
```bash
awk 'NR==1 {max=$1} $1>max {max=$1} END {print max}' file
```

### Unique Values
```bash
awk '{print $1}' file | sort -u
# or
awk '!seen[$1]++' file              # remove duplicate lines based on column 1
```

### Top 10 IPs in Access Log
```bash
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10
```

### Print Specific Columns Reformatted
```bash
awk '{printf "%-20s %10s\n", $1, $2}' file
```

### Conditional Print
```bash
awk '$3 == "ERROR" {print $1, $2}' file
awk 'NR>1 {print}' file               # skip header
```

### Range
```bash
awk '/^BEGIN/,/^END/' file
```

## printf

```bash
awk '{printf "%-15s %5d\n", $1, $2}' file
```

Like C's printf:
- `%s` string
- `%d` integer
- `%f` float
- `%-15s` left-aligned 15-char string
- `%5.2f` 5 wide, 2 decimal

## Multi-Action

```bash
awk '
    /ERROR/ {errors++}
    /WARN/ {warns++}
    END {
        print "Errors:", errors
        print "Warnings:", warns
    }
' file
```

## Arrays (Associative)

```bash
awk '{counts[$1]++} END {for (key in counts) print counts[key], key}' file
```

```bash
# Sum by category
awk '{sums[$1] += $2} END {for (k in sums) print k, sums[k]}' file
```

## Field Manipulation

```bash
awk '{$1=$1; print}' file              # rewrite line (reformats spacing)
awk 'BEGIN{OFS="\t"} {$1=$1; print}' file   # convert to tab-separated
awk '{print $1 "/" $2}' file           # concatenate with delimiter
```

## Computing on Multiple Files

```bash
awk '
  FNR==1 {print "--- " FILENAME " ---"}
  {print}
' file1 file2 file3
```

## awk vs cut vs sed

| | Best for |
|---|---|
| `cut` | Fixed-position or delimited field extraction (fastest) |
| `awk` | Field-based with logic, math, conditions |
| `sed` | Line-based substitution |

For extracting column 3: `cut` is simpler. For "column 3 > 100 then print column 1": awk.

## Examples in Production

### Log analysis
```bash
awk '/POST/ && $7 > 500 {print $1, $7}' access.log
```

### Convert CSV to JSON
```bash
awk -F, 'NR==1{for(i=1;i<=NF;i++) h[i]=$i; next}
         {printf "{"; for(i=1;i<=NF;i++) printf "\"%s\":\"%s\"%s", h[i], $i, i<NF?",":""; print "}"}' file.csv
```

### K8s Pod Memory Usage Percentage
```bash
kubectl top pods --no-headers | awk '{
    gsub("Mi","",$3); gsub("Mi","",$4)
    if ($4 > 0) printf "%-40s %5.1f%%\n", $1, ($3/$4)*100
}' | sort -k2 -rn
```

## When to Switch to Python

awk one-liners > python for simple processing.
For:
- Complex data structures
- JSON parsing
- HTTP calls
- Multi-step logic

→ Python.

## Operations

```bash
gawk '{...}' file        # GNU awk (more features)
mawk '{...}' file        # fast Mike's awk
nawk '{...}' file        # original new awk
```

GNU awk has additional features (regex, time functions). Most modern systems have `gawk` aliased to `awk`.

## Common Mistakes

- **Quoting the program in double quotes**: `awk "{print $1}"` lets the shell expand `$1` to nothing. Always single-quote the awk script.
- **`$1` vs the shell's `$1`**: inside `'...'` the `$1` is awk's first field; to pass a shell value, use `-v var="$val"` and reference `var`.
- **String vs numeric comparison surprises**: `$1 == "10"` is a string match; for numbers use `$1 + 0 == 10` or `$1 > 100` so `"010"` and `"10"` compare numerically.
- **Forgetting `OFS` when rebuilding lines**: changing `FS` alone doesn't change output spacing — set `OFS` and touch a field (`$1=$1`) to reformat.
- **Assuming whitespace `FS` for tabs/CSV**: default `FS` collapses runs of spaces; set `-F'\t'` or `-F,` explicitly, and note commas inside quoted CSV fields need a real parser.
- **Uninitialized variables**: awk treats an unset variable as `0`/`""` silently, so a typo'd accumulator gives wrong totals with no error.

## Best Practices

- Single-quote the program, and pass external values via `-v name=value` rather than string interpolation.
- Set `FS`/`OFS` in a `BEGIN` block (or with `-F`) so intent is explicit and the script self-documents.
- Use `BEGIN`/`END` for headers, totals, and one-time setup; accumulate into associative arrays for group-by aggregation.
- Prefer a single awk pass over chains of `grep | cut | sort` when you need field logic plus arithmetic — it is faster and clearer.
- Use `printf` (not `print`) for aligned, formatted columnar output.
- Know when to stop: once you need JSON, nested data, or multi-step logic, switch to Python.

## Quick Refs

```bash
# Fields & records
awk '{print $1, $NF}' file        # first and last field
awk -F: '{print $1}' /etc/passwd  # custom separator
awk 'NR>1' file                   # skip header row
awk 'NF' file                     # drop blank lines (NF>0)

# Filtering
awk '$3 > 100' file               # numeric column filter
awk '$1 ~ /^web/' file            # regex on a field
awk '/ERROR/{print $2}' file      # pattern + action

# Aggregation
awk '{s+=$1} END{print s}' file               # sum a column
awk '{s+=$1;n++} END{print s/n}' file         # average
awk '{c[$1]++} END{for(k in c)print c[k],k}' file   # count by key
awk '{sum[$1]+=$2} END{for(k in sum)print k,sum[k]}' file  # sum by key
awk '!seen[$0]++' file            # dedup, preserve order

# Pass shell values in safely
threshold=500
awk -v t="$threshold" '$7 > t {print $1, $7}' access.log

# Formatted output & reformatting
awk '{printf "%-20s %8.2f\n", $1, $2}' file
awk 'BEGIN{OFS="\t"} {$1=$1; print}' file   # space- to tab-separated
```

## Interview Prep

**Mid**: "Sum column 2 grouped by column 1."

**Senior**: "Top 10 IPs in nginx access log."

**Staff**: "Parse CSV; output JSON via awk."

## Next Topic

→ [T04 — cut, sort, uniq, tr, paste, join](T04-Cut-Sort-Uniq.md)
