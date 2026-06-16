# L04/C01/T01 — Shells: bash, zsh, fish, sh, dash

## Learning Objectives

- Compare common shells
- Choose right shell for scripting vs interactive
- Recognize POSIX compatibility levels

## Common Shells

| Shell | Path | Use |
|---|---|---|
| bash | /bin/bash | Default Linux interactive + scripting |
| sh | /bin/sh | POSIX scripting; symlink to bash/dash |
| dash | /bin/dash | Lightweight POSIX shell; Debian default `/bin/sh` |
| zsh | /bin/zsh | macOS default; pleasant interactive |
| fish | /usr/local/bin/fish | User-friendly; NOT POSIX |
| ash | /bin/ash | Alpine default; very minimal |
| ksh | /bin/ksh | Korn shell; legacy |
| pwsh | PowerShell | Microsoft; cross-platform |

## bash

The de facto Linux shell. Most scripts target it. Features:
- Job control
- Arrays + associative arrays
- Process substitution
- Brace expansion
- Tab completion
- `[[ ]]` extended test

## sh (POSIX)

The lowest common denominator. Strictly POSIX. Most portable but limited:
- No arrays in pure POSIX (some dash extensions have them)
- No `[[ ]]` test
- No process substitution
- No `function` keyword (use `name() { ... }`)

Use `#!/bin/sh` only if you need to run on minimal systems (Alpine, busybox, embedded).

## dash

Debian Almquist Shell. Strict POSIX. Fast.
- Default for `/bin/sh` on Debian/Ubuntu since ~2009
- ~5× faster than bash for script startup
- Lacks bashisms (arrays, `[[`, etc.)

```bash
# This works in bash but NOT dash:
[[ "$x" == "1" ]]  # → syntax error in dash
```

## zsh

macOS default since Catalina. Bash-compatible mostly + extensions:
- Better tab completion
- Plugins (oh-my-zsh)
- Better array handling
- Globbing extensions

Bash scripts mostly work. zsh scripts not always portable.

## fish

Friendly shell. NOT POSIX. Different syntax:
- No `$?`; use `echo $status`
- No `2>&1`; use `2>&1` (different model)
- No `[[ ]]`

Great for interactive use; bad for portable scripts.

## Choosing for Scripts

### Recommendation
```bash
#!/usr/bin/env bash
set -euo pipefail
```

Why:
- `env bash` finds bash wherever it is (Linux, macOS)
- bash widely available
- Modern features (arrays, `[[ ]]`)
- Strict mode catches common errors

### When sh
Only when:
- Targeting Alpine containers (often no bash)
- Embedded systems
- Maximum portability required

Stick to POSIX features only. Use `shellcheck -s sh` to verify.

## Verifying What `/bin/sh` Points To

```bash
ls -l /bin/sh
# Ubuntu: → /bin/dash
# CentOS/RHEL: → /bin/bash (with POSIX mode)
# Alpine: BusyBox ash
```

A "POSIX-only" script on Ubuntu uses dash; same script on RHEL uses bash. Different behaviors possible.

## bash Version Considerations

- bash 3.2: macOS default (very old, missing features)
- bash 4.0+: associative arrays, `mapfile`, `coproc`
- bash 4.4+: `${var@U}`, `nameref` improvements
- bash 5.0+: minor improvements

macOS ships 3.2 by default (Apple chose due to licensing). For modern bash: `brew install bash`.

## Common Shell Differences

```bash
# bash/zsh: works
arr=(a b c)
echo "${arr[1]}"   # b

# dash: fails
arr=(a b c)        # syntax error
```

```bash
# bash: works
if [[ "$x" =~ ^[0-9]+$ ]]; then ... fi

# dash: fails (no [[)
case "$x" in
    *[!0-9]* | "") echo "not number" ;;
    *) echo "number" ;;
esac
```

## Container Implications

Alpine uses BusyBox ash:
- Minimal; many bash features missing
- `apk add bash` to install
- Or stick to POSIX in scripts

Common error: write bash script; assume runs in Alpine container; fails.

## What to Use

### Daily Interactive
- macOS: zsh (default) or bash via brew
- Linux: bash or zsh

### Scripts You Write
- bash with `#!/usr/bin/env bash` + `set -euo pipefail`

### Scripts for Distribution
- POSIX sh if portability critical
- bash otherwise (most systems have it)

## Operations

```bash
# What shell am I in?
echo $0
ps -p $$

# Available shells
cat /etc/shells

# Change default shell
chsh -s /usr/bin/zsh
```

## Common Mistakes

- **Assuming `#!/bin/sh` runs bash**: on Debian/Ubuntu `/bin/sh` is dash, on Alpine it is BusyBox ash — bashisms (`[[ ]]`, arrays, `source`) silently break.
- **Shipping bash scripts into Alpine images**: the base image has no bash; the script dies on the first run. Either `apk add --no-cache bash` or write strict POSIX `sh`.
- **Developing on macOS bash 3.2 and deploying to Linux bash 5**: features like `mapfile`, `${var,,}`, and `wait -n` exist on the target but not your laptop, so bugs surface only in prod.
- **Hardcoding `#!/bin/bash`**: bash lives at `/usr/local/bin/bash` (Homebrew) or `/usr/bin/bash` on some distros; prefer `#!/usr/bin/env bash`.
- **Testing portability with `sh script.sh`**: that uses your login `/bin/sh`, not the deploy target's; lint with `shellcheck -s sh` instead.

## Best Practices

- Use `#!/usr/bin/env bash` plus `set -euo pipefail` as the default header for anything beyond a throwaway one-liner.
- Pick the shell by audience: bash for scripts you control, strict POSIX `sh` only when you must run on minimal/embedded systems.
- Declare the intended shell to ShellCheck (`# shellcheck shell=bash` or `-s sh`) so the linter matches the real interpreter.
- Keep interactive-shell choice (zsh, fish) separate from script-shell choice — never write production scripts in fish.
- Detect, don't assume: check `command -v bash` or `ls -l /bin/sh` in setup steps rather than trusting a fixed path.
- On macOS, `brew install bash` and reference it explicitly when you need bash 4+/5 features locally.

## Quick Refs

```bash
# Which shell is running this script / session?
echo "$0"              # script/shell name
ps -p $$ -o comm=      # process command of current shell
readlink -f /bin/sh    # what /bin/sh actually points to

# bash version (feature gating)
echo "$BASH_VERSION"
(( BASH_VERSINFO[0] >= 4 )) || { echo "need bash 4+"; exit 1; }

# List installed shells / change default
cat /etc/shells
chsh -s "$(command -v zsh)"

# Portability checks
shellcheck -s sh script.sh     # strict POSIX lint
shellcheck -s bash script.sh   # treat as bash
bash --posix -n script.sh      # POSIX-mode syntax check

# Run a snippet under different shells
for sh in sh dash bash zsh; do command -v "$sh" >/dev/null && "$sh" -c 'echo "$0 ok"'; done
```

## Interview Prep

**Junior**: "What's the difference between bash and sh?"

**Mid**: "Why might a script work on RHEL but fail on Ubuntu?"

**Senior**: "Why isn't bash 5.0 default on macOS?"

## Next Topic

→ [T02 — Variables, Quoting, Expansion](T02-Variables-Quoting.md)
