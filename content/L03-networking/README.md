# L03 — Networking Deep Dive (OSI to BGP)

## Overview

Networking is the #1 source of production incidents in distributed systems. Every senior+ DevOps engineer must be able to: trace packets through a stack, debug TLS handshakes, design VPCs, and explain BGP. This lecture covers each layer in production-grade depth.

**8 chapters, 39 topics.**

## Learning Outcomes

After this lecture, you will:
1. Trace a packet through the OSI/TCP stack from your laptop to a backend service
2. Debug TCP connection issues using `tcpdump`, `ss`, and `wireshark`
3. Explain TLS 1.3 handshake including PSK and 0-RTT
4. Design AWS-style VPCs with PrivateLink, Transit Gateway, Direct Connect
5. Diagnose DNS issues across resolvers, caching, and TTLs
6. Understand BGP, Anycast, and how CDNs route at scale
7. Tune TCP for high-bandwidth-delay-product (BDP) workloads

## Chapter Map

| # | Chapter | Topics | Hours |
|---|---|---|---|
| [C01](C01/) | Network Models (OSI, TCP/IP) | 3 | 2 |
| [C02](C02/) | IP, TCP, UDP, QUIC | 6 | 6 |
| [C03](C03/) | DNS Deep Dive | 5 | 4 |
| [C04](C04/) | HTTP, HTTPS, HTTP/2, HTTP/3 | 5 | 5 |
| [C05](C05/) | TLS / SSL Deep Dive | 5 | 4 |
| [C06](C06/) | Network Troubleshooting | 5 | 5 |
| [C07](C07/) | Cloud & Data Center Networking | 6 | 6 |
| [C08](C08/) | Edge & CDN Networking | 4 | 3 |

## Chapter Outlines

### C01 — Network Models
- T01 OSI Model (All 7 Layers, In Detail)
- T02 TCP/IP Model
- T03 Packet Encapsulation

### C02 — IP, TCP, UDP, QUIC
- T01 IPv4 Addressing, Subnetting, CIDR
- T02 IPv6 (Why It Matters Now)
- T03 TCP Three-Way Handshake & Termination
- T04 TCP Flow Control, Congestion Control, Slow Start
- T05 UDP and When to Use It
- T06 QUIC (and HTTP/3)

### C03 — DNS Deep Dive
- T01 DNS Resolution Flow (Recursive vs Iterative)
- T02 Record Types (A, AAAA, CNAME, MX, TXT, SRV, NS, SOA)
- T03 DNS Caching, TTLs, and Why TTLs Lie
- T04 DNSSEC
- T05 DNS as a Load Balancer (Route53, GeoDNS)

### C04 — HTTP, HTTPS, HTTP/2, HTTP/3
- T01 HTTP Methods, Status Codes, Headers
- T02 HTTPS / TLS Handshake (Step by Step)
- T03 HTTP/2 Multiplexing & Server Push
- T04 HTTP/3 Over QUIC
- T05 Cookies, CORS, Same-Origin Policy

### C05 — TLS / SSL Deep Dive
- T01 Symmetric vs Asymmetric Cryptography
- T02 Certificates, CAs, Chains of Trust
- T03 mTLS (Mutual TLS)
- T04 Cipher Suites, Forward Secrecy
- T05 Certificate Rotation & ACME (Let's Encrypt)

### C06 — Network Troubleshooting
- T01 ping, traceroute, mtr
- T02 tcpdump & Wireshark
- T03 netstat, ss, lsof
- T04 curl and HTTP Debugging
- T05 Reading Real Packet Captures

### C07 — Cloud & Data Center Networking
- T01 VPC, Subnets, Route Tables, IGW, NAT
- T02 VPC Peering, Transit Gateway, PrivateLink
- T03 Direct Connect, VPN
- T04 BGP and Anycast
- T05 SD-WAN
- T06 Load Balancing (L4 vs L7)

### C08 — Edge & CDN Networking
- T01 CDN Topology (PoPs, Origin)
- T02 Anycast IP
- T03 Edge Computing
- T04 DDoS Protection at the Edge

## Key Diagrams

### TCP Handshake
```
Client                  Server
   │ ─── SYN(seq=x) ──► │
   │ ◄ SYN-ACK(seq=y,    │
   │   ack=x+1) ──       │
   │ ─── ACK(ack=y+1) ──►│
   │                     │
   │ ◄ HTTP request/resp ►
```

### TCP Termination
```
Client                  Server
   │ ─── FIN ─────────►  │
   │ ◄── ACK ───         │
   │ ◄── FIN ─────────   │
   │ ─── ACK ────────►   │
```

### TLS 1.3 Handshake (1-RTT)
```
ClientHello + key_share + signature_algos
                         ─────►
                              ServerHello + key_share
                              {EncryptedExtensions, Certificate,
                               CertificateVerify, Finished}
                         ◄─────
{Finished}              ─────►
{HTTP request}          ─────►
```

## Recommended Reading

- *TCP/IP Illustrated* — W. Richard Stevens (Vol 1 timeless)
- *High Performance Browser Networking* — Ilya Grigorik (free online)
- *Computer Networking: A Top-Down Approach* — Kurose & Ross
- Cloudflare blog posts on TLS, HTTP/3, QUIC

## Interview Relevance

- "Trace what happens when you type google.com in a browser" — classic
- "Why is UDP faster than TCP? When would you use each?"
- "Explain TLS 1.3 vs 1.2"
- "Design a multi-AZ VPC"
- "What's BGP and why does it cause global outages?"

## Next

→ [L04 — Shell, Bash & Scripting for Automation](../L04-bash-scripting/README.md)
