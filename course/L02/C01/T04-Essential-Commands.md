# L02/C01/T04 — Essential Commands

## Learning Objectives

- Truly master `ls`, `find`, `grep`, `xargs`, `awk`, `sed` (covered more in L04)
- Build muscle memory for production-grade command chains
- Use the commands' power features, not just basics

## ls Deep

```bash
ls -la              # all incl. hidden, long format
ls -lh              # human-readable sizes
ls -ltr             # sort by time, oldest first
ls -lS              # sort by size
ls -li              # show inode number
ls -lZ              # show SELinux context
ls -lA --color=auto # exclude . and ..
```

Tip: alias `ll='ls -lah --color=auto'`

## find Deep

```bash
# By name (case insensitive)
find / -iname "*.log" 2>/dev/null

# By size > 100M
find / -size +100M -type f

# Modified in last 24h
find /var/log -mtime -1

# Modified in last 5 min (fast iteration)
find . -mmin -5

# Multiple conditions
find /var/log -type f -name "*.log" -mtime +30

# Execute on results
find /tmp -type f -name "*.tmp" -delete
find . -type f -name "*.py" -exec wc -l {} +

# Pipe to xargs for parallelism
find . -name "*.json" -print0 | xargs -0 -P 4 jq .
```

`-exec ... {} +` vs `-exec ... {} \;`: the `+` batches arguments (faster), `\;` runs one per file.

## grep / ripgrep

```bash
grep -r "pattern" /path             # recursive
grep -i "pattern"                   # case insensitive
grep -v "pattern"                   # invert match
grep -n "pattern" file              # show line numbers
grep -A 3 -B 3 "pattern" file       # 3 lines after & before context
grep -E "regex|alt"                 # extended regex (or use egrep)
grep -F "literal"                   # literal (no regex)
grep -c "pattern" file              # count matches
grep -l "pattern" *                 # only filenames with match
grep -o "match"                     # print only matched portion
```

For large codebases, use `ripgrep` (`rg`): ~10–100× faster, respects `.gitignore`.

## xargs

The "take stdin, run command with it" tool.

```bash
ls *.log | xargs rm                       # remove .log files
ls *.log | xargs -I {} mv {} archive/{}   # rename via placeholder
ls | xargs -n 1 echo                      # one arg per invocation
find . -name "*.py" -print0 | xargs -0 wc -l   # NUL-delimited (safe for spaces)
ls *.json | xargs -P 8 -I {} jq . {}      # parallel
```

The `-P N` flag is essential for parallel batch work.

## Process & Misc Essentials

```bash
ps auxf                  # all processes, tree format
ps -eo pid,ppid,user,cmd # custom columns
top                      # interactive (or htop, btop)
kill -9 PID              # send SIGKILL
pkill -f "pattern"       # kill by command match
pgrep -f "pattern"       # find by command match
killall nginx            # kill all matching name

# Disk and files
df -h                    # disk usage
du -sh dir/              # directory total
du -ah dir | sort -hr | head  # largest items
ncdu                     # interactive du (great)

# Networking quick
ss -tulpn                # listening sockets
ip a                     # interfaces (replaces ifconfig)
ip r                     # routing table

# System info
uname -a                 # kernel, OS
lsb_release -a           # distro version
cat /etc/os-release      # universal distro info
uptime
free -h                  # memory
nproc                    # CPU count
```

## Heredoc, Tee, Subshells (Useful Daily)

```bash
cat <<EOF > /etc/myconf.conf
key=value
key2=value2
EOF

echo "hello" | tee /tmp/log              # write AND print
echo "data" | tee -a /var/log/app.log    # append

# subshell  vs current shell
(cd /tmp && ls)          # subshell, dir change isolated
{ cd /tmp; ls; }         # current shell — actually changes dir
```

## Pipes, Process Substitution

```bash
diff <(sort file1) <(sort file2)         # diff sorted versions
comm -12 file1 file2                     # lines in both
```

## Aliases You'll Want

```bash
alias ll='ls -lah --color=auto'
alias gs='git status'
alias k='kubectl'
alias tf='terraform'
alias dps='docker ps'
alias ports='ss -tulpn'
alias myip='curl -s ifconfig.me'
```

## Interview Prep

**Mid**: "Find the 10 largest files under /var."
- `find /var -type f -printf '%s %p\n' 2>/dev/null | sort -rn | head -10`

**Senior**: "Kill all processes matching a name pattern, but only if they've been running > 1 hour."
- Combine `ps`, `awk`, and `kill`. Or use `ps -eo etime,pid,cmd` and filter.

**Staff**: "We have 50 GB of logs across /var/log on 100 servers. Find unique error messages without DOS'ing the servers."
- Discuss: SSH parallelism (pdsh, parallel-ssh), structured logging shipping (preferred), rate limiting per host, and centralized log aggregation.

## Next Chapter

→ [C02 — Process Management](../C02/README.md)
