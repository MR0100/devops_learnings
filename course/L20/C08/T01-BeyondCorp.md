# L20/C08/T01 — BeyondCorp Model

## Learning Objectives

- Understand Zero Trust
- Apply BeyondCorp

## Old Model

Castle + moat:
```
Untrusted Internet
   ↓
Firewall / VPN
   ↓
Trusted Internal (free movement)
```

Problem:
- Breached perimeter = full access
- VPN bypasses controls
- Insider threats

## Zero Trust

Trust nothing by default:
- Verify every request
- Identity + context
- No "trusted network"

## BeyondCorp

Google's implementation (2014):
- No VPN
- Per-user / per-device verified
- Access based on identity + context

## Principles

1. All access to apps verified
2. Identity not network determines access
3. Per-user, per-device, per-app
4. No implicit trust

## Architecture

```
User → Identity-Aware Proxy
   - Authenticate (SSO + MFA)
   - Check device (managed?)
   - Check context (location, time)
   - Authorize per-app
   ↓
App
```

## Components

### Device Identity
- Certificate per device
- Posture (patched, encrypted, etc.)

### User Identity
- SSO + MFA
- Groups

### Access Tier
- Sensitive: highest bar
- Internal: medium
- Public: minimal

### Inventory
- Devices
- Users
- Apps

### Policy
- Match context to allowed access

## Tools

- Google Identity-Aware Proxy
- Cloudflare Access
- Okta + 3rd party
- Tailscale (network)
- WireGuard
- Zscaler ZPA

## Per-App Auth

```
example.com/finance → Identity Proxy
  - User in Finance group?
  - Device managed?
  - From corporate network or trusted?
  - ✓ Allow
```

## Vs VPN

VPN:
- All-or-nothing
- Stale after compromise

Zero Trust:
- Per-app
- Continuous

## Implementation

### Step 1
- SSO everywhere
- MFA enforced
- Device certs

### Step 2
- Identity proxy in front of apps
- Public IP, but auth required

### Step 3
- Phase out VPN
- Per-app access

### Step 4
- Context-aware policies

Years to fully implement.

## Conditional Access

```
Rule:
  If user in Eng, from managed device, in US: allow GitHub
  If user in Eng, from BYOD: read-only GitHub
  Else: deny
```

For: granular.

## Continuous Verification

Not just at login:
- Re-check periodically
- On context change
- On suspicious activity

## Microsegmentation

Internal services:
- Same Zero Trust
- mTLS between
- AuthZ per call

(See T02, T03.)

## SDP

Software Defined Perimeter:
- Don't expose apps to all
- Issue access per identity
- Hidden until auth

## Examples

### Google
BeyondCorp internal.

### Many Tech Cos
Cloudflare Access for SaaS.

### Cloudflare
Zero Trust for self.

## When Adopt

- Hybrid work
- Many apps
- Compliance
- Security-forward

## Cost

- IAP / Access: per user/month
- Implementation: significant engineering

For: ROI in reduced breach.

## Cultural

- Users adjust (no VPN)
- IT shifts mindset
- Continuous improvement

## Best Practices

- SSO + MFA baseline
- Per-app identity proxy
- Device posture
- Phase out VPN gradually
- Audit access

## Common Mistakes

- "Zero Trust" buzzword without action
- Skip device check
- VPN side-by-side forever
- Trust internal network

## Frameworks

- NIST 800-207
- BeyondCorp papers
- Google whitepapers

## Quick Refs

```
Zero Trust:
- Identity > network
- Per-app, per-user, per-device
- Continuous verification

Tools:
- IAP / Cloudflare Access
- Okta SSO + MFA
- Device cert
```

## Interview Prep

**Mid**: "What's Zero Trust."

**Senior**: "BeyondCorp."

**Staff**: "Zero Trust strategy."

## Next Topic

→ [T02 — Service-to-Service Identity (SPIFFE/SPIRE)](T02-SPIFFE-SPIRE.md)
