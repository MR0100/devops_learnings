# L03/C02/T03 — TCP Three-Way Handshake & Termination

## Learning Objectives

- Walk through SYN, SYN-ACK, ACK exchange
- Understand TCP termination (4-way close)
- Recognize TCP states

## The Three-Way Handshake

```
Client                                Server
  │                                     │
  │ SYN (seq=x)                         │   1. Client says hello
  │ ───────────────────────────────→   │
  │                                     │
  │ SYN-ACK (seq=y, ack=x+1)            │   2. Server replies
  │ ←───────────────────────────────   │
  │                                     │
  │ ACK (ack=y+1)                       │   3. Client confirms
  │ ───────────────────────────────→   │
  │                                     │
  │      ESTABLISHED — data flows       │
```

### Details

1. Client sends SYN (Synchronize): random initial sequence number `x`, SYN flag set
2. Server responds with SYN-ACK: its own ISN `y`, acknowledging `x+1`
3. Client sends ACK: acknowledging `y+1`

After this, both sides know each other's ISN and can track byte ordering.

## Why Three?

To confirm both directions are open. Could you do two? No — server wouldn't know client received its SYN-ACK.

## Sequence Numbers

Each byte gets a sequence number. ISNs are randomized to prevent attacks (SYN flooding, sequence prediction).

After handshake:
- Client sends data starting at `x+1`
- Server sends data starting at `y+1`
- ACKs increment as data flows

## TCP Termination — Four-Way

```
Client (active close)            Server (passive close)
  │                                    │
  │ FIN                                 │   1. Client done
  │ ──────────────────────────────→    │
  │ ACK                                 │   2. Server ack
  │ ←──────────────────────────────    │
  │                                     │
  │ (server may keep sending)           │
  │ FIN                                 │   3. Server done
  │ ←──────────────────────────────    │
  │ ACK                                 │   4. Client ack
  │ ──────────────────────────────→    │
  │                                     │
  │ TIME_WAIT (2 × MSL)                 │
  │ CLOSED                              │
```

Either side can initiate close. The one that initiates ends in `TIME_WAIT`.

## TCP States

```
LISTEN (server waiting)
    ↓
SYN_RECV (received SYN, sent SYN-ACK)
    ↓
ESTABLISHED (handshake done)
    ↓
FIN_WAIT_1 → FIN_WAIT_2 → TIME_WAIT → CLOSED (active close)
        OR
CLOSE_WAIT → LAST_ACK → CLOSED (passive close)
```

Check with `ss -tn state established`.

## TIME_WAIT

After active close, the closer holds the socket in TIME_WAIT for 2×MSL (Maximum Segment Lifetime, typically 60-240 seconds).

Why: ensure delayed packets from the closed connection don't arrive at a new connection on the same 4-tuple.

### TIME_WAIT Exhaustion

If a client makes thousands of connections per second to the same server:
- Each close → TIME_WAIT for ~60s
- Sockets queue up
- Eventually: no available ports → connections fail

Mitigations:
- `net.ipv4.tcp_tw_reuse=1` (allow reuse for new outgoing connections)
- Connection pooling (don't close after each request)
- Larger ephemeral port range
- Server-side close (server holds TIME_WAIT, not client)

## SYN Flood Attack

Attacker sends many SYNs from spoofed IPs:
- Server allocates state (half-open queue)
- Never sends final ACK
- Queue fills; legitimate connections rejected

Defense:
- SYN cookies (Linux: `net.ipv4.tcp_syncookies=1`) — no state until handshake completes
- Increase backlog
- Rate limit

## Half-Close

TCP allows one direction to close while the other stays open:
- App finishes sending; calls `shutdown(SHUT_WR)`
- Sends FIN; receives are still possible
- Other side may continue sending
- Useful for HTTP request/response patterns

## Connection 4-Tuple

A unique connection is `(src IP, src port, dst IP, dst port)`. Two clients can both connect to same server:port; differentiated by src port.

Source port is ephemeral, allocated by client OS (typically 32768-60999 on Linux).

## Reading tcpdump Output

```
12:00:00.001  src.54321 > dst.443: Flags [S], seq 1000, win 65535
12:00:00.002  dst.443 > src.54321: Flags [S.], seq 5000, ack 1001, win 64240
12:00:00.003  src.54321 > dst.443: Flags [.], ack 5001, win 65535
```

Flags:
- S = SYN
- . = ACK only
- P = PUSH
- F = FIN
- R = RST

`[S.]` = SYN + ACK.

## TCP Reset (RST)

Abrupt termination. Sent when:
- Connection to closed port
- Application crashed (kernel resets pending sockets)
- Stateful firewall removed flow
- Application calls `SO_LINGER` with 0 timeout

User sees "Connection reset by peer."

## Common Issues

- **Many TIME_WAIT**: connection pooling missing
- **SYN_RECV stuck**: SYN flood, slow accept loop
- **Frequent RST**: app/middlebox dropping connections
- **Slow handshake**: high latency path; tune initial RTT estimate

## Common Mistakes

- **Blaming the server for TIME_WAIT buildup on the client**: TIME_WAIT lands on whichever side calls `close()` first (the active closer). High-throughput clients opening a fresh connection per request flood their own ephemeral port range.
- **Setting `net.ipv4.tcp_tw_recycle=1`**: it was removed in Linux 4.12 and breaks clients behind NAT (drops connections sharing a source IP). Use `tcp_tw_reuse` for *outbound* reuse instead.
- **Assuming a SYN with no SYN-ACK means "server down"**: it usually means a firewall/security-group dropping the SYN, a full accept backlog, or no listener on that port — distinct failure modes with different fixes.
- **Treating RST as a graceful close**: RST is abrupt ("Connection reset by peer") — closed port, crashed app, or a middlebox that evicted the flow. A clean shutdown is FIN/ACK, not RST.
- **Confusing the 4-way close direction**: either side can initiate. CLOSE_WAIT piling up means *your app isn't calling close()* on its end after the peer sent FIN — an application bug, not a network one.
- **Ignoring half-open connections after a crash**: without keepalives, a peer that vanished leaves sockets ESTABLISHED forever, leaking fds and pool slots.

## Best Practices

- **Pool and reuse connections** (HTTP keep-alive, DB pools) instead of one-shot connects — this is the single biggest defense against TIME_WAIT/ephemeral-port exhaustion.
- **Enable `net.ipv4.tcp_syncookies=1`** so the server survives SYN floods without exhausting the half-open queue; raise `tcp_max_syn_backlog` and the listen `backlog` for bursty accept loops.
- **Prefer server-side close** for short-lived request/response services so TIME_WAIT accumulates on the (fewer, beefier) servers rather than on every client.
- **Widen the ephemeral range** (`net.ipv4.ip_local_port_range = 1024 65535`) and set `tcp_tw_reuse=1` on hosts that make many outbound connections.
- **Use TCP keepalives** (or app-level heartbeats) to reap dead half-open connections and free pooled sockets.

## Quick Refs

TCP flags in `tcpdump`: `S`=SYN · `S.`=SYN-ACK · `.`=ACK · `P`=PSH · `F`=FIN · `R`=RST.

State transitions: `LISTEN → SYN_RECV → ESTABLISHED`; active close `→ FIN_WAIT_1 → FIN_WAIT_2 → TIME_WAIT → CLOSED`; passive close `→ CLOSE_WAIT → LAST_ACK → CLOSED`. TIME_WAIT lasts 2×MSL (~60s on Linux).

```bash
# Watch a handshake
sudo tcpdump -ni any 'tcp port 443 and (tcp[tcpflags] & (tcp-syn|tcp-fin|tcp-rst) != 0)'

# Connection state census
ss -tan | awk 'NR>1{c[$1]++} END{for(s in c) print s, c[s]}'
ss -tan state time-wait | wc -l        # count TIME_WAIT
ss -tanp state close-wait              # CLOSE_WAIT + owning process (app leak)

# Relevant sysctls
sysctl net.ipv4.tcp_syncookies net.ipv4.tcp_tw_reuse \
       net.ipv4.ip_local_port_range net.ipv4.tcp_max_syn_backlog
```

## Interview Prep

**Junior**: "Walk through TCP three-way handshake."

**Mid**: "What's TIME_WAIT and why does it exist?"

**Senior**: "TIME_WAIT exhaustion — what causes and how to fix?"

**Staff**: "We see TCP RSTs in production. Walk through diagnosis."

## Next Topic

→ [T04 — TCP Flow Control, Congestion Control, Slow Start](T04-TCP-Congestion-Control.md)
