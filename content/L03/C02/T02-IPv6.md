# L03/C02/T02 — IPv6 (Why It Matters Now)

## Learning Objectives

- Understand IPv6 addressing and notation
- Compare IPv6 to IPv4
- Recognize IPv6 use cases in cloud

## The Address

128 bits, 8 groups of 4 hex digits:
```
2001:0db8:85a3:0000:0000:8a2e:0370:7334
```

Total addresses: 3.4 × 10^38 (effectively unlimited).

## Shortening Rules

- Drop leading zeros in groups: `0db8` → `db8`
- Replace contiguous zero groups with `::` (once per address)

Examples:
- `2001:0db8:0000:0000:0000:0000:0000:0001` → `2001:db8::1`
- `fe80:0000:0000:0000:1234:5678:9abc:def0` → `fe80::1234:5678:9abc:def0`
- `0000:0000:0000:0000:0000:0000:0000:0001` → `::1` (loopback)
- `0000:0000:0000:0000:0000:0000:0000:0000` → `::` (unspecified)

## Important Ranges

| Range | Purpose |
|---|---|
| `::1/128` | Loopback (= 127.0.0.1) |
| `::/128` | Unspecified |
| `fe80::/10` | Link-local (auto-configured) |
| `fc00::/7` | Unique Local Addresses (ULA; like RFC 1918) |
| `2000::/3` | Global Unicast (routable Internet) |
| `ff00::/8` | Multicast |
| `2001:db8::/32` | Documentation (like 192.0.2.0/24 in IPv4) |

## CIDR in IPv6

Subnetting works the same. Typical allocations:
- ISP gives you a /48 (65,536 /64 networks)
- Each /64 is a single subnet, leaving 64 host bits — that's 2^64 ≈ 1.8 × 10^19 addresses per subnet (vastly more than any LAN needs; this is by design, since SLAAC assumes a /64)
- Always use /64 for end networks

## IPv6 vs IPv4

| | IPv4 | IPv6 |
|---|---|---|
| Address size | 32 bits | 128 bits |
| Notation | dotted decimal | colon hex |
| Header size | 20-60 bytes | 40 bytes (fixed) |
| NAT | usually | rarely needed |
| Broadcast | yes | no (multicast only) |
| ARP | yes | NDP (Neighbor Discovery) |
| DHCP | typical | SLAAC or DHCPv6 |
| Configuration | mostly DHCP | mostly auto |

## Why IPv6 Hasn't Fully Won

- NAT extended IPv4's life
- Existing infra all IPv4
- Inertia + cost of dual-stack
- Some apps hardcode IPv4 expectations

But growing:
- Mobile networks heavily IPv6
- Cloud providers IPv6-native increasingly
- Some regions (Asia) have IPv4 scarcity forcing IPv6

## IPv6 in AWS

VPC supports dual-stack:
- IPv4 + IPv6 simultaneously
- IPv6 CIDR assigned by AWS (you don't choose)
- /56 per VPC; /64 per subnet
- No NAT (every IPv6 is publicly routable)

Egress-Only Internet Gateway (EIGW): IPv6 equivalent of NAT — allows outbound, blocks inbound.

## Dual Stack

Run both:
```
Pod has IPv4 + IPv6 addresses
DNS returns both A (IPv4) and AAAA (IPv6) records
Client picks (typically IPv6 preferred via "Happy Eyeballs")
```

## Happy Eyeballs (RFC 8305)

Client tries IPv6 + IPv4 in parallel; uses whichever responds first. Avoids slow fallback when IPv6 broken.

## Common IPv6 Configurations

### SLAAC (Stateless Address Autoconfiguration)
- Router advertises prefix
- Host generates its own address (typically from MAC)
- No DHCP needed
- Common on Linux

### DHCPv6
- Centralized address management
- More like IPv4 DHCP
- Used in enterprises

## Kubernetes IPv6

K8s supports dual-stack:
- Pods get IPv4 + IPv6
- Services dual-stack
- Useful for IPv6-only clusters or migration

## DNS for IPv6

- A record → IPv4
- AAAA record → IPv6
- Reverse: ip6.arpa (PTR records)

## Operations

```bash
ip -6 addr show               # IPv6 addresses
ip -6 route show              # IPv6 routes
ping6 google.com              # ping (newer ping handles both)
traceroute6 google.com
ss -t6                        # IPv6 TCP sockets
curl -6 https://example.com   # force IPv6
```

## Common Issues

- **Firewall rules not duplicated for IPv6** → traffic blocked silently
- **Apps hardcode IPv4** → don't work on IPv6
- **MTU smaller on tunnels** → fragmentation issues
- **No IPv6 in legacy app** → forced IPv4-only deployment

## Should You Use IPv6?

| Need | Verdict |
|---|---|
| Internal-only K8s cluster | IPv4 (simpler; most teams) |
| Public-facing service | Dual-stack (don't lose IPv6 users) |
| Mobile app | Definitely (mobile carriers IPv6-heavy) |
| Greenfield in 2025+ | Consider dual-stack |
| IPv4 exhaustion in your region | Yes |

## Common Mistakes

- **Using `::` twice in one address**: the double-colon zero-compression is allowed only once — `2001:db8::1::2` is invalid and ambiguous.
- **Subnetting smaller than /64 for a LAN**: SLAAC and many features assume a /64. Carving /112 or /120 "to save space" breaks autoconfiguration; address space is not the constraint in IPv6.
- **Forgetting AAAA records or dual-stack firewall rules**: adding IPv6 connectivity without an AAAA record (or with IPv4-only ACLs) silently leaves IPv6 paths broken or wide open.
- **Assuming NAT exists**: every global IPv6 address is publicly routable. Inbound is reachable by default — you must use firewall rules / Egress-Only IGW, not NAT, to restrict it.
- **Treating fe80:: link-local as routable**: link-local addresses require a zone index (`%eth0`) and never cross a router; don't hand them out as service endpoints.
- **Ignoring Happy Eyeballs implications**: a broken-but-present IPv6 path adds connection latency as clients race and fall back. Half-configured IPv6 is often worse than none.

## Best Practices

- **Always use /64 for end networks**; allocate /56 (or AWS-assigned /56) per VPC and /64 per subnet. Keep the prefix hierarchy consistent.
- **Run dual-stack for public-facing services**: publish both A and AAAA, mirror every firewall/security-group rule for IPv6, and test both paths explicitly.
- **Validate IPv6 reachability end-to-end before relying on it** (`curl -6`, `ping6`) — Happy Eyeballs masks a broken IPv6 path behind IPv4, hiding the misconfig until it bites.
- **Use Egress-Only Internet Gateway (AWS) for outbound-only IPv6**, the equivalent of NAT's "outbound yes, inbound no" semantics.
- **Allow the right ICMPv6 types**: Neighbor Discovery (NS/NA), Router Advertisement, and Packet Too Big are mandatory — blocking them breaks address resolution and PMTUD.

## Quick Refs

| Range | Purpose |
|---|---|
| `::1/128` | Loopback (= 127.0.0.1) |
| `::/128` | Unspecified |
| `fe80::/10` | Link-local (needs `%iface` zone) |
| `fc00::/7` | Unique Local (ULA; ~RFC 1918) |
| `2000::/3` | Global Unicast (routable) |
| `ff00::/8` | Multicast (replaces broadcast) |
| `2001:db8::/32` | Documentation only |

IPv4 → IPv6 mental map: ARP → NDP · DHCP → SLAAC/DHCPv6 · broadcast → multicast · A → AAAA · in-addr.arpa → ip6.arpa.

```bash
ip -6 addr show                 # interface IPv6 addresses
ip -6 route show                # IPv6 routing table
ip -6 neigh                     # NDP cache (IPv6 "ARP")
ping6 -c1 google.com            # or: ping -6
curl -6 https://example.com     # force IPv6 path
dig AAAA example.com            # IPv6 address record
ping6 fe80::1%eth0              # link-local needs zone index
```

## Interview Prep

**Mid**: "What's an IPv6 address look like?"

**Senior**: "Why hasn't IPv6 fully replaced IPv4?"

**Staff**: "Design dual-stack support for an existing IPv4-only service."

## Next Topic

→ [T03 — TCP Three-Way Handshake & Termination](T03-TCP-Handshake.md)
