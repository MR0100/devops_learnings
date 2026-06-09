# L03/C01 — Network Models

## Chapter Overview

The OSI and TCP/IP models are not just historical artifacts — they are the working vocabulary every senior engineer uses to describe and debug systems. This chapter establishes that vocabulary in production-grade depth.

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-OSI-Model.md) | OSI Model (All 7 Layers, In Detail) | 1 hr |
| [T02](T02-TCP-IP-Model.md) | TCP/IP Model | 0.5 hr |
| [T03](T03-Packet-Encapsulation.md) | Packet Encapsulation | 0.5 hr |

## The OSI 7-Layer Model

```
+---+-----------------+----------------------------------+----------------------+
| # | Layer           | Function                         | Protocols / Examples  |
+---+-----------------+----------------------------------+----------------------+
| 7 | Application     | App-specific data exchange       | HTTP, DNS, SMTP, SSH  |
| 6 | Presentation    | Encoding, encryption             | TLS, JPEG, MIME       |
| 5 | Session         | Session establishment/teardown   | RPC, NetBIOS          |
| 4 | Transport       | Reliable / unreliable delivery   | TCP, UDP, QUIC, SCTP  |
| 3 | Network         | Routing across networks          | IP, ICMP, BGP, OSPF   |
| 2 | Data Link       | Addressing on local link         | Ethernet, ARP, MAC    |
| 1 | Physical        | Bits over wire/air               | Cables, fiber, radio  |
+---+-----------------+----------------------------------+----------------------+
```

**Mnemonic**: *All People Seem To Need Data Processing* (top down)

## TCP/IP (DoD) 4-Layer Model

The model that actually runs the internet (OSI was an idealized framework):

```
+----+-----------------+----------------------------+
| 4  | Application     | HTTP, DNS, SSH, TLS        |  ← merges OSI 5,6,7
| 3  | Transport       | TCP, UDP, QUIC             |
| 2  | Internet        | IP, ICMP                   |
| 1  | Link            | Ethernet, Wi-Fi            |  ← merges OSI 1,2
+----+-----------------+----------------------------+
```

## Encapsulation

As data moves DOWN the stack, each layer adds a header (and sometimes trailer):

```
User data
   │ (App layer)
   ▼
+-------+-----------------------+
| App H |   Data                |
+-------+-----------------------+
   │ (Transport)
   ▼
+-------+-------+--------------+
| TCP H | App H |  Data        |
+-------+-------+--------------+
   │ (Network)
   ▼
+------+-------+-------+--------+
| IP H | TCP H | App H |  Data  |
+------+-------+-------+--------+
   │ (Link)
   ▼
+-------+------+-------+-------+-------+-------+
| Eth H | IP H | TCP H | App H |  Data | Eth T |
+-------+------+-------+-------+-------+-------+
   │
   ▼  bits over wire
```

Receiving end DEcapsulates in reverse.

## Why Modern Engineers Still Care

- **Debugging** — "Is this an L4 issue (TCP reset) or L7 (HTTP 503)?"
- **Load Balancers** — L4 LB (NLB, HAProxy) vs L7 LB (ALB, Envoy, Nginx)
- **Firewalls** — packet filter (L3/4) vs WAF (L7)
- **CDN** — operates L3/4 (anycast) + L7 (HTTP caching)
- **Service Mesh** — entirely L7 (HTTP/gRPC routing)

## Where the Boundaries Blur

- **TLS straddles 5/6/7** (session + presentation)
- **QUIC bundles 4+5+TLS** into UDP for HTTP/3
- **WireGuard tunnels L3 over UDP** (so an "L3 protocol" rides L4)
- **Service meshes do L7 routing of L4 connections**

A staff engineer recognizes these blurs rather than rigidly mapping protocols to layers.

## Production Vocabulary

| Term | Layer | Meaning |
|---|---|---|
| MAC address | 2 | 48-bit hardware address |
| ARP | 2.5 | Resolves IP → MAC on LAN |
| IP address | 3 | 32-bit (v4) or 128-bit (v6) host address |
| Subnet | 3 | A range of IPs sharing a routing prefix |
| Port | 4 | 16-bit endpoint identifier (TCP/UDP) |
| Socket | 4 | (IP, port) tuple |
| Connection | 4 | (src IP, src port, dst IP, dst port, protocol) |
| URL | 7 | Universal Resource Locator |

## Interview Themes

- "Walk me through what happens when you type google.com in a browser" (all layers)
- "What's the difference between L4 and L7 load balancing?"
- "Where does TLS fit in the OSI model?"
- "Diagnose: I see TCP retransmits — which layer?"

## Hands-On Lab

Use `tcpdump -i any -nn -X port 443` to capture a TLS handshake. Open in Wireshark. Identify:
- L2 (Ethernet) header
- L3 (IP) header
- L4 (TCP) header
- L7 (TLS) ClientHello

This builds intuition that lasts a career.

## Recommended Reading

- *TCP/IP Illustrated, Vol 1* — Stevens (still the canonical reference)
- *Computer Networking: A Top-Down Approach* — Kurose & Ross
- RFC 1122 (Requirements for Internet Hosts)
