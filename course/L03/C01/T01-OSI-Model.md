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
