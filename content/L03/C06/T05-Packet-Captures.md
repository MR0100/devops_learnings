# L03/C06/T05 — Reading Real Packet Captures

## Learning Objectives

- Interpret tcpdump output rapidly
- Recognize common patterns (handshakes, resets, retransmits)
- Build muscle memory for production debugging

## TCP Handshake Pattern

Healthy connection:
```
12:00:00.001 client.54321 > server.443: Flags [S], seq 1000, win 65535
12:00:00.002 server.443 > client.54321: Flags [S.], seq 5000, ack 1001, win 64240
12:00:00.003 client.54321 > server.443: Flags [.], ack 5001
12:00:00.004 client.54321 > server.443: Flags [P.], seq 1001:1200, ack 5001, length 199  ← TLS ClientHello
```

Three packets, then data flows.

## Slow Connect

```
12:00:00.001 client.54321 > server.443: Flags [S], seq 1000
12:00:01.001 client.54321 > server.443: Flags [S], seq 1000           ← retransmit after 1s
12:00:03.001 client.54321 > server.443: Flags [S], seq 1000           ← exponential backoff
```

Server not responding to SYN. Could be:
- Firewall dropping silently
- Server overloaded
- Routing issue

## Connection Refused (RST on SYN)

```
12:00:00.001 client.54321 > server.443: Flags [S], seq 1000
12:00:00.002 server.443 > client.54321: Flags [R.], seq 0, ack 1001
```

Server actively rejected. Port closed.

## Active Reset (Application Crash)

```
12:00:00.001 ... [established connection, data flowing]
12:00:05.234 server.443 > client.54321: Flags [R.], seq 12345, ack 67890
```

Server suddenly RST. Could be:
- App crashed
- Connection timeout on LB
- Stateful firewall flushed flow

## TCP Retransmissions

```
12:00:00.100 client > server: seq 1000:2460, length 1460
12:00:00.150 server > client: ack 2460                    ← server confirms
12:00:00.200 client > server: seq 2460:3920, length 1460
12:00:01.200 client > server: seq 2460:3920, length 1460  ← retransmit (after RTO)
```

Lost packet or lost ACK. Wireshark highlights these.

## Selective ACK (SACK)

```
12:00:00.100 client > server: seq 1000:2460, length 1460
12:00:00.150 client > server: seq 2460:3920, length 1460   ← second segment
12:00:00.200 server > client: ack 1000, sack 2460:3920    ← got #2 but missing #1
12:00:00.300 client > server: seq 1000:2460, length 1460   ← retransmit #1 only
12:00:00.400 server > client: ack 3920                     ← got everything now
```

SACK lets receiver acknowledge non-contiguous data.

## Out-of-Order

Network may deliver segments out of order:
```
seq 1, 2, 4, 3, 5
```

TCP reorders at receiver. Wireshark shows "TCP Out-of-Order".

## TCP Zero Window

```
12:00:00.100 server > client: ack 12345, win 0
```

Server says "buffer full; stop sending." Sender pauses. When window opens, sender resumes.

If you see persistent zero windows: receiver app too slow to read.

## TCP Reset (Connection Tear-Down)

Two kinds:
- **Graceful**: FIN exchanged (4-way)
- **Abrupt**: RST sent

RST means "abort now." Many causes:
- App called close() with SO_LINGER 0
- Firewall removed flow state
- Crash
- Idle timeout

## DNS Query

```
12:00:00.001 client.54321 > 8.8.8.8.53: 12345+ A? example.com. (28)
12:00:00.010 8.8.8.8.53 > client.54321: 12345 1/0/0 A 93.184.216.34 (44)
```

- `12345+`: query ID + recursion desired
- `A? example.com.`: A record for example.com
- `1/0/0`: 1 answer, 0 authority, 0 additional

## TLS Handshake

In tcpdump:
```
client > server: Flags [P.], length 199  ← ClientHello
server > client: Flags [P.], length 5000 ← ServerHello + Cert + ...
client > server: Flags [P.], length 70   ← ClientKeyExchange + Finished
```

In Wireshark: dissects TLS handshake messages.

## Common Patterns in Wireshark

### Filter Useful Things
```
tcp.flags.reset == 1                  # all RSTs
tcp.analysis.retransmission           # retransmits (Wireshark detects)
tcp.analysis.zero_window              # zero window events
tcp.analysis.duplicate_ack            # duplicate ACKs (loss indicator)
tcp.analysis.fast_retransmission      # fast retransmits
ip.ttl < 3                            # nearby hops (often local issue)
```

### Look for Color
Wireshark colors retransmits red, RSTs black. Quick visual scan.

### Conversation View
Statistics → Conversations. Top talkers + RTT estimates.

## Use Cases

### Slow API
Filter: `ip.addr == server`. Look at timing:
- DNS query + response delay
- TCP connect + SYN-ACK RTT
- TLS handshake
- HTTP request to response gap

### Intermittent Drops
Filter `tcp.flags.reset == 1` over time. Patterns? Same time? Same client?

### Mysterious Latency
Look at `tcp.analysis.retransmission` and SACKs. Loss → retransmit → app sees delay.

### Connection Pool Exhaustion
Filter SYN flood from your app. Server returns SYN-ACK but app doesn't reuse → many new connections.

## Operations

```bash
# 10MB capture, only port 443 traffic to specific IP
sudo tcpdump -C 10 -w slow.pcap -i any 'host 1.2.3.4 and port 443'

# View in Wireshark on laptop
scp slow.pcap your-laptop:/tmp/
```

## Tips

- Capture BEFORE the issue happens (start early)
- Filter narrowly (BPF) to keep capture size sane
- Don't capture on production for long (overhead, privacy)
- Sanitize before sharing (passwords, tokens may be in cleartext)
- Use mergecap to combine multiple captures

## Common Mistakes

- **Calling every RST a problem** — an RST after a clean exchange is often a normal abort (LB idle-timeout, `SO_LINGER 0`). Look at *what preceded it* before blaming the network.
- **Confusing ICMP rate-limit loss with packet loss** — retransmits in the capture (`tcp.analysis.retransmission`) are the real loss signal, not a missing traceroute reply.
- **Starting the capture after the symptom** — you miss the SYN/handshake and the trigger. Start capturing first, then reproduce.
- **Reading raw seq numbers instead of deltas** — Wireshark's *relative* sequence numbers and the time column tell the story; absolute hex values rarely do.
- **Ignoring zero-window events** — persistent `win 0` means the *receiver's app* is too slow to read, not a network fault. People chase the wrong layer.

## Best Practices

- Learn the **healthy baseline by sight**: `S` → `S.` → `.` then `P.` data. Anything that deviates (repeated `S`, early `R.`) is your lead.
- Use **Wireshark's Expert Info and colorizing** to jump straight to retransmits, RSTs, and zero-windows instead of scrolling.
- **Follow the TCP/TLS stream** (right-click → Follow) to reconstruct application data and see request/response timing in context.
- Correlate **`tcp.time_delta`** (gap between packets in a flow) to find the slow side — a big gap before the server's data = server processing, not network.
- Keep captures **short and narrowly filtered**, then sanitize and attach to the ticket so others can verify your reading.

## Quick Refs

Pattern decoder:

| You see | Means |
|---|---|
| `S` repeated with backoff, no `S.` | SYN dropped — firewall/blackhole or dead server |
| `S` then `R.` | port closed / connection refused |
| `R.` mid-flow after data | app crash, LB/firewall flushed flow, idle timeout |
| same `seq` re-sent after RTO | retransmission (loss) |
| `ack X, sack Y:Z` | SACK — got later bytes, missing earlier |
| `ack N, win 0` | receiver buffer full — slow consumer |
| `F.` / `.` exchange | graceful 4-way close (normal) |

```bash
# Capture early, narrow, rotating
sudo tcpdump -i any -nn -C 10 -w slow.pcap 'host 1.2.3.4 and port 443'

# Pull the interesting packets back out
tcpdump -nn -r slow.pcap 'tcp[tcpflags] & (tcp-syn|tcp-rst|tcp-fin) != 0'
```

Wireshark filters worth memorizing: `tcp.analysis.retransmission`, `tcp.analysis.zero_window`, `tcp.analysis.duplicate_ack`, `tcp.flags.reset==1`, `tcp.time_delta > 0.5`.

## Interview Prep

**Mid**: "What does TCP retransmit look like in tcpdump?"

**Senior**: "Customer reports random timeouts. How do you capture + analyze?"

**Staff**: "Walk through analyzing a slow API call from capture."

## Next Chapter

→ [C07 — Cloud & Data Center Networking](../C07/README.md)
