# L03/C01/T02 — TCP/IP Model

## Learning Objectives

- Compare TCP/IP and OSI models
- Understand why TCP/IP "wins" in practice
- Map common protocols to TCP/IP layers

## The Model

The TCP/IP model (also called the DoD model — Department of Defense, where it originated) is the model the Internet actually runs on.

```
+----+--------------+-------------------------+
| 4  | Application  | HTTP, DNS, SSH, TLS     |  ← OSI 5,6,7 merged
+----+--------------+-------------------------+
| 3  | Transport    | TCP, UDP, QUIC          |  ← OSI 4
+----+--------------+-------------------------+
| 2  | Internet     | IP, ICMP                |  ← OSI 3
+----+--------------+-------------------------+
| 1  | Link         | Ethernet, Wi-Fi         |  ← OSI 1,2 merged
+----+--------------+-------------------------+
```

## OSI vs TCP/IP

| OSI | TCP/IP | Notes |
|---|---|---|
| 7 Application | 4 Application | Both same concept |
| 6 Presentation | 4 Application | Merged |
| 5 Session | 4 Application | Merged |
| 4 Transport | 3 Transport | Same |
| 3 Network | 2 Internet | Same; different name |
| 2 Data Link | 1 Link | Merged |
| 1 Physical | 1 Link | Merged |

## Why TCP/IP Won

- **Simpler**: 4 layers is easier to think about
- **Pragmatic**: came from real-world implementation, not a committee
- **Free**: published openly, no licensing
- **Better timing**: arrived as the Internet grew
- **OSI's complexity**: 7 layers became more confusing than helpful

OSI is the academic model. TCP/IP is what runs.

## Application Layer

Everything above transport. The TCP/IP model doesn't try to subdivide further.

Protocols:
- **HTTP / HTTPS** — the web
- **DNS** — name resolution
- **SSH** — secure remote shell
- **SMTP / IMAP / POP3** — email
- **FTP / SFTP** — file transfer
- **TLS** — encryption (often considered "between" transport and app)
- **gRPC** — RPC framework (HTTP/2-based)
- **WebSocket** — bidirectional over HTTP upgrade

## Transport Layer

End-to-end between processes.

- **TCP** — reliable, ordered, slower (web, SSH, most apps)
- **UDP** — unreliable, fast (DNS, NTP, video, gaming)
- **QUIC** — modern; reliable transport over UDP; used by HTTP/3

Ports identify processes:
- 22 — SSH
- 53 — DNS
- 80 — HTTP
- 443 — HTTPS
- 3306 — MySQL
- 5432 — Postgres
- 6379 — Redis
- 8080 — common alt-HTTP

## Internet Layer

Routing across the Internet.

- **IPv4** — 32-bit addresses, mostly exhausted
- **IPv6** — 128-bit addresses, slow rollout
- **ICMP** — control messages (ping, traceroute)
- **Routing protocols** (BGP, OSPF) — figure out paths

## Link Layer

Local network delivery.

- **Ethernet** — wired
- **Wi-Fi (802.11)** — wireless
- **ARP** — IP → MAC translation

## Where Does TLS Fit?

This is the perpetual debate. TLS:
- Operates above TCP (uses TCP as transport)
- Below HTTP (HTTPS = HTTP over TLS)
- Provides encryption + authentication
- Often called "Layer 5/6" or "between transport and app"

In TCP/IP terms: it's part of the Application layer. Some draw a "Security" layer between 3 and 4.

Don't get stuck on the placement — focus on what it does.

## A Real Stack

When you `curl https://example.com`:

```
Application:  HTTPS request → TLS encrypts → HTTP request inside
Transport:    TCP, port 443
Internet:     IPv4 packet, source/dest IPs
Link:         Ethernet frame, source/dest MACs
              (then physical: bits on wire)
```

## Useful Mental Model

> Layer 7: what the user wants
> Layer 4: which process on which machine
> Layer 3: which machine on the Internet
> Layer 2: which device on the local wire
> Layer 1: actual bits

This is the simplest way to teach networking.

## Interview Prep

**Junior**: "What's the TCP/IP model?"

**Mid**: "Why TCP/IP over OSI?"
- Simpler; pragmatic; what the Internet actually runs.

**Senior**: "Where does TLS fit in TCP/IP?"
- Above transport, below the app's logic. Practically: part of "Application" in 4-layer model.

**Staff**: "When you say 'Layer 7 load balancer,' what does that mean in TCP/IP terms?"
- LB understands and acts on Application-layer content (HTTP method, URL, headers).

## Further Reading

- RFC 1122 — Internet Host Requirements
- RFC 1180 — TCP/IP Tutorial

## Next Topic

→ [T03 — Packet Encapsulation](T03-Packet-Encapsulation.md)
