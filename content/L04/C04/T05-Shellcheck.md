# L04/C04/T05 — ShellCheck and Style Guides

## Learning Objectives

- Use shellcheck to catch bugs
- Apply consistent style
- Integrate into CI

## ShellCheck

Static analyzer for bash scripts. Catches dozens of common bugs.

```bash
shellcheck script.sh
```

## Sample Output

```
script.sh:5: SC2086: Double quote to prevent globbing and word splitting.
script.sh:7: SC2046: Quote this to prevent word splitting.
```

## Common Findings

### SC2086 — Quote Variables
```bash
rm $file               # warns
rm "$file"             # OK
```

### SC2046 — Quote Substitution
```bash
ls $(get_dir)          # warns
ls "$(get_dir)"        # OK
```

### SC2155 — Declare Separately
```bash
local x=$(may_fail)    # warns: exit code of `local` masks failure

local x
x=$(may_fail)          # correct
```

### SC2128 — Array Without Index
```bash
arr=(a b c)
echo $arr              # prints only "a" — likely bug
echo "${arr[@]}"       # all
```

### SC2154 — Unset Variable
```bash
echo "$undefined"      # warns (with -u also errors at runtime)
```

### SC2034 — Unused Variable
```bash
USED=1
UNUSED=2               # warns
echo "$USED"
```

## Install

```bash
# macOS
brew install shellcheck

# Ubuntu
apt install shellcheck

# Docker
docker run --rm -v "$PWD:/mnt" koalaman/shellcheck script.sh
```

## CI Integration

```yaml
# GitHub Actions
- name: ShellCheck
  uses: ludeeus/action-shellcheck@master
```

Or:
```yaml
- name: ShellCheck
  run: find . -name '*.sh' -exec shellcheck {} +
```

## pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
- repo: https://github.com/koalaman/shellcheck-precommit
  rev: v0.10.0
  hooks:
  - id: shellcheck
```

Catches before commit.

## Disable Specific

For specific rules in script:
```bash
# shellcheck disable=SC2086
echo $intentional_word_split
```

Or globally in `.shellcheckrc`:
```
disable=SC2086
shell=bash
```

## Severity Levels

- `error` — definitely wrong
- `warning` — likely wrong
- `info` — suggestion
- `style` — preference

Filter:
```bash
shellcheck --severity=warning script.sh
```

## Modes

```bash
shellcheck script.sh
shellcheck -s bash script.sh        # treat as bash even if shebang is sh
shellcheck -s sh script.sh          # strict POSIX
shellcheck -x script.sh             # follow source statements
```

## Format

```bash
shellcheck --format=gcc script.sh   # gcc-like output (IDE friendly)
shellcheck --format=json script.sh
shellcheck --format=tty script.sh   # default
```

## Style Guides

### Google Shell Style Guide
- 2-space indentation
- 80-char lines
- Functions: lowercase, snake_case
- Variables: UPPERCASE for globals/env, lowercase for locals
- Use `[[ ]]` not `[ ]`
- Always quote variables
- Use `$()` not backticks

### Recommendations
- `#!/usr/bin/env bash` (not `#!/bin/bash`)
- `set -euo pipefail` at top
- Functions have local variables only
- Constants `readonly`
- Cleanup via trap

## shfmt (Formatter)

```bash
shfmt -i 2 -ci -w script.sh
```

- `-i 2`: 2-space indent
- `-ci`: indent case
- `-w`: write in place

## Code Smells

### Too Long
- > 200 lines: consider splitting into functions
- > 500 lines: consider Python/Go

### Too Many Globals
- Hard to test
- Use functions with parameters

### Lots of `eval`
- Almost always wrong; security risk
- Refactor

### Lots of Conditional Logic
- Bash isn't great for complex business logic
- Consider Python

## Testing Bash Scripts

### bats
```bash
@test "addition works" {
    result=$(./calculate.sh 2 3)
    [ "$result" = "5" ]
}
```

```bash
bats tests/
```

### shunit2
Similar concept, JUnit-style.

For shell scripts in CI: at minimum lint with shellcheck. For critical scripts: write bats tests.

## Example: Production Script Lint Pass

```bash
#!/usr/bin/env bash
# shellcheck disable=SC1090,SC1091
set -euo pipefail
IFS=$'\n\t'

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_PREFIX="[$(basename "$0")]"

log()   { echo "$LOG_PREFIX $*" >&2; }
err()   { echo "$LOG_PREFIX ERROR: $*" >&2; }
fatal() { err "$*"; exit 1; }

main() {
    local arg="${1:-}"
    [[ -z "$arg" ]] && fatal "Argument required"
    log "Processing: $arg"
    process "$arg"
}

process() {
    local input="$1"
    # ... work
}

main "$@"
```

`shellcheck` passes clean on this.

## Operations

```bash
# Lint everything
find . -name '*.sh' -exec shellcheck {} +

# Format
find . -name '*.sh' -exec shfmt -i 2 -ci -w {} \;

# Bats tests
bats tests/
```

## Common Mistakes

- **Blanket-disabling rules**: a top-of-file `# shellcheck disable=SC2086` silences the warning for the whole script, hiding real unquoted-variable bugs. Disable narrowly, one line above the offending statement.
- **Linting with the wrong shell**: if the shebang is `#!/bin/sh` but you mean bash, ShellCheck flags valid bashisms (or misses sh-only issues). Set `-s bash`/`-s sh` or `# shellcheck shell=...`.
- **Not following sourced files**: ShellCheck can't see `source lib.sh` by default, so it warns about "undefined" variables; pass `-x` to follow.
- **Treating `style`/`info` noise as blocking**: failing CI on every stylistic nit causes people to disable the linter; gate CI on `--severity=warning` and fix style separately.
- **Skipping `shfmt`**: relying on manual indentation produces inconsistent diffs; let a formatter own whitespace.
- **No tests for critical scripts**: a clean lint proves syntax, not behavior — important scripts still need `bats`/`shunit2` tests.

## Best Practices

- Run `shellcheck` in CI and as a pre-commit hook so issues are caught before merge, not in production.
- Fix or annotate every finding; when suppressing, use a scoped `# shellcheck disable=SCxxxx` with a comment explaining why.
- Follow the Google Shell Style Guide: `#!/usr/bin/env bash`, `set -euo pipefail`, 2-space indent, `[[ ]]` over `[ ]`, `$()` over backticks, quote everything.
- Format with `shfmt -i 2 -ci -w` so diffs stay about logic, not whitespace.
- Tell the linter the truth: declare the shell (`-s`) and follow sources (`-x`) so results match runtime.
- Add `bats` tests for scripts that gate deploys or mutate state; lint is necessary but not sufficient.

## Quick Refs

```bash
# Run it
shellcheck script.sh
shellcheck -s bash script.sh      # force bash dialect
shellcheck -s sh   script.sh      # strict POSIX
shellcheck -x script.sh           # follow `source`d files
shellcheck --severity=warning script.sh   # ignore info/style
find . -name '*.sh' -exec shellcheck {} +

# Suppress one rule, scoped to the next line
# shellcheck disable=SC2086
echo $intentional_split

# Project config (.shellcheckrc)
# shell=bash
# disable=SC1090,SC1091
# external-sources=true

# Format
shfmt -i 2 -ci -w script.sh       # 2-space indent, indent case, write
shfmt -d script.sh                # show diff only

# Frequently seen rules
# SC2086 quote to prevent splitting/globbing   SC2046 quote $(...)
# SC2155 declare and assign separately          SC2128 array without index
# SC2034 unused variable                        SC2164 cd without || exit

# Tests
bats tests/

# CI (GitHub Actions)
# - uses: ludeeus/action-shellcheck@master
```

## Interview Prep

**Junior**: "Why use shellcheck?"

**Mid**: "Common shellcheck warnings and fixes."

**Senior**: "CI integration for script quality."

## Next Chapter

→ [C05 — Beyond Bash](../C05/README.md)
