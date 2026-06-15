# L04/C04/T04 — Dry-Run, Idempotency, Atomic Operations

## Learning Objectives

- Add dry-run mode safely
- Write idempotent scripts
- Perform atomic file writes

## Dry-Run

Print what would happen without doing it.

```bash
DRY_RUN=${DRY_RUN:-false}

run() {
    if $DRY_RUN; then
        echo "DRY-RUN: $*" >&2
    else
        "$@"
    fi
}

run rm -rf "$DIR"
run kubectl delete pod "$pod"
```

Use `run` wrapper for destructive operations.

## Idempotency

Re-running script should be safe.

### Common Patterns

```bash
# Bad: errors if exists
mkdir /opt/myapp

# Good: idempotent
mkdir -p /opt/myapp
```

```bash
# Bad: appends every time
echo "line" >> /etc/config

# Good: check before
grep -qxF "line" /etc/config || echo "line" >> /etc/config
```

```bash
# Bad: replaces if exists
ln -s /target /link

# Good
[[ -L /link ]] || ln -s /target /link
```

```bash
# Bad: tries to add even if present
usermod -a -G docker alice

# Good: check
groups alice | grep -q docker || usermod -a -G docker alice
```

## Idempotent Apt/Yum

```bash
# apt/dnf are idempotent for install
apt-get install -y nginx       # OK to re-run

# But this isn't:
apt-get install -y nginx && systemctl enable nginx

# Better:
apt-get install -y nginx
systemctl enable nginx          # also idempotent (no-op if already)
```

## Atomic File Write

Write to temp file; rename atomically.

```bash
tmp=$(mktemp /etc/config.XXXXXX)
trap 'rm -f "$tmp"' EXIT

generate_content > "$tmp"
mv "$tmp" /etc/config           # atomic on same filesystem
```

`mv` (rename) is atomic on same FS. Half-written file never visible.

## Locking

Prevent concurrent runs.

```bash
LOCK=/var/run/myscript.lock

acquire() {
    exec 200>"$LOCK"
    flock -n 200 || { echo "Already running"; exit 1; }
    echo $$ > "$LOCK"
}

acquire
# Critical section
# flock auto-releases on FD close (script end)
```

Or pid-based:
```bash
LOCK=/var/run/myscript.pid

if [[ -f "$LOCK" ]]; then
    if kill -0 "$(cat "$LOCK")" 2>/dev/null; then
        echo "Already running (PID $(cat "$LOCK"))"
        exit 1
    fi
    rm "$LOCK"      # stale
fi

echo $$ > "$LOCK"
trap 'rm -f "$LOCK"' EXIT
```

## Symbolic Links Atomically

For zero-downtime config swap:
```bash
ln -sfn /etc/app/v2 /etc/app/current
```

`-f` force; `-n` don't follow existing symlink. Old and new app versions coexist; switch via symlink update.

## Database Migrations

For DB scripts:
```sql
-- Idempotent
CREATE TABLE IF NOT EXISTS users (...);
ALTER TABLE users ADD COLUMN IF NOT EXISTS email TEXT;
INSERT INTO config VALUES ('key', 'value') ON CONFLICT DO NOTHING;
```

## Check Before Action

```bash
needs_update() {
    [[ "$1" -nt "$2" ]]
}

if needs_update src.tmpl /etc/config; then
    render src.tmpl > /etc/config
fi
```

## Idempotent Loop

```bash
for user in "${users[@]}"; do
    if id "$user" &>/dev/null; then
        log "user $user exists; skipping"
        continue
    fi
    useradd "$user"
done
```

## Real Examples

### Add User to Group
```bash
add_user_to_group() {
    local user=$1 group=$2
    if id "$user" | grep -qw "$group"; then
        log "$user already in $group"
        return 0
    fi
    usermod -aG "$group" "$user"
}
```

### Replace Config Section
```bash
replace_section() {
    local file=$1 marker=$2 content=$3
    if grep -q "# BEGIN $marker" "$file"; then
        sed -i "/# BEGIN $marker/,/# END $marker/d" "$file"
    fi
    cat >> "$file" <<EOF
# BEGIN $marker
$content
# END $marker
EOF
}
```

### State Check
```bash
running_pid() {
    [[ -f /var/run/myapp.pid ]] && cat /var/run/myapp.pid
}

start_app() {
    local pid
    pid=$(running_pid)
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
        log "already running (PID $pid)"
        return 0
    fi
    /opt/app/run &
    echo $! > /var/run/myapp.pid
}
```

## Atomic Counter (with flock)

```bash
COUNTER=/var/run/counter
LOCK="$COUNTER.lock"

increment() {
    (
        flock -x 200
        local n=$(cat "$COUNTER" 2>/dev/null || echo 0)
        echo $((n + 1)) > "$COUNTER"
    ) 200>"$LOCK"
}
```

## Common Mistakes

- **No check before action**: scripts fail on re-run
- **Mid-script crash**: leaves partial state
- **No locking**: concurrent runs conflict
- **`>` mid-write**: file appears half-written

## Testing Idempotency

Run script twice. Verify:
- Second run completes (no errors)
- Final state matches first run
- Side effects same (or none)

## Best Practices

- Route every mutating action through a `run` wrapper that honors `DRY_RUN`, so previewing is uniform and destructive ops are visible.
- Make operations idempotent by construction: `mkdir -p`, `ln -sfn`, `grep -qxF || append`, `INSERT ... ON CONFLICT DO NOTHING`.
- Write files atomically: render to a temp file on the same filesystem, then `mv` into place so readers never see a half-written file.
- Guard against concurrent runs with `flock` on a dedicated FD (auto-released on exit) rather than racy `[[ -f lock ]]` checks.
- Check-before-act on state changes (user in group? symlink present? service enabled?) so the second run is a clean no-op.
- Test idempotency explicitly: run the script twice and assert the second run makes no changes and exits cleanly.

## Quick Refs

```bash
# Dry-run wrapper
DRY_RUN=${DRY_RUN:-false}
run() { if $DRY_RUN; then echo "DRY-RUN: $*" >&2; else "$@"; fi; }
run rm -rf "$dir"

# Idempotent primitives
mkdir -p /opt/app                                   # no error if it exists
ln -sfn /etc/app/v2 /etc/app/current                # atomic symlink swap
grep -qxF "line" /etc/conf || echo "line" >> /etc/conf   # append once
id -nG "$user" | grep -qw docker || usermod -aG docker "$user"

# Atomic file write (same filesystem!)
tmp=$(mktemp "$(dirname "$dst")/.tmp.XXXXXX")
trap 'rm -f "$tmp"' EXIT
render > "$tmp" && mv "$tmp" "$dst"

# Locking with flock (released on FD close at exit)
exec 200>/var/run/myjob.lock
flock -n 200 || { echo "already running" >&2; exit 1; }

# Idempotent SQL
# CREATE TABLE IF NOT EXISTS ...;
# ALTER TABLE t ADD COLUMN IF NOT EXISTS c TEXT;
# INSERT ... ON CONFLICT DO NOTHING;

# Prove it: run twice, expect no second-run changes
./setup.sh && ./setup.sh
```

## Interview Prep

**Junior**: "Make this script safe to re-run."

**Mid**: "Atomic file write — how?"

**Senior**: "Prevent concurrent runs."

**Staff**: "Cluster of nodes runs same script via cron. Lock?"

## Next Topic

→ [T05 — ShellCheck and Style Guides](T05-Shellcheck.md)
