# L03/C03/T02 — Record Types

## Learning Objectives

- Identify each DNS record type and use
- Apply correct records for common scenarios
- Recognize record syntax in zone files

## Common Types

| Type | Purpose | Example |
|---|---|---|
| A | IPv4 address | `example.com. A 93.184.216.34` |
| AAAA | IPv6 address | `example.com. AAAA 2606:2800::1` |
| CNAME | Alias to another name | `www CNAME example.com.` |
| MX | Mail server | `example.com. MX 10 mail.example.com.` |
| TXT | Arbitrary text | `example.com. TXT "v=spf1 ..."` |
| NS | Authoritative nameservers | `example.com. NS ns1.example.com.` |
| SOA | Start of Authority | (zone metadata) |
| SRV | Service location | `_sip._tcp SRV 0 5 5060 sip.example.com.` |
| PTR | Reverse DNS (IP→name) | `34.216.184.93.in-addr.arpa. PTR example.com.` |
| CAA | Cert Authority Authorization | `example.com. CAA 0 issue "letsencrypt.org"` |

## A and AAAA

The fundamental records.
- A: 32-bit IPv4
- AAAA: 128-bit IPv6
- Multiple records per name = round-robin LB

## CNAME

Alias from one name to another. Resolver follows.

```
www.example.com. CNAME example.com.
example.com.     A     93.184.216.34
```

Browsers querying www → see CNAME → query example.com → get IP.

### CNAME Rules
- **A CNAME cannot coexist with other records at the same name** (RFC)
- **The zone apex (root) cannot be a CNAME**

Apex limitation → `example.com` can't be a CNAME → can't easily point to ALB DNS. Workarounds:
- AWS Route 53 alias records (acts like CNAME at apex)
- Cloudflare CNAME flattening
- ALIAS / ANAME records (some providers)

## MX

Mail routing. Lower priority = preferred.

```
example.com. MX 10 mail1.example.com.
example.com. MX 20 mail2.example.com.
```

Receivers try priority 10 first; fall back to 20.

## TXT

Arbitrary strings. Common uses:
- **SPF**: email anti-spoofing
  ```
  example.com. TXT "v=spf1 ip4:1.2.3.4 include:_spf.google.com -all"
  ```
- **DKIM**: email signature key
- **DMARC**: email policy
- **Domain verification**: prove ownership for Google Workspace, etc.

## SRV

Service location with priority + weight + port.

```
_sip._tcp.example.com. SRV 0 5 5060 sip.example.com.
                            │ │ └─ port
                            │ └─ weight (within same priority)
                            └─ priority
```

Used by: SIP, XMPP, K8s headless services.

## NS

Where authoritative servers live.

At TLD: `example.com. NS ns1.example.com.`
At apex: `example.com. NS ns1.example.com.` (consistency)

## SOA

One per zone. Metadata:
```
example.com. SOA ns1.example.com. admin.example.com. (
    2026060901  ; serial (increment on change)
    7200        ; refresh (secondary checks every)
    3600        ; retry (on failure)
    1209600     ; expire (after no refresh)
    86400       ; minimum TTL
)
```

## CAA

Authorize specific CAs to issue certs.

```
example.com. CAA 0 issue "letsencrypt.org"
example.com. CAA 0 issuewild ";"     # no wildcards
example.com. CAA 0 iodef "mailto:security@example.com"
```

Other CAs see this and refuse to issue. Defense against rogue cert issuance.

## ALIAS / ANAME (Provider-Specific)

Like CNAME but works at apex. Route 53 alias records, Cloudflare CNAME flattening.

## PTR

Reverse DNS. Used by mail servers to verify sender.

```
34.216.184.93.in-addr.arpa. PTR example.com.
```

Special domain `in-addr.arpa` for IPv4, `ip6.arpa` for IPv6.

## DS, DNSKEY, RRSIG

DNSSEC. Cryptographic verification. Covered in T04.

## Zone File Format

```
$ORIGIN example.com.
$TTL 3600

@   IN  SOA   ns1.example.com. admin.example.com. (
                2026060901 7200 3600 1209600 86400 )
@   IN  NS    ns1.example.com.
@   IN  NS    ns2.example.com.
@   IN  A     93.184.216.34
@   IN  MX 10 mail.example.com.
www IN  CNAME @
mail IN A    93.184.216.35
```

`@` = origin (zone name).

## Operations

```bash
dig example.com A
dig example.com AAAA
dig example.com MX
dig example.com TXT
dig example.com NS
dig example.com SOA
dig +noall +answer example.com ANY    # all records (some servers refuse ANY)
```

## Interview Prep

**Junior**: "What's a CNAME?"

**Mid**: "Why can't zone apex be a CNAME?"

**Senior**: "How does Route 53's alias work around the CNAME apex limitation?"

**Staff**: "SPF/DKIM/DMARC — explain."

## Next Topic

→ [T03 — DNS Caching, TTLs, and Why TTLs Lie](T03-Caching-TTLs.md)
