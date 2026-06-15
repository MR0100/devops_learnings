# L20/C09/T03 — PCI DSS

## Learning Objectives

- Understand PCI DSS
- Scope minimization

## PCI DSS

Payment Card Industry Data Security Standard:
- For orgs handling cards
- v4.0 latest (2024+)
- Mandated by card brands

## Levels

Based on volume:
- L1: 6M+ tx/year (full audit)
- L2: 1M-6M
- L3: 20k-1M
- L4: < 20k

L1: external QSA audit.
L2-4: self-assessment (mostly).

## 12 Requirements

1. Install + maintain firewall
2. Don't use vendor defaults
3. Protect stored cardholder data
4. Encrypt transmission
5. Use + update anti-virus
6. Develop + maintain secure systems
7. Restrict access
8. Authenticate access
9. Restrict physical access
10. Track + monitor access
11. Test security regularly
12. Maintain info security policy

## Cardholder Data

CHD:
- PAN (Primary Account Number)
- Cardholder name
- Expiration
- Service code

Sensitive:
- CVV
- Full track data
- PIN

PAN: tokenize / encrypt.
CVV: never store post-auth.

## Tokenization

```
Card 4111-1111-1111-1111
   ↓
Token "tok_abc123"
```

Token stored; card in PCI vault.

Tools:
- Stripe
- Braintree
- TokenEx

For: reduce PCI scope.

## Scope Reduction

For NOT in scope:
- Don't store CHD
- Use tokenization
- Outsource (Stripe.js)

Result: less audit.

## Network Segmentation

CDE (Cardholder Data Environment):
- Isolated
- Strict access
- Logs

Other systems:
- Out of scope
- Easier compliance

## Encryption

At rest:
- Strong crypto
- Key mgmt

In transit:
- TLS 1.2+
- Strong ciphers

## Logging

Track:
- Access to CHD
- Admin actions
- Login attempts

Retain 1 year (3 months online).

## Vulnerability Management

- Patching
- ASV (Approved Scanning Vendor) external scan quarterly
- Internal scan
- Pen test annually

## Pen Test

Annual + on significant change.

By qualified party.

## Compliance Validation

- L1: QSA audit
- L2-4: SAQ (Self-Assessment Questionnaire)

SAQ types:
- SAQ A: outsourced
- SAQ A-EP: outsourced with redirect
- SAQ D: handles CHD

For most modern: SAQ A (Stripe Checkout).

## Stripe / Braintree

Hosted payment:
- Customer enters card on Stripe
- Token to merchant
- Merchant: SAQ A (simplest)

For: most SaaS, this path.

## PCI in Cloud

- AWS PCI-compliant (services)
- Azure PCI
- GCP PCI
- You implement controls; cloud verifies infrastructure

Shared responsibility.

## v4.0 Changes

- Customized approach (flexibility)
- More controls (~64 new)
- More documentation
- MFA broader

## Cost

- L1 audit: $30-200k
- Tools, training: $$
- Annual

For: justify with revenue.

## When PCI

- Process cards directly
- Store CHD
- Touch CHD

For: payment-facing.

## Tools

- Drata / Vanta (mapping)
- Aqua (compliance)
- Cloud-native (AWS Inspector, Azure Defender)

## Best Practices

- Tokenize (reduce scope)
- Hosted payment (SAQ A)
- Network segmentation
- Encryption everywhere
- Strict access
- Continuous monitoring

## Common Mistakes

- Store cards on server (scope explodes)
- No tokenization
- Mix CHD + other data
- Log CHD
- Skip pen test

## Quick Refs

```
12 requirements
4 levels (volume)
SAQ types (validation)

Tokenize → SAQ A
Don't store CVV
Pen test annually
Quarterly ASV scan
```

## Interview Prep

**Junior**: "What is PCI DSS?" — The Payment Card Industry Data Security Standard: a set of requirements any organization handling cardholder data must meet to protect that data (encryption, access control, network segmentation, monitoring).

**Mid**: "What is PCI scope and why does it matter?" — Scope is every system that stores, processes, or transmits cardholder data, plus connected systems; the larger the scope, the more systems must meet the full standard, so reducing scope directly reduces compliance cost and risk.

**Senior**: "How do you reduce PCI scope?" — Don't store card data when you can avoid it: use tokenization and a third-party/hosted payment page so raw PAN never touches your systems, and network-segment the cardholder data environment so unrelated systems fall out of scope.

**Staff**: "How do you approach PCI DSS in a cloud environment?" — Lean on the shared-responsibility model and a PCI-compliant provider for infrastructure controls, minimize and isolate the CDE (segmented accounts/VPCs, tokenization, hosted payment flows), automate evidence and continuous control monitoring, and architect so the in-scope footprint is as small and well-bounded as possible.

## Next Topic

→ [T04 — HIPAA, GDPR, FedRAMP](T04-HIPAA-GDPR-FedRAMP.md)
