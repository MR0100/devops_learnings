# L04/C03/T02 — Process Substitution, Heredocs

## Learning Objectives

- Use process substitution effectively
- Write heredocs for inline content

## Process Substitution

Treat command output as a file: `<(...)`.

```bash
diff <(sort file1) <(sort file2)
comm -12 <(sort a) <(sort b)
join <(sort users) <(sort orders)
```

`<(...)` creates a file descriptor (`/dev/fd/63` or similar) that yields the command's output.

## Common Use Cases

### Compare Sorted Versions
```bash
diff <(sort -u file1) <(sort -u file2)
```

### Avoid Subshell Loss
```bash
# Subshell loses variables
count=0
ls | while read f; do
    ((count++))
done
echo "$count"     # 0 (subshell)

# Process sub keeps current shell
count=0
while IFS= read -r f; do
    ((count++))
done < <(ls)
echo "$count"     # correct
```

### Multi-Output Tee
```bash
generate | tee >(grep ERROR > errors.log) >(grep WARN > warns.log) > /dev/null
```

Three consumers in parallel.

### Compare Remote vs Local
```bash
diff <(ssh remote 'cat /etc/config') /etc/config
```

## Heredocs

Multi-line strings inline.

```bash
cat <<EOF > /etc/myapp.conf
key=value
host=$(hostname)
port=8080
EOF
```

### Expansion Rules

```bash
# EOF unquoted: variables and command substitution expand
cat <<EOF
$USER will get $((5*5)) at $(date)
EOF

# 'EOF' quoted: literal; no expansion
cat <<'EOF'
$USER literally
EOF

# <<- strips leading TABS only (for indented code)
function f() {
    cat <<-EOF
        indented line
        another
    EOF
}
```

`<<-` removes only TABS (not spaces). Useful with indented heredocs.

## Here-Strings

For a single string:
```bash
read -r line <<< "hello world"
echo "$line"
```

Or feed to a command:
```bash
grep "pattern" <<< "string"
bc <<< "5+5"
```

## Real Examples

### Generate K8s manifest
```bash
cat <<EOF > deploy.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: $APP_NAME
  namespace: $NAMESPACE
spec:
  replicas: $REPLICAS
  selector:
    matchLabels:
      app: $APP_NAME
  template:
    metadata:
      labels:
        app: $APP_NAME
    spec:
      containers:
      - name: $APP_NAME
        image: $IMAGE
EOF
```

### Embed SQL
```bash
psql -d mydb <<SQL
SELECT count(*) FROM users WHERE active = true;
SQL
```

### SSH with Commands
```bash
ssh remote bash <<'REMOTE'
echo "running on $HOSTNAME"
cd /opt/app
./restart.sh
REMOTE
```

Note: `'REMOTE'` ensures variables expand on the REMOTE side.

### Multi-line String to Variable
```bash
msg=$(cat <<EOF
Multi-line
content
here
EOF
)
echo "$msg"
```

## Common Mistakes

### Heredoc Inside Function (quoting)
```bash
deploy() {
    cat <<EOF
    Using $1
EOF
}
```

`EOF` must be at start of line (no leading whitespace) unless using `<<-`.

### Variable Expansion Surprise
```bash
cat <<EOF
$undefined           # expands to empty (no error in default)
${100/0}              # arithmetic error
EOF
```

Use `<<'EOF'` to prevent expansion when not wanted.

## Operations

```bash
# Output of two commands diffed
diff <(seq 1 10) <(seq 5 15)

# Sort big file streaming (no temp)
sort huge.txt | uniq -c

# Process two files in parallel
paste <(awk '{print $1}' file1) <(awk '{print $2}' file2)
```

## Combining

```bash
# Multi-file diff
diff <(sort file1) <(sort file2) <(sort file3)   # diff only supports 2; use comm

# Compose with heredoc
psql -d mydb <<SQL > result.txt
SELECT * FROM users;
SQL
```

## Best Practices

- Use `< <(cmd)` to feed a `while read` loop so variables set in the loop survive (a pipe runs the loop in a subshell and loses them).
- Quote the heredoc delimiter (`<<'EOF'`) when you want literal content; leave it unquoted only when you intend `$var` and `$(cmd)` to expand.
- Use `<<-EOF` with leading **tabs** (not spaces) to keep heredocs indented inside functions/blocks; the closing delimiter must sit at column 0.
- Prefer process substitution over temp files for "compare two command outputs" (`diff <(...) <(...)`) — no cleanup, no race.
- For remote execution, quote the delimiter (`ssh host bash <<'EOF'`) so variables expand on the remote side, not locally.
- Remember process substitution is a bashism (`/dev/fd`), not POSIX `sh`; gate it to a bash shebang.

## Quick Refs

```bash
# Process substitution: command output as a file
diff <(sort a) <(sort b)            # compare two streams
comm -12 <(sort a) <(sort b)        # common lines
while IFS= read -r f; do n=$((n+1)); done < <(find . -type f)   # no subshell
generate | tee >(grep ERROR >err.log) >(grep WARN >warn.log) >/dev/null

# Here-string: feed one string to stdin
read -r a b <<< "hello world"
bc <<< "6 * 7"
grep -q foo <<< "$line"

# Heredoc: multi-line stdin
cat <<EOF              # expands $VAR and $(cmd)
host=$(hostname)
EOF

cat <<'EOF'           # literal, no expansion
$HOME stays literal
EOF

func() {
	cat <<-EOF        # <<- strips leading TABS only
		indented but tab-stripped
	EOF
}

# Capture a heredoc into a variable
msg=$(cat <<EOF
line one
line two
EOF
)
```

## Interview Prep

**Mid**: "Process substitution — when?"

**Senior**: "Avoid subshell variable loss in pipe."

**Staff**: "Multi-line YAML in script — best practice."

## Next Topic

→ [T03 — Trap & Signal Handling](T03-Trap-Signals.md)
