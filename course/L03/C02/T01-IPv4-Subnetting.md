# L03/C02/T01 — IPv4 Addressing, Subnetting, CIDR

## Learning Objectives

- Compute subnet sizes from CIDR notation
- Identify private vs public ranges
- Design network address plans

## IPv4 Address

32 bits, written as 4 octets (dotted decimal):
```
192 . 168 . 1 . 100
1100 0000 . 1010 1000 . 0000 0001 . 0110 0100
```

Range: 0.0.0.0 to 255.255.255.255 (~4.3 billion)

## CIDR Notation

`address/prefix`:
- `192.168.1.0/24` means the first 24 bits are the network; last 8 bits are hosts
- /24 → 256 addresses (254 usable; 2 reserved)
- /16 → 65,536 addresses
- /8 → 16,777,216 addresses

## CIDR Cheat Sheet

| Prefix | Hosts | Block Size | Subnet Mask |
|---|---|---|---|
| /8 | 16,777,214 | 16.7M | 255.0.0.0 |
| /16 | 65,534 | 65K | 255.255.0.0 |
| /20 | 4,094 | 4K | 255.255.240.0 |
| /22 | 1,022 | 1K | 255.255.252.0 |
| /24 | 254 | 256 | 255.255.255.0 |
| /25 | 126 | 128 | 255.255.255.128 |
| /26 | 62 | 64 | 255.255.255.192 |
| /27 | 30 | 32 | 255.255.255.224 |
| /28 | 14 | 16 | 255.255.255.240 |
| /29 | 6 | 8 | 255.255.255.248 |
| /30 | 2 | 4 | 255.255.255.252 |
| /31 | 2 | 2 | 255.255.255.254 (point-to-point) |
| /32 | 1 | 1 | 255.255.255.255 (single host) |

**Formula**: 2^(32 - prefix) - 2 usable hosts (minus network + broadcast).

## Network and Broadcast

For `192.168.1.0/24`:
- Network address: `192.168.1.0` (all host bits = 0)
- Broadcast address: `192.168.1.255` (all host bits = 1)
- Usable: `192.168.1.1` to `192.168.1.254`

AWS reserves 5 IPs per subnet: .0 (network), .1 (router), .2 (DNS), .3 (future), .255 (broadcast).

## Private Address Ranges (RFC 1918)

Non-routable on Internet. Used in internal networks.

| Range | CIDR | Common Use |
|---|---|---|
| 10.0.0.0 — 10.255.255.255 | 10.0.0.0/8 | Big networks (~16M hosts) |
| 172.16.0.0 — 172.31.255.255 | 172.16.0.0/12 | Medium |
| 192.168.0.0 — 192.168.255.255 | 192.168.0.0/16 | Home networks (~65K) |

Other special:
- `169.254.0.0/16` — link-local (APIPA; AWS IMDS at 169.254.169.254)
- `127.0.0.0/8` — loopback
- `224.0.0.0/4` — multicast
- `100.64.0.0/10` — Carrier-Grade NAT

## Subnetting Examples

### Split 10.0.0.0/16 into 4 equal /18 subnets

256 - 64 = 192. So mask is 255.255.192.0.

- 10.0.0.0/18 → 10.0.0.0 - 10.0.63.255
- 10.0.64.0/18 → 10.0.64.0 - 10.0.127.255
- 10.0.128.0/18 → 10.0.128.0 - 10.0.191.255
- 10.0.192.0/18 → 10.0.192.0 - 10.0.255.255

### Split /24 into /27 subnets

256 / 32 = 8 subnets of 32 addresses each:
- 192.168.1.0/27 → .0-.31
- 192.168.1.32/27 → .32-.63
- ...
- 192.168.1.224/27 → .224-.255

## VPC Address Planning

For a multi-account AWS org:
```
10.0.0.0/8 = your reserved space (16M)
  10.0.0.0/16 = shared services VPC
  10.1.0.0/16 = prod-us-east-1
  10.2.0.0/16 = prod-us-west-2
  10.3.0.0/16 = staging
  10.4.0.0/16 = dev
  10.10.0.0/16 = tenant 1
  ...
```

Each /16 holds 65K IPs, plenty for most VPCs.

Within a VPC:
```
10.1.0.0/16 = prod-us-east-1
  10.1.0.0/20 = public subnets (4096 each)
    10.1.0.0/24 = public AZ-a
    10.1.1.0/24 = public AZ-b
    10.1.2.0/24 = public AZ-c
  10.1.16.0/20 = private subnets
    10.1.16.0/22 = private AZ-a (1022 hosts)
    10.1.20.0/22 = private AZ-b
    10.1.24.0/22 = private AZ-c
  10.1.32.0/20 = data subnets
    ...
```

Plan for growth. Hard to renumber later.

## CIDR Overlap

Never overlap CIDR across:
- VPCs you'll peer
- On-prem + cloud (you'll need to connect them)
- Acquired companies

A merger or peering becomes painful if both use 10.0.0.0/16.

## Common Mistakes

- **Too small VPC**: pick /16, not /24
- **/24 for AZ subnet**: only 254 usable IPs → exhausted with many pods/instances
- **Overlapping with existing networks**: peering will fail
- **Forgetting reserved addresses**: AWS reserves 5 per subnet
- **No room for growth**: /22 subnet at 90% saturated, no expansion possible

## CIDR Math Tricks

- /24 → 256, /25 → 128, /26 → 64, /27 → 32, /28 → 16, /29 → 8, /30 → 4
- Each /N+1 = half of /N

## Tools

```bash
ipcalc 192.168.1.0/24             # subnet info
sipcalc 10.0.0.0/16               # alternative
python3 -c "import ipaddress; print(list(ipaddress.ip_network('10.0.0.0/22').hosts())[:5])"
```

## Interview Prep

**Junior**: "What does /24 mean?"

**Mid**: "Split 10.0.0.0/16 into 4 equal subnets."

**Senior**: "Design CIDR for a multi-account org with 50+ VPCs."

**Staff**: "We have two M&A companies, both use 10.0.0.0/8. Plan the integration."
- Renumber one side (slow); use NAT (operational complexity); use overlapping IPs with PrivateLink (clever but limited).

## Next Topic

→ [T02 — IPv6 (Why It Matters Now)](T02-IPv6.md)
