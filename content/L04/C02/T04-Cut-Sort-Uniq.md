# L04/C02/T04 — cut, sort, uniq, tr, paste, join

## Learning Objectives

- Apply small tools to compose pipelines
- Recognize when to use each

## cut

Extract columns.

```bash
cut -d: -f1 /etc/passwd            # field 1 (delimiter :)
cut -d: -f1,3 /etc/passwd          # fields 1 and 3
cut -d: -f1-3 /etc/passwd          # 1 through 3
cut -d: -f1- /etc/passwd            # 1 to end
cut -c1-10 file                    # chars 1-10
cut -c1,5,10 file                  # chars 1, 5, 10
```

Limitations:
- Doesn't collapse multiple spaces (delimiter is exactly 1 char)
- For variable whitespace: use awk

## sort

Sort lines.

```bash
sort file                         # alphabetical (lexicographic)
sort -r file                      # reverse
sort -n file                      # numeric
sort -h file                      # human-readable (1k, 1M, 1G)
sort -k2 file                     # sort by column 2
sort -t: -k3 -n /etc/passwd       # delimiter :, key column 3, numeric
sort -u file                      # unique
sort -R file                      # random shuffle
sort -c file                      # check if already sorted
sort -m sorted1 sorted2 > out     # merge already-sorted files
```

Performance:
- Large files: uses temp files
- `LC_ALL=C sort` faster for ASCII (skip locale)
- Multi-threaded `sort` with --parallel

## uniq

Remove ADJACENT duplicates. (sort first!)

```bash
sort file | uniq                  # truly unique
sort file | uniq -c               # with counts
sort file | uniq -c | sort -rn    # sorted by count desc
uniq -d file                      # only duplicates
uniq -u file                      # only unique (non-duplicated)
```

`uniq` only compares adjacent lines. `sort | uniq` is the idiom.

## tr (Translate)

Character-by-character translation.

```bash
tr 'a-z' 'A-Z' < file              # lowercase to uppercase
tr -d '\r' < file                  # delete CR chars (DOS → Unix)
tr -d '[:punct:]' < file           # remove punctuation
tr -s ' ' < file                   # squeeze repeated spaces to one
tr ' ' '\n' < file                 # spaces to newlines
tr -c 'a-zA-Z\n' ' '               # complement (NOT alphanumeric → space)
```

Character classes:
- `[:alpha:]` letters
- `[:digit:]` digits
- `[:alnum:]` alphanumeric
- `[:space:]` whitespace
- `[:punct:]` punctuation
- `[:upper:]` uppercase
- `[:lower:]` lowercase

## paste

Side-by-side merge.

```bash
paste a b                         # tab-separated columns
paste -d, a b                     # comma-separated
paste -s file                     # serial: join lines of one file
paste -s -d, file                 # join with comma
```

```bash
# Example: combine names + ages
$ cat names
alice
bob
carol

$ cat ages
30
25
28

$ paste names ages
alice    30
bob      25
carol    28
```

## join

SQL-style join on sorted files.

```bash
join -t: -1 1 -2 1 file1 file2
```

- `-t:` delimiter
- `-1 N` join column in file 1
- `-2 N` join column in file 2

Files must be sorted on join column.

```bash
sort -t: -k1 users > users.sorted
sort -t: -k1 perms > perms.sorted
join -t: users.sorted perms.sorted
```

For complex joins: SQL or Python.

## Composition Examples

### Top 10 IPs
```bash
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10
```

### Unique Users by Domain
```bash
cut -d@ -f2 emails.txt | sort -u
```

### Disk Usage Top 10
```bash
du -h /var/log/* | sort -rh | head -10
```

### Lines Common to Two Files
```bash
sort a > a.sorted; sort b > b.sorted
comm -12 a.sorted b.sorted
```

`comm` shows:
- col 1: lines only in file 1
- col 2: lines only in file 2
- col 3: common
- `-N` suppresses column N

### Count Word Frequencies
```bash
tr ' ' '\n' < file | sort | uniq -c | sort -rn | head
```

### CSV Transformations
```bash
# Convert tab-separated to CSV (with quoted fields)
sed 's/\t/","/g; s/^/"/; s/$/"/' file.tsv
```

## head and tail

```bash
head file                         # first 10 lines
head -n 20 file                   # first 20
head -c 100 file                  # first 100 bytes
tail file                         # last 10
tail -n 20 file
tail -f file                      # follow (live)
tail -n +5 file                   # from line 5 to end
```

## wc (Word Count)

```bash
wc file                           # lines, words, chars
wc -l file                        # lines only
wc -w file                        # words
wc -c file                        # bytes
wc -m file                        # chars (UTF-8 aware)
```

## tee

Write to file AND stdout.

```bash
cmd | tee out.txt                 # see output AND save
cmd | tee -a out.txt              # append
sudo tee /etc/sysctl.conf <<<"line"   # write privileged
```

## xargs (covered more in T05)

```bash
echo "a b c" | xargs -n 1         # one arg per line
ls *.log | xargs gzip             # gzip each file
find . -name "*.tmp" -print0 | xargs -0 rm    # NUL-delimited for safety
```

## comm

Compare sorted files.
```bash
comm sorted1 sorted2
comm -12 sorted1 sorted2          # common
comm -23 sorted1 sorted2          # only in sorted1
```

## Examples in Production

### Find services using most memory
```bash
ps -eo pid,rss,comm --sort=-rss | head -10
```

### Top 10 largest files
```bash
find . -type f -printf '%s %p\n' | sort -rn | head -10
```

### Top 10 directories by size
```bash
du -h --max-depth=1 /var | sort -rh | head -10
```

### Compare lists of users
```bash
comm -3 <(cut -d: -f1 /etc/passwd | sort) <(cut -d: -f1 /etc/shadow | sort)
```

## Common Mistakes

- **`uniq` without `sort` first**: `uniq` only collapses *adjacent* duplicates, so unsorted input keeps repeats. The idiom is `sort | uniq` (or `sort -u`).
- **`cut` on whitespace-aligned columns**: `cut -d' '` treats every single space as a delimiter, so runs of spaces create empty fields. Use `awk` or `tr -s ' '` first.
- **Sorting numbers lexically**: plain `sort` puts `10` before `2`. Use `sort -n` (or `-h` for `1K`/`2M`) for numeric order.
- **`join`/`comm` on unsorted files**: both require inputs sorted on the join key, or they silently miss matches.
- **Locale slowing/altering sorts**: a UTF-8 locale changes collation and is slower; prefix `LC_ALL=C sort` for byte-order, ASCII-fast sorting.
- **Counting with `wc -l` when the last line has no newline**: it under-counts by one; `grep -c ''` or `awk 'END{print NR}'` is safer.

## Best Practices

- Compose small tools left-to-right; the canonical "rank by frequency" pipeline is `... | sort | uniq -c | sort -rn`.
- Use `sort -u` instead of `sort | uniq` when you only need uniqueness (one process, less I/O).
- Set `LC_ALL=C` for large ASCII sorts to gain speed and predictable byte ordering.
- Pick `cut` for fast fixed-delimiter extraction, `awk` when delimiters vary or you need logic.
- Always sort inputs to `join`/`comm` on the same key first, and use `-t` to match the delimiter.
- NUL-delimit filename pipelines (`find -print0 | sort -z | ...`) so spaces and newlines in names don't break parsing.

## Quick Refs

```bash
# cut — extract fields/columns
cut -d: -f1,7 /etc/passwd     # delimited fields
cut -c1-10 file               # character ranges

# sort
sort -u file                  # unique, sorted
sort -n file                  # numeric         sort -h file   # 1K/2M/3G
sort -rn file                 # numeric, descending
sort -t: -k3 -n file          # by 3rd field, numeric, ':'-delimited
LC_ALL=C sort big.txt         # fast ASCII/byte sort

# uniq (input must be sorted)
sort f | uniq -c              # prefix counts
sort f | uniq -d              # only duplicated lines
sort f | uniq -u              # only non-duplicated lines

# frequency ranking (top 10)
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head

# tr — translate/squeeze/delete
tr 'a-z' 'A-Z' < f            # upper-case
tr -s ' ' < f                 # squeeze repeated spaces
tr -d '\r' < f                # strip CR

# set ops on sorted files
comm -12 <(sort a) <(sort b)  # lines common to both
comm -23 <(sort a) <(sort b)  # only in a
join -t: <(sort a) <(sort b)  # relational join on field 1

# misc
paste -sd, file               # join lines with commas
wc -l file                    # line count
column -t file                # align into a table
```

## Interview Prep

**Junior**: "Cut field 1 from /etc/passwd."

**Mid**: "Top 10 disk hogs."

**Senior**: "Compose pipeline to find unique error types."

## Next Topic

→ [T05 — jq for JSON, yq for YAML](T05-Jq-Yq.md)
