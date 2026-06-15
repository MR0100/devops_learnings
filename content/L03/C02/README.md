# L03/C02 — IP, TCP, UDP, QUIC

## Chapter Overview

The transport and network layers. This is where most production network issues happen and where most interview questions live.

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-IPv4-Subnetting.md) | IPv4 Addressing, Subnetting, CIDR | 1 hr |
| [T02](T02-IPv6.md) | IPv6 (Why It Matters Now) | 0.5 hr |
| [T03](T03-TCP-Handshake.md) | TCP Three-Way Handshake & Termination | 1 hr |
| [T04](T04-TCP-Congestion-Control.md) | TCP Flow Control, Congestion Control, Slow Start | 1.5 hr |
| [T05](T05-UDP.md) | UDP and When to Use It | 0.5 hr |
| [T06](T06-QUIC.md) | QUIC (and HTTP/3) | 1 hr |

## IPv4 Addressing & CIDR

```
192.168.1.0 / 24
└──── Network ──┘└┬┘
                  └ Prefix length (/24 means top 24 bits are network)

CIDR Cheat Sheet:
/8   → 16,777,214 hosts (e.g., 10.0.0.0/8)
/16  → 65,534 hosts     (e.g., 172.16.0.0/16)
/24  → 254 hosts        (e.g., 192.168.1.0/24)
/28  → 14 hosts
/29  → 6 hosts
/30  → 2 hosts (point-to-point)
/32  → 1 host (a specific address)
```

### Private Address Ranges (RFC 1918)
- 10.0.0.0/8 (~16M)
- 172.16.0.0/12 (~1M)
- 192.168.0.0/16 (~65K)
- 100.64.0.0/10 — Carrier-Grade NAT (rarely used in clouds)
- 169.254.0.0/16 — Link-local (AWS uses 169.254.169.254 for IMDS)

## TCP 3-Way Handshake

```
Client                  Server
   │ SYN (seq=x)          │
   │ ──────────────────►  │
   │  SYN-ACK             │
   │  (seq=y, ack=x+1)    │
   │ ◄──────────────────  │
   │ ACK (ack=y+1)        │
   │ ──────────────────►  │
   │                      │
   │   ESTABLISHED        │
```

Each side maintains: sequence number, ack number, window, MSS.

## TCP 4-Way Termination

```
Client (active close)    Server (passive close)
   │ FIN                   │
   │ ─────────────────►    │
   │   ACK                 │
   │ ◄─────────────────    │
   │   FIN                 │
   │ ◄─────────────────    │  (server may take time here)
   │ ACK                   │
   │ ─────────────────►    │
   │                       │
   │ TIME_WAIT (2 MSL)     │
   │ CLOSED                │
```

`TIME_WAIT` ensures stray segments don't reach a future connection on the same 4-tuple. Default 60s in Linux. High-rate clients see TIME_WAIT exhaustion.

## TCP State Machine (Essential)

```
LISTEN ──► SYN_RECV ──► ESTABLISHED ──► FIN_WAIT_1 ──► FIN_WAIT_2 ──► TIME_WAIT ──► CLOSED
                          ▲
              SYN_SENT ───┘
```

Check with `ss -tn state established`.

## Congestion Control

Modern algorithms (cc):
- **Reno / NewReno** — classic AIMD (Additive Increase, Multiplicative Decrease)
- **CUBIC** — Linux default; faster recovery on high-bandwidth long-RTT paths
- **BBR** — Google; estimates bandwidth-delay product; dramatically faster on lossy paths

Check on Linux:
```bash
sysctl net.ipv4.tcp_congestion_control
sysctl -w net.ipv4.tcp_congestion_control=bbr  # if available
cat /proc/sys/net/ipv4/tcp_available_congestion_control
```

## Window Scaling & Buffer Tuning

For high-BDP (Bandwidth-Delay Product) paths:
```bash
# Larger socket buffers
sysctl -w net.ipv4.tcp_rmem='4096 87380 16777216'
sysctl -w net.ipv4.tcp_wmem='4096 65536 16777216'
sysctl -w net.core.rmem_max=16777216
sysctl -w net.core.wmem_max=16777216
```

BDP = bandwidth × RTT. A 10 Gbps link with 100ms RTT needs ~125 MB of buffer to saturate.

## UDP

- Connectionless, unreliable, unordered
- Header: 8 bytes (vs TCP's 20+)
- Use cases: DNS, NTP, VoIP, video streaming, gaming, QUIC, gRPC over UDP

UDP has no flow control or congestion control — app must implement what it needs.

## QUIC and HTTP/3

QUIC = UDP-based reliable transport with TLS 1.3 baked in.

Wins over TCP+TLS:
- **0-RTT** handshake (after first connection)
- **No head-of-line blocking** between streams
- **Connection migration** (laptop changes Wi-Fi → connection survives)
- **Better loss recovery** (per-stream)

Losses:
- Middleboxes don't understand UDP/QUIC (some block)
- Higher CPU than TCP (encryption overhead in user space)
- New tooling needed

## Performance Numbers

| Operation | Latency |
|---|---|
| Local TCP send | ~10 μs |
| Same-AZ RTT | 0.5 ms |
| Same-region RTT | 1-2 ms |
| Cross-region (US east-west) | 70 ms |
| US ↔ Europe | 100 ms |
| US ↔ Asia | 150-200 ms |

## Interview Themes

- "Walk through the TCP 3-way handshake"
- "What happens when a packet is lost? Recovery mechanism?"
- "Why does TIME_WAIT exist and what problems does it cause?"
- "When would you choose UDP over TCP?"
- "What does QUIC solve that TCP doesn't?"
- "Tune TCP for a 1 Gbps link with 100ms RTT" (BDP calc)
- "Subnet 10.0.0.0/16 into 4 equal subnets"
