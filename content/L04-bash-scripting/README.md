# L04 — Shell, Bash & Scripting for Automation

## Overview

The shell is your daily interface to Linux. Mastery here multiplies your productivity for the rest of your career.

**5 chapters, 22 topics.**

## Chapter Map

### [C01](C01/) — Bash Fundamentals
- T01 Shells: bash, zsh, fish, sh, dash
- T02 Variables, Quoting, Expansion
- T03 Conditionals, Loops, Functions
- T04 Exit Codes, set -euo pipefail

### [C02](C02/) — Text Processing
- T01 grep, egrep, fgrep, ripgrep
- T02 sed (Substitution, In-Place Editing)
- T03 awk (Programming with awk)
- T04 cut, sort, uniq, tr, paste, join
- T05 jq for JSON, yq for YAML

### [C03](C03/) — Advanced Bash
- T01 Arrays, Associative Arrays
- T02 Process Substitution, Heredocs
- T03 Trap & Signal Handling
- T04 Background Jobs, Job Control
- T05 Parallel Execution (xargs -P, GNU parallel)

### [C04](C04/) — Production-Grade Scripts
- T01 Argument Parsing (getopts, getopt)
- T02 Logging, Stderr vs Stdout, Tee
- T03 Error Handling Patterns
- T04 Dry-Run, Idempotency, Atomic Operations
- T05 ShellCheck and Style Guides

### [C05](C05/) — Beyond Bash
- T01 When to Move to Python/Go
- T02 Makefile for Automation
- T03 just, task, mage Alternatives

## Learning Outcomes

- Write production-grade bash scripts with proper error handling
- Master awk, sed, jq for log analysis and config manipulation
- Know when bash stops being the right tool
- Pass `shellcheck` clean

## The 10 Bash Idioms You Use Daily

```bash
set -euo pipefail               # crash on error, unset var, pipe fail
trap cleanup EXIT               # always cleanup
[[ "$var" == "value" ]]         # double bracket
${var:-default}                 # default if unset
${var/old/new}                  # replace
arr=(a b c); for x in "${arr[@]}"; do echo "$x"; done
diff <(sort f1) <(sort f2)      # process substitution
{ cmd1; cmd2; } > out.log       # group
echo "$(date +%s)"              # command substitution
read -r -p "Prompt: " var       # interactive read
```

## Key Quoting Rules

- Single quotes: literal, no expansion
- Double quotes: expansion, but preserve as one arg
- Backticks: deprecated; use `$(...)`
- Always quote variables in commands: `"$var"`
- Heredocs preserve quoting:
  - `<<EOF` — expansion happens
  - `<<'EOF'` — no expansion (literal)

## Recommended Reading

- *Bash Cookbook* — Carl Albing, JP Vossen
- *The Linux Command Line* — William Shotts (free)
- ShellCheck wiki (the lint rules are deeply educational)

## Interview Relevance

- "Write a bash script that does X" (always asked at some level)
- "Find all unique IPs in this log file"
- "Process 1000 files in parallel"
- "When would you choose Python over bash?"

## Next

→ [L05 — Version Control & Git Internals](../L05-git/README.md)
