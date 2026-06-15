# L04/C03/T01 — Arrays, Associative Arrays

## Learning Objectives

- Use indexed and associative arrays
- Iterate safely
- Convert between strings and arrays

## Indexed Arrays

```bash
arr=(apple banana cherry)
echo "${arr[0]}"                 # apple
echo "${arr[@]}"                 # all
echo "${#arr[@]}"                # count
echo "${!arr[@]}"                # indices
echo "${arr[@]:1:2}"             # slice (offset 1, length 2)

arr+=(date)                      # append
arr[10]="other"                  # sparse OK
unset 'arr[1]'                   # remove (doesn't shift)
```

### Iterate
```bash
for item in "${arr[@]}"; do echo "$item"; done

# With index
for i in "${!arr[@]}"; do echo "$i: ${arr[$i]}"; done
```

### Build from Command
```bash
mapfile -t files < <(ls *.log)
readarray -t lines < file.txt
```

`mapfile` is bash 4+. `-t` strips newlines.

### Build from String
```bash
str="a b c d"
arr=( $str )                     # word split (unquoted)

# Safer with IFS
IFS=, read -ra arr <<< "a,b,c,d"
```

## Associative Arrays (bash 4+)

```bash
declare -A map
map[alice]=30
map[bob]=25
echo "${map[alice]}"

# All keys
for k in "${!map[@]}"; do
    echo "$k -> ${map[$k]}"
done

# Count
echo "${#map[@]}"

# Check key
[[ -v map[alice] ]] && echo "exists"
[[ -n "${map[alice]+x}" ]] && echo "exists"
```

## Common Patterns

### Dedup
```bash
declare -A seen
for x in "${items[@]}"; do
    [[ -z "${seen[$x]}" ]] && {
        seen[$x]=1
        unique+=("$x")
    }
done
```

### Count
```bash
declare -A counts
for x in "${items[@]}"; do
    ((counts[$x]++))
done
```

### Multi-Value (parallel arrays)
```bash
names=(alice bob carol)
ages=(30 25 28)
for i in "${!names[@]}"; do
    echo "${names[$i]} is ${ages[$i]}"
done
```

## Slicing

```bash
arr=(a b c d e f)
echo "${arr[@]:0:3}"             # a b c
echo "${arr[@]:3}"               # d e f
echo "${arr[@]: -2}"             # e f (space before -)
```

## String Operations on Each Element

```bash
arr=(apple banana cherry)
echo "${arr[@]^^}"               # uppercase all
echo "${arr[@]/a/A}"             # replace first 'a' in each
echo "${arr[@]/#/PREFIX_}"        # prepend
```

## Common Mistakes

### Quoting
```bash
arr=("hello world" "foo bar")
for item in ${arr[@]}; do echo "$item"; done    # WRONG: word splits
for item in "${arr[@]}"; do echo "$item"; done  # CORRECT
```

### Sparse Arrays
```bash
arr[5]="x"
echo "${arr[@]}"                 # just "x" — others empty
echo "${#arr[@]}"                # 1 (count of defined)
echo "${!arr[@]}"                # 5 (only index)
```

### Copying
```bash
a=(1 2 3)
b=("${a[@]}")                    # proper copy
```

## Multidimensional?

bash doesn't have multidimensional arrays. Workarounds:
- Associative array with composite keys: `map["row1,col2"]=...`
- Parallel arrays

For real 2D: use awk or Python.

## Read CSV Into Array

```bash
while IFS=, read -ra fields; do
    echo "First: ${fields[0]}, Second: ${fields[1]}"
done < data.csv
```

## Convert to String

```bash
arr=(a b c)
str="${arr[*]}"                  # "a b c"
str=$(IFS=,; echo "${arr[*]}")   # "a,b,c"
```

`*` joins with first char of IFS; `@` keeps separate.

## Operations

```bash
# Check existence of value
contains() {
    local needle="$1"; shift
    for x in "$@"; do
        [[ "$x" == "$needle" ]] && return 0
    done
    return 1
}

if contains "apple" "${fruits[@]}"; then ...
```

## Best Practices

- Always iterate with the quoted `"${arr[@]}"` form so elements containing spaces stay intact.
- Build arrays from command output with `mapfile -t arr < <(cmd)` instead of unquoted `arr=( $(cmd) )`, which word-splits and globs.
- Declare associative arrays explicitly with `declare -A map` before use (bash 4+); without it, keys are treated as arithmetic.
- Copy arrays with `b=("${a[@]}")` and serialize with a chosen IFS: `joined=$(IFS=,; echo "${a[*]}")`.
- Check counts and indices with `${#arr[@]}` (length) and `${!arr[@]}` (indices) rather than assuming a dense 0..n-1 range — arrays can be sparse.
- Use associative arrays as sets/counters (`seen[$x]=1`, `((count[$x]++))`) to dedup and tally without temp files.

## Quick Refs

```bash
# Indexed arrays
arr=(a b c)
echo "${arr[0]}"        # element
echo "${arr[@]}"        # all elements (quote in real use)
echo "${#arr[@]}"       # count
echo "${!arr[@]}"       # indices
echo "${arr[@]:1:2}"    # slice: offset 1, length 2
arr+=(d)                # append
unset 'arr[1]'          # remove (leaves a gap)

# Iterate
for x in "${arr[@]}"; do echo "$x"; done
for i in "${!arr[@]}"; do echo "$i -> ${arr[$i]}"; done

# Build from input
mapfile -t lines < file            # one element per line, no trailing \n
IFS=, read -ra parts <<< "a,b,c"   # split a string on a delimiter

# Associative arrays (bash 4+)
declare -A m
m[alice]=30; m[bob]=25
echo "${m[alice]}"
for k in "${!m[@]}"; do echo "$k=${m[$k]}"; done
[[ -v m[alice] ]] && echo "key exists"

# Counter / set idioms
declare -A count; for x in "${items[@]}"; do ((count[$x]++)); done
declare -A seen; for x in "${items[@]}"; do [[ ${seen[$x]+_} ]] || { seen[$x]=1; uniq+=("$x"); }; done

# Array <-> string
joined=$(IFS=,; echo "${arr[*]}")  # "a,b,c"
```

## Interview Prep

**Mid**: "Count word frequencies via associative array."

**Senior**: "Read file lines into array safely."

**Staff**: "Detect duplicates without temp files."

## Next Topic

→ [T02 — Process Substitution, Heredocs](T02-Process-Substitution-Heredocs.md)
