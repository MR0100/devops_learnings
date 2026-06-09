# L03/C06/T01 — ping, traceroute, mtr

## Learning Objectives

- Use ping for connectivity tests
- Trace network paths with traceroute / mtr
- Interpret results despite ICMP firewall drops

## ping

Sends ICMP Echo Request; expects Echo Reply.

```bash
ping example.com                  # default 1/sec
ping -c 4 example.com             # 4 pings, then exit
ping -i 0.2 example.com           # 5/sec
ping -s 1472 example.com          # 1472 bytes payload (test MTU)
ping -W 1 example.com             # timeout 1s per probe
ping -M do -s 1472 example.com    # don't fragment
```

Output:
```
64 bytes from 93.184.216.34: icmp_seq=1 ttl=56 time=14.3 ms
```

- TTL: hops remaining (max - hops traversed)
- time: RTT in ms

## Why Ping May Fail

Many networks drop ICMP:
- Corporate firewalls
- Some cloud security groups
- Cloud LBs

Absence of ping doesn't prove unreachability. Try other tools.

## traceroute

Discover the path packets take.
- Sends packets with increasing TTL (1, 2, 3, ...)
- Each hop with TTL=0 sends ICMP Time Exceeded back
- Reveals each router

```bash
traceroute google.com
traceroute -n google.com          # numeric (no DNS)
traceroute -T -p 443 google.com   # use TCP SYN (passes firewalls better)
traceroute -U google.com          # UDP probes
```

Linux default: UDP. macOS: ICMP. Try `-T` for HTTPS firewalls.

Output:
```
 1  192.168.1.1  1.123 ms  1.001 ms  0.989 ms
 2  10.0.0.1     5.234 ms  5.123 ms  5.301 ms
 3  * * *                                          ← timeout
 4  93.184.216.34  14.234 ms  14.123 ms  14.301 ms
```

Stars (`*`) = no response. May be:
- Router dropped ICMP
- Router doesn't decrement TTL (some load balancers)
- Asymmetric routing (response took different path)

## mtr

My TraceRoute. Combines ping + traceroute in continuous mode.

```bash
mtr google.com
mtr -rwn -c 100 google.com        # report mode, 100 packets
mtr --tcp -P 443 google.com       # TCP probes
```

Output (live):
```
Host                Loss%   Snt   Avg   Best  Wrst
1. 192.168.1.1       0.0%   100   1.2    1.0    2.1
2. 10.0.0.1          0.0%   100   5.3    5.0    8.0
3. core.isp.com      0.5%   100  14.2   13.5   18.0
```

`Loss%` reveals lossy hops. Investigate routers showing loss but their downstream doesn't (probably ICMP rate limit, not real loss).

## Interpreting Latency

```
1. local router          1 ms       (LAN)
2. ISP edge              5 ms       (city)
3. ISP backbone         20 ms       (cross-country)
4. peering / transit    50 ms       (cross-continent)
5. target               60 ms       (final destination)
```

Sudden jumps indicate cross-region transitions.

## Common Patterns

### High latency at hop N onwards
Issue is downstream of hop N. Common: bad peering link.

### Loss at hop N only
Likely ICMP rate-limit, not real loss. Verify by testing TCP.

### Loss at multiple hops increasing
Real loss downstream. Look at responsible AS.

### Asymmetric Routes
Forward and return paths different. mtr shows forward path only; tools like `mtr --bidirectional` help.

## Limitations

- Reveals network path; not application issues
- ICMP drops obscure
- Some networks dedicated to "blackhole" ICMP
- Cloud private backbones often invisible

## Cloud-Specific

### AWS
- AWS uses anycast extensively; results may vary per probe
- AWS Direct Connect bypasses public Internet
- Reachability Analyzer (in console) gives more info than traceroute

### CDN
- Anycast destination IP
- Traceroute reveals which PoP serves you

## Modern Alternatives

- **tcpping** — TCP-based ping (works through firewalls)
- **hping3** — flexible packet crafter
- **paris-traceroute** — handles load-balanced paths
- **nmap traceroute mode**

## Operations

```bash
# Quick connectivity check
ping -c 3 -W 1 host

# Latency check (real network without firewall noise)
tcpping host 443           # apt install tcpping

# Path with TCP
mtr --tcp -P 443 host
```

## Interview Prep

**Junior**: "Ping doesn't work — does that mean host is down?"

**Mid**: "Traceroute shows `* * *` at hop 5 — what does that mean?"

**Senior**: "Diagnose: connections are slow but ping is fine."

## Next Topic

→ [T02 — tcpdump & Wireshark](T02-Tcpdump-Wireshark.md)
