# L20/C01/T02 — Defense in Depth

## Learning Objectives

- Layer security
- Avoid single point

## Principle

Multiple security layers:
- One fails, others remain
- Reduce blast radius

For: assume layers fail.

## Layers

### Perimeter
- Firewall
- DDoS
- WAF
- VPN

### Network
- Segmentation
- NSG / SG
- Egress control

### Compute
- Hardened OS
- Patching
- Endpoint protection
- Container runtime security

### Application
- Input validation
- AuthN/Z
- Rate limit
- CSRF / XSS protection

### Data
- Encryption at rest
- Encryption in transit
- Access control
- DLP

### Identity
- MFA
- Strong passwords
- Conditional access
- PIM (privileged identity mgmt)

### Monitoring
- IDS / IPS
- SIEM
- Anomaly detection

### Process
- Code review
- Threat modeling
- Pen testing
- Postmortems

## Example: API

```
Internet
  ↓
DDoS protection (Cloudflare)
  ↓
WAF (rules)
  ↓
LB + TLS
  ↓
Auth gateway (MFA)
  ↓
Service mesh (mTLS)
  ↓
App (input validation)
  ↓
DB (encryption, RBAC)
```

Multi-layer.

## Failure Modes

If one layer fails:
- WAF bug: app validation catches
- App bug: DB RBAC limits damage
- DB breach: encryption + key separation

Each layer: backstop.

## Single Point Failures

### Single Firewall
If exploited: all behind exposed.

### Single Auth Service
If down: all access broken.

For: redundancy + diversity.

## Zero Trust

Don't trust anything by default:
- Verify every request
- Never trust network alone
- Least privilege

(See L20/C08.)

## Diversity

Different products / vendors:
- One vendor exploit doesn't break all
- E.g. firewall + WAF different brands

For: avoid monoculture.

## Cost vs Risk

Each layer:
- Cost
- Operational overhead
- Diminishing returns

For: balance.

## Critical First

Layers prioritized:
- MFA (huge ROI)
- Encryption (compliance)
- Patching (huge ROI)
- WAF (some)

For: top layers first.

## Examples

### Cloud
- VPC isolation
- Security groups
- IAM
- Encryption
- KMS
- Audit logs

Many layers.

### Container
- Image scanning
- Runtime policy (PSS)
- Network policy
- mTLS
- Audit

### Code
- Static analysis
- Dependency scan
- Code review
- Pen test

## Detection in Depth

Multi-layer monitoring:
- Network IDS
- App WAF
- Audit logs
- Behavioral analysis

For: see attacks across layers.

## Common Mistakes

### Single Strong Layer
"WAF is enough."

No; layers needed.

### Skip Internal
"Internal network = trusted."

False; insider threats + breach.

### Compliance Min
"PCI checklist done."

Not enough.

## Real Examples

### Equifax (2017)
- Apache Struts unpatched (single layer)
- No segmentation
- Plaintext credentials

Multi-layer would have helped.

### Target (2013)
- HVAC vendor breached
- Network not segmented
- Reached card data

Layer: segment.

## Best Practices

- Multiple layers
- Different vendors (diversity)
- Test each layer
- Update each
- Monitor
- Pen test

## Common Mistakes

- One product trust
- Internal "trusted"
- Compliance minimum
- No updates

## Diagram

```
Internet → Edge → DMZ → App → DB
   Each: own controls
   Logs aggregated
   Each: tested
```

## Quick Refs

```
Layers:
- Perimeter
- Network
- Compute
- App
- Data
- Identity
- Monitoring
- Process

Principle: assume each fails
```

## Interview Prep

**Mid**: "Defense in depth."

**Senior**: "Layer design."

**Staff**: "Security architecture."

## Next Topic

→ [T03 — Least Privilege](T03-Least-Privilege.md)
