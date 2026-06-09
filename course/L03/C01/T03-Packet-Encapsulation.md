# L03/C01/T03 — Packet Encapsulation

## Learning Objectives

- Understand how data is wrapped at each layer
- Identify headers added by each protocol
- Calculate overhead

## The Concept

As data travels DOWN the stack on the sender, each layer adds a header (and sometimes trailer). On the receiver, it travels UP, with each layer stripping its header.

```
Sender:                       Receiver:
[App data]                    [App data]
[L4 header | App data]        [L4 header | App data]
[L3 header | L4 | App data]   [L3 | L4 | App data]
[L2 hdr | L3 | L4 | App | L2 trailer]   [L2 | ... | trailer]
   ↓ wire ↓                   ↑ wire ↑
```

Each header has just enough info for that layer to do its job.

## Header Sizes

| Layer | Header | Bytes |
|---|---|---|
| Ethernet | Eth header + trailer | 14 + 4 = 18 |
| IPv4 | IP header | 20 (typical) to 60 (with options) |
| IPv6 | IP header | 40 (fixed) |
| TCP | TCP header | 20 (typical) to 60 (with options) |
| UDP | UDP header | 8 |
| TLS | TLS record header | 5 + ~30 for crypto overhead |

For a typical HTTPS request:
- Ethernet: 18
- IPv4: 20
- TCP: 20
- TLS: ~35
- HTTP: variable
- Total framing: ~93 bytes before payload

## MTU and MSS

- **MTU (Maximum Transmission Unit)**: largest L2 frame (typically 1500 bytes on Ethernet)
- **MSS (Maximum Segment Size)**: largest TCP payload, typically MTU − 40 (IP+TCP headers) = 1460

If data > MSS, TCP breaks it into multiple segments.
If a frame > MTU, IP fragments it (avoid; expensive).

## Jumbo Frames

Some networks support MTU 9000 (jumbo frames). Reduces overhead for big transfers:
- 1500 MTU → 1460 payload → 3% overhead
- 9000 MTU → 8960 payload → 0.4% overhead

Used in: data center backbones, storage networks.

## Packet Walk Example

`curl http://example.com/data`:

1. App writes 5000 bytes of HTTP body
2. TCP splits into 4 segments of 1460 + 1 of ~340 bytes
3. Each segment: TCP header (20) + IP header (20) + Eth header/trailer (18) = 58 framing
4. Sent over Ethernet, 5 frames total

Receiver:
1. NIC receives Ethernet frames; strips Eth headers
2. IP layer reassembles if fragmented; strips IP headers
3. TCP layer reorders + acks; strips TCP headers
4. App receives the 5000 bytes

## VLAN Tagging (802.1Q)

Adds 4 bytes to Ethernet header for VLAN ID.

```
[Eth: dest|src|0x8100|VLAN|EtherType|payload|FCS]
```

So MTU effectively becomes 1496 on VLANs (in some implementations).

## Tunneling Adds Overhead

VPNs, overlays add headers:
- **GRE**: 24 bytes
- **VXLAN**: 50 bytes (used in K8s overlay networks)
- **IPSec**: 50-100 bytes
- **WireGuard**: ~60 bytes

K8s with VXLAN: original MTU 1500 → effective 1450 for pods. Mis-configured MTU = mysterious connection hangs.

## Overhead Math

For a 1 GB file transfer over typical Ethernet (1500 MTU):
- ~684K packets
- Framing overhead: ~38 MB (4%)
- Useful payload: ~96%

For tiny requests (DNS query, ~50 bytes):
- Framing dominates payload
- DNS over UDP: 8 (UDP) + 20 (IP) + 18 (Eth) = 46 bytes overhead for 50 bytes data = ~50% overhead

## Wireshark Layer View

In a captured packet, Wireshark displays the encapsulation:

```
Frame 1: ...
+ Ethernet II, Src: aa:bb:cc:..., Dst: dd:ee:ff:...
  + Internet Protocol Version 4, Src: 192.168.1.10, Dst: 93.184.216.34
    + Transmission Control Protocol, Src Port: 54321, Dst Port: 443
      + Transport Layer Security
        + TLSv1.3 Record Layer: Application Data
```

Each "+" you click expands a layer.

## Common Problems

### MTU Mismatch
- Tunnel MTU smaller than local
- Sender sets DF (Don't Fragment) bit
- Packet too big to forward → ICMP "Fragmentation Needed" sent back
- If ICMP blocked → black hole; connection hangs after handshake
- Symptom: "small requests work, big ones don't"

Fix:
- Match MTU on tunnels
- Enable PMTU (Path MTU Discovery)
- Don't block ICMP

### Fragmentation
- IP fragments packets > MTU
- Receiver reassembles
- Loss of any fragment → retransmit whole thing
- Expensive; avoid

Modern TCP uses PMTUD to avoid fragmentation entirely.

## Interview Prep

**Mid**: "What's MTU and why does it matter?"

**Senior**: "Why is TCP MSS = MTU − 40?"
- 20 IP header + 20 TCP header.

**Staff**: "Diagnose: TLS handshake completes, but data transfer hangs."
- Likely MTU mismatch with DF + blocked ICMP. PMTUD broken.

## Hands-On

```bash
# Check MTU on interface
ip link show eth0

# Test largest packet that fits without fragmentation
ping -M do -s 1472 google.com    # 1472 + 28 (ICMP+IP) = 1500
```

Increase -s until "Frag needed and DF set" error appears. That's your PMTU.

## Next Chapter

→ [C02 — IP, TCP, UDP, QUIC](../C02/README.md)
