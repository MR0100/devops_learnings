# L03/C06/T03 — netstat, ss, lsof

## Learning Objectives

- Use ss for socket inspection (modern netstat)
- Find which process owns a port
- Diagnose connection states

## ss (Socket Statistics)

Modern, fast replacement for netstat.

```bash
ss                                    # all sockets
ss -t                                 # TCP only
ss -u                                 # UDP only
ss -l                                 # listening only
ss -tnp                               # TCP, numeric, with process info
ss -tlnp                              # TCP listening
ss -tan                               # all TCP
ss -tan state established             # only established
ss -tan state time-wait               # all TIME_WAIT
ss -s                                 # summary stats
```

### Common Usages

```bash
# What's listening on what port?
sudo ss -tlnp

# All connections to port 443
sudo ss -tn '( dport = :443 )'

# Connections to specific host
sudo ss -tn '( dst 1.2.3.4 )'

# Sockets owned by a process
sudo ss -tnp | grep nginx

# Count by state
ss -tan | awk 'NR>1 {print $1}' | sort | uniq -c
```

## netstat (Legacy)

```bash
netstat -tulpn                        # TCP+UDP listening with process
netstat -an                           # all sockets, numeric
netstat -i                            # interface stats
netstat -r                            # routing table (use `ip r` now)
netstat -s                            # protocol stats
```

`ss` is 10-100× faster on busy systems. Use it.

## lsof (List Open Files)

Files include sockets, pipes, regular files.

```bash
sudo lsof -i :443                     # what's using port 443
sudo lsof -i tcp                      # all TCP
sudo lsof -i tcp -p 1234               # TCP for process 1234
sudo lsof -i @1.2.3.4                 # connections to host
sudo lsof -i tcp:80                   # TCP port 80 specifically
sudo lsof -u alice                    # files opened by user
sudo lsof /var/log/syslog             # what's open this file
sudo lsof -p 1234                     # all files of process
```

Versatile but slower than ss for sockets.

## Common Diagnostics

### "Address already in use"
```bash
sudo ss -tlnp | grep :8080
# OR
sudo lsof -i :8080
```

Find the process holding it.

### Many TIME_WAIT
```bash
ss -tan state time-wait | wc -l
```

If thousands: connection pooling missing somewhere.

### Connection States Distribution
```bash
ss -tan | awk 'NR>1 {print $1}' | sort | uniq -c | sort -rn
```

Healthy: lots of ESTAB, few TIME_WAIT (some is fine).

Bad: tons of SYN_RECV (slow accept loop), tons of CLOSE_WAIT (app not closing).

### CLOSE_WAIT Buildup
- Server: app didn't call close() after client disconnected
- Application bug; identify via process and code

### Sockets Per Process
```bash
ls -1 /proc/<pid>/fd | wc -l
```

Many sockets per app may indicate connection leak.

## State Reference

| State | Meaning |
|---|---|
| LISTEN | server waiting for connections |
| SYN_SENT | client sent SYN, waiting for SYN-ACK |
| SYN_RECV | server got SYN, sent SYN-ACK, waiting for ACK |
| ESTABLISHED | both sides connected; data flows |
| FIN_WAIT_1 | active closer sent FIN |
| FIN_WAIT_2 | got ACK of FIN; waiting for peer's FIN |
| TIME_WAIT | both sides closed; waiting 2×MSL |
| CLOSE_WAIT | peer closed; we haven't yet |
| LAST_ACK | we sent FIN; waiting for ACK |
| CLOSED | done |

## Connection Tracking

```bash
sudo conntrack -L           # all tracked connections
sudo conntrack -L -p tcp    # TCP only
sudo conntrack -E           # events stream
cat /proc/net/nf_conntrack  # raw
```

Conntrack table fills → silent connection drops. Tune `net.netfilter.nf_conntrack_max`.

## Interface Stats

```bash
ip -s link show eth0
```

Look for: rx_dropped, tx_dropped, errors, collisions.

## Connection Tracking Counters

```bash
ss -s
# Output:
# Total: 1234
# TCP:   456 (estab 100, closed 200, orphaned 0, timewait 156)
```

Time-wait > 1000 → consider tuning or pooling.

## /proc Interfaces

```bash
cat /proc/net/tcp           # raw socket table (hex format)
cat /proc/net/sockstat      # summary
cat /proc/sys/net/ipv4/tcp_max_syn_backlog
```

## Operations

```bash
# Just-the-listeners
sudo ss -tlnp | awk 'NR>1 {print $4, $6}'

# Top processes by socket count
sudo lsof -nP -iTCP -sTCP:ESTABLISHED | awk '{print $1}' | sort | uniq -c | sort -rn | head
```

## Interview Prep

**Junior**: "What's listening on port 80?"
- `sudo ss -tlnp | grep :80`

**Mid**: "TIME_WAIT exhaustion — diagnose."

**Senior**: "Diagnose connection leak in a Java app."

**Staff**: "Conntrack table full — symptoms and fix."

## Next Topic

→ [T04 — curl and HTTP Debugging](T04-Curl-HTTP-Debug.md)
