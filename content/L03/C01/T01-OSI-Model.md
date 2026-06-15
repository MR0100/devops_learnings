# L03/C01/T01 — OSI Model (All 7 Layers, In Detail)

## Learning Objectives

- Name and describe each of the 7 OSI layers
- Identify which protocols live at each layer
- Use the OSI model as a debugging vocabulary

## Prerequisites

Basic familiarity with "what is a network" — that's it.

## The Model

```
+-----+-------------+----------------------------+--------------------------+
| Lvl | Layer       | Job                        | Examples                 |
+-----+-------------+----------------------------+--------------------------+
| 7   | Application | What the user actually     | HTTP, FTP, SSH, DNS,     |
|     |             | wants to do                | SMTP, gRPC                |
+-----+-------------+----------------------------+--------------------------+
| 6   | Presentation| Data representation,        | TLS, JPEG, MIME,          |
|     |             | encoding, encryption        | ASCII, Unicode            |
+-----+-------------+----------------------------+--------------------------+
| 5   | Session     | Establishing/maintaining    | RPC, NetBIOS, PPTP        |
|     |             | conversations               |                           |
+-----+-------------+----------------------------+--------------------------+
| 4   | Transport   | End-to-end delivery,        | TCP, UDP, QUIC, SCTP      |
|     |             | reliability                 |                           |
+-----+-------------+----------------------------+--------------------------+
| 3   | Network     | Routing across networks     | IP, ICMP, BGP, OSPF       |
+-----+-------------+----------------------------+--------------------------+
| 2   | Data Link   | Local link addressing       | Ethernet, ARP, MAC, PPP   |
+-----+-------------+----------------------------+--------------------------+
| 1   | Physical    | Bits on the wire            | Cables, fiber, radio      |
+-----+-------------+----------------------------+--------------------------+
```

**Mnemonics**:
- Top down: *All People Seem To Need Data Processing*
- Bottom up: *Please Do Not Throw Sausage Pizza Away*

## Each Layer in Depth

### Layer 1 — Physical

The hardware. Voltage, light pulses, radio signals.

- **Examples**: Cat6 cable, fiber optic, Wi-Fi radio, Bluetooth
- **Units**: bits
- **Devices**: hubs (mostly obsolete), repeaters, cables, NICs (Network Interface Cards)
- **Problems here**: cable damaged, fiber dirty, signal degradation

Debugging signal: link lights, cable tester, optical power meter.

### Layer 2 — Data Link

Local network delivery. Within one collision domain or VLAN.

- **Examples**: Ethernet frames, MAC addresses, ARP, VLAN tagging (802.1Q)
- **Units**: frames
- **Devices**: switches, bridges
- **Addresses**: MAC (48-bit, hardware-burned)

ARP (Address Resolution Protocol) translates IP → MAC for local delivery. Sometimes called "Layer 2.5" because it bridges L2 and L3.

Debugging: `arp -a`, switch port counters, MAC tables.

### Layer 3 — Network

Routing between networks. The Internet operates here.

- **Examples**: IPv4, IPv6, ICMP (ping), routing protocols (BGP, OSPF, RIP)
- **Units**: packets
- **Devices**: routers, L3 switches
- **Addresses**: IP (32-bit IPv4 or 128-bit IPv6)

Each packet has source + destination IP. Routers forward based on routing tables.

Debugging: `ping`, `traceroute`, `ip route`.

### Layer 4 — Transport

End-to-end delivery between processes (not just hosts).

- **TCP**: connection-oriented, reliable, ordered, slower
- **UDP**: connectionless, unreliable, fast
- **QUIC**: TCP-like reliability over UDP, modern
- **SCTP**: niche, telecom
- **Units**: segments (TCP) or datagrams (UDP)
- **Addresses**: ports (16-bit, 0-65535)

Ports are how the OS knows which process to deliver to.

Debugging: `ss -tn`, `netstat`, `tcpdump`.

### Layer 5 — Session

Manages conversations. In modern Internet stacks, this is often merged into application logic.

- **Examples**: RPC (remote procedure call) frameworks, NetBIOS (legacy)
- Reality: most apps build session logic into the application layer

This layer is the most ambiguous in practice.

### Layer 6 — Presentation

Data format and encryption.

- **Examples**: TLS/SSL, character encoding (UTF-8, ASCII), data formats (JPEG, MPEG)
- **Function**: translate between application-specific format and network-neutral format
- Reality: largely merged into application logic; TLS is usually called out as "between L4 and L7"

### Layer 7 — Application

What users see. What apps actually do.

- **Examples**: HTTP, HTTPS, FTP, SSH, SMTP, DNS, gRPC, WebSockets, MQTT
- **Units**: messages

This is the layer most engineers spend most of their time on.

## Encapsulation Walkthrough

User clicks a button on a webpage:

```
L7  App data:           "GET /index.html HTTP/1.1\r\nHost: example.com\r\n..."
L4  TCP segment:        [TCP header | App data]
L3  IP packet:          [IP header | TCP header | App data]
L2  Ethernet frame:     [Eth header | IP header | TCP header | App data | Eth trailer]
L1  bits:               010101010101110100... (on wire)
```

Each layer adds its header. Receiver decapsulates in reverse.

## Real Engineering Vocabulary

Senior engineers say:
- "It's an L4 issue — TCP reset" — meaning Transport
- "It's an L7 problem — HTTP 503" — meaning Application
- "We need an L7 load balancer" — meaning understands HTTP
- "Drop at L3" — block by IP
- "Drop at L7" — block based on URL/header content

Use this vocabulary. It's how staff engineers talk.

## Where the Model Breaks Down

The OSI model is **idealized**. Reality:

- **TLS** straddles L5/L6/L7
- **QUIC** bundles transport + session + TLS over UDP
- **WireGuard** tunnels L3 over UDP (so an "L3 protocol" rides on L4)
- **Service Mesh** does L7 routing of L4 connections

A pedant says these are wrong. A staff engineer says "yeah, the model is a guide, not law."

## Load Balancer Layer Comparison

| Layer | LB Operates At | Decisions Based On | Examples |
|---|---|---|---|
| L4 | TCP / UDP | IP, port | AWS NLB, HAProxy TCP, Envoy TCP |
| L7 | HTTP, gRPC | URL, header, method, body | AWS ALB, Nginx, Envoy HTTP |

L4 is faster but dumber. L7 is richer but slower.

## Hands-On Lab

### Wireshark a Request

1. Open Wireshark
2. Start capture on your active interface
3. In a terminal: `curl https://example.com`
4. Stop capture
5. Filter: `tcp.port == 443`
6. Find a packet; expand the layers in Wireshark's "Packet Details" pane:
   - Frame (metadata)
   - Ethernet II (L2)
   - Internet Protocol (L3)
   - Transmission Control Protocol (L4)
   - Transport Layer Security (TLS, L5-6)
   - Hypertext Transfer Protocol (L7, if you decrypt)

Visualize each layer separately. This sticks.

## Common Mistakes

- **Treating the model as literal protocol architecture**: The Internet runs on TCP/IP (4 layers). OSI is a teaching/vocabulary tool; don't expect a clean 1:1 mapping to real stacks.
- **Calling TLS "Layer 7"**: TLS sits between transport and application (commonly tagged L5/L6). HTTPS = HTTP (L7) over TLS over TCP (L4). Lumping it into L7 confuses where encryption actually happens.
- **Asking an L4 load balancer to route by URL or `Host` header**: L4 sees only IP + port; the URL lives in the L7 payload. Path/host routing requires an L7 proxy (ALB, Nginx, Envoy HTTP).
- **Confusing MAC (L2) with IP (L3)**: MAC is link-local and never crosses a router; IP is end-to-end. "Why doesn't the destination MAC change?" — it does, at every hop.
- **Saying ARP is "Layer 3"**: ARP resolves IP→MAC and bridges L2/L3; it's an L2 protocol (often called "L2.5"), not routing.

## Best Practices

- **Use the layer number as a debugging filter**: Localize a fault to one layer first (link light → L1, `arp`/MAC → L2, `ping`/route → L3, `ss`/port → L4, `curl -v` → L7) before guessing.
- **Pick the LB layer for the job**: L4 for raw throughput, non-HTTP protocols, and TLS passthrough; L7 for path/host routing, header inspection, retries, and request-level observability.
- **Encrypt at the right layer**: TLS for application traffic; IPsec/WireGuard (L3) for network-wide tunnels. Don't reinvent transport security at L7.
- **Speak in layers with your team**: "It's an L3 reachability issue" vs "L7 returns 503" scopes an incident instantly and routes it to the right owner.
- **Capture and expand packets in Wireshark** when a problem spans layers — seeing Ethernet → IP → TCP → TLS → HTTP nested in one frame builds durable intuition.

## Quick Refs

OSI layers (bottom-up: *Please Do Not Throw Sausage Pizza Away*):

| L | Name | PDU | Address | Example protocols | Debug |
|---|---|---|---|---|---|
| 1 | Physical | bits | — | Ethernet PHY, fiber, Wi-Fi radio | link lights, cable tester |
| 2 | Data Link | frame | MAC (48-bit) | Ethernet, ARP, 802.1Q | `ip -s link`, `arp -a`, `bridge fdb` |
| 3 | Network | packet | IP | IPv4/6, ICMP, BGP, OSPF | `ping`, `traceroute`, `ip route` |
| 4 | Transport | segment/datagram | port (16-bit) | TCP, UDP, QUIC, SCTP | `ss -tunap`, `tcpdump` |
| 5-6 | Session/Presentation | — | — | TLS, RPC, encodings | `openssl s_client` |
| 7 | Application | message | — | HTTP, DNS, SSH, gRPC | `curl -v`, `dig` |

```bash
# Layer-by-layer reachability check
ip link show          # L1/L2: is the interface up?
arp -an               # L2:    is the next hop's MAC known?
ping -c1 <gw>         # L3:    is the gateway reachable?
ip route get <dst>    # L3:    which route/interface is chosen?
ss -tn dst <ip>       # L4:    is a TCP socket established?
curl -v http://<dst>  # L7:    does the application respond?
```

## Interview Prep

**Junior**: "What are the 7 OSI layers?"
- Recite names; one-line description of each.

**Mid**: "Which layer does TCP operate at? What about HTTP?"
- TCP = L4 transport. HTTP = L7 application.

**Senior**: "An L4 load balancer can't make decisions based on URL — explain why."
- L4 LB sees only TCP/IP headers. URL is in the HTTP body (L7). LB hasn't decoded that. To route by URL, it must be L7.

**Staff**: "Walk me through a packet from a curl on your laptop to a server in another data center, layer by layer."

## Further Reading

- *TCP/IP Illustrated, Vol 1* — W. Richard Stevens
- *Computer Networking: A Top-Down Approach* — Kurose & Ross
- RFC 1122 — Requirements for Internet Hosts

## Next Topic

→ [T02 — TCP/IP Model](T02-TCP-IP-Model.md)
