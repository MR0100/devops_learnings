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

## Common Mistakes

- **Putting a CNAME at the zone apex**: RFC forbids a CNAME coexisting with the SOA/NS records that must live at the apex. Use a provider ALIAS/ANAME, Route 53 alias, or Cloudflare CNAME flattening instead.
- **Adding other records alongside a CNAME**: a name with a CNAME can have *no* other record types. An apex with a CNAME plus MX/TXT is invalid and resolves unpredictably.
- **Pointing MX at a CNAME or an IP**: MX (and NS) targets must be hostnames that resolve to A/AAAA records, never CNAMEs or bare IPs — many mail servers reject the former.
- **Forgetting the trailing dot in zone files**: `mail.example.com` without the dot becomes `mail.example.com.example.com`. Always FQDN-qualify (trailing `.`) or rely deliberately on `$ORIGIN`.
- **Not bumping the SOA serial after edits**: secondaries refresh based on the serial. Editing records without incrementing it leaves slaves serving stale data.
- **Splitting long TXT (SPF/DKIM) incorrectly**: a single TXT string maxes at 255 bytes; longer values must be split into multiple quoted strings that concatenate — a stray space or extra record breaks SPF/DKIM validation.

## Best Practices

- **Use ALIAS/Route 53 alias for apex → load balancer** mapping; reserve CNAME for non-apex subdomains (`www`, `api`).
- **Lock down certificate issuance with CAA** (`0 issue "letsencrypt.org"`, `0 issuewild ";"`) plus an `iodef` contact, so rogue CAs are refused.
- **Keep one authoritative source of truth** (IaC/Terraform or the DNS provider), and auto-increment the SOA serial on every change.
- **Use SRV for service discovery** (SIP, XMPP, Kubernetes headless services) where priority/weight/port belong in DNS rather than hard-coded.
- **Maintain consistent NS records** at both the parent (TLD delegation) and the apex; mismatches cause intermittent "lame delegation" failures.

## Quick Refs

| Type | Purpose | Target form |
|---|---|---|
| A / AAAA | IPv4 / IPv6 address | IP literal |
| CNAME | alias (non-apex only) | another name |
| ALIAS/ANAME | apex alias (provider-specific) | another name |
| MX | mail server (lower pref wins) | hostname (not CNAME/IP) |
| TXT | SPF/DKIM/DMARC, verification | quoted string(s) |
| NS | delegation / authoritative servers | hostname |
| SOA | zone metadata (1 per zone) | serial/refresh/retry/expire/min |
| SRV | service location | priority weight port target |
| PTR | reverse DNS (IP→name) | name in in-addr.arpa/ip6.arpa |
| CAA | authorized cert issuers | flags tag "value" |

SOA fields order: `serial refresh retry expire minimum`. SPF example: `"v=spf1 ip4:1.2.3.4 include:_spf.google.com -all"`.

```bash
dig example.com A          dig example.com AAAA
dig example.com MX         dig example.com TXT
dig example.com NS         dig example.com SOA
dig example.com CAA
dig +noall +answer example.com   # answer section only
dig -x 93.184.216.34             # reverse lookup (PTR)
```

## Interview Prep

**Junior**: "What's a CNAME?"

**Mid**: "Why can't zone apex be a CNAME?"

**Senior**: "How does Route 53's alias work around the CNAME apex limitation?"

**Staff**: "SPF/DKIM/DMARC — explain."

## Next Topic

→ [T03 — DNS Caching, TTLs, and Why TTLs Lie](T03-Caching-TTLs.md)
