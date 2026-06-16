# L20/C01 — Security Mindset

## Topics

- **T01 Threat Modeling (STRIDE, PASTA)** — Structured threat analysis
- **T02 Defense in Depth** — Multiple layers
- **T03 Least Privilege** — Minimum access

## Why Mindset First

Security isn't a feature; it's a way of thinking. Engineers who internalize the mindset write better systems by default. Engineers who treat security as a checklist miss things checklists can't catch.

## STRIDE

A threat modeling framework from Microsoft:

| Letter | Threat | Example | Mitigation |
|---|---|---|---|
| S | Spoofing identity | Stolen token used | MFA, mTLS, short tokens |
| T | Tampering with data | DB record modified | Signing, audit logs |
| R | Repudiation | "I didn't do that" | Signed audit logs |
| I | Information disclosure | Data leak | Encryption, access controls |
| D | Denial of service | DDoS, resource exhaustion | Rate limiting, autoscaling |
| E | Elevation of privilege | Container escape | Least priv, sandboxing |

For each component in your system, ask which STRIDE risks apply. Add mitigations.

## PASTA

Process for Attack Simulation and Threat Analysis. 7 stages from business objectives down to attack tree. Heavier than STRIDE; used for high-value systems.

## Threat Modeling in Practice

### Quick STRIDE
1. Draw the system: components + data flows
2. For each component + flow:
   - Which STRIDE threats apply?
   - What's the impact?
   - What mitigations exist?
3. Identify gaps; create work items

### Example: User Login Flow

```
[User] → HTTPS → [Auth Service] → [DB] → User Record
```

| Component | Threat | Mitigation |
|---|---|---|
| HTTPS in transit | Spoofing (TLS interception) | TLS 1.3, HSTS, cert pinning (mobile) |
| Auth Service | DoS (login spam) | Rate limiting, CAPTCHA |
| Auth Service | Tampering (request modification) | Signed requests, replay protection |
| DB | Information Disclosure | At-rest encryption, KMS, IAM auth |
| User Record | Tampering (account takeover) | Audit log, anomaly detection |

## Defense in Depth

> No single security control is sufficient. Stack many; assume each can fail.

Layers for a typical app:
1. **Network**: VPC isolation, security groups, NetworkPolicy
2. **Identity**: IAM, RBAC, OIDC
3. **Application**: input validation, secure coding
4. **Data**: encryption at rest + transit
5. **Endpoint**: container hardening
6. **Runtime**: Falco, anomaly detection
7. **Audit**: logs, alerting

Even if one layer fails (e.g., container escape), others stand.

## Least Privilege

Every principal (user, service, system) has only the minimum permissions needed.

### Practice
- IAM roles per service (not per team)
- Read-only by default; explicitly granted writes
- Time-bound (just-in-time elevation for humans)
- Reviewed quarterly (revoke unused)

### Anti-Patterns
- `*` permissions on `*` resources
- Personal account used for service authentication
- Shared credentials
- Long-lived API keys

## Zero Trust

Modern evolution of defense in depth + least privilege.

Tenets:
1. **Verify explicitly**: every request authenticated + authorized
2. **Least privilege**: minimum access per request
3. **Assume breach**: design for inevitable compromise

Implementation:
- Per-request authn/authz (not perimeter-based)
- Workload identity (SPIFFE/SPIRE, IRSA)
- Continuous evaluation
- Encrypted everything (incl. service-to-service)

## Shift Left

Security in early stages, not just at the gate:
- Developer security training
- IDE plugins flagging vulnerable patterns
- Pre-commit hooks (secret scan, lint)
- PR checks (SAST, SCA)
- IaC scanning (Checkov, tfsec)

Cheaper to fix at PR than in prod.

## Secure by Default

System designs that make insecure config require explicit opt-out:
- S3 bucket created → Block Public Access ON by default
- New AWS account → MFA enforced for root
- New service → mTLS enabled
- Container → no privileged, no root, drop all caps

## Compliance vs Security

- Compliance = meets standard (SOC2, PCI, etc.)
- Security = actually safe
- They're related but not the same
- Compliant systems can be insecure (and vice versa)

Aim for both. Don't let compliance become theater.

## Attacker Mindset

Practice thinking like an attacker:
- "How would I steal this token?"
- "What can I read with this access?"
- "Where does input come from? Is it trusted?"
- "What happens if this fails?"

Red team exercises (people pretending to be attackers) teach this viscerally.

## Common Security Failures

1. **Hardcoded secrets** in code
2. **Overly broad IAM** (admin, root)
3. **No MFA on critical accounts**
4. **Public S3 buckets** with sensitive data
5. **Unpatched CVEs** in production deps
6. **Logs containing PII / tokens**
7. **No alerting on auth failures**
8. **Lateral movement enabled** (no NetworkPolicy)

## Interview Themes

- "Threat model X system using STRIDE"
- "Defense in depth — example"
- "Least privilege — apply to a real system"
- "Zero Trust — concretely"
- "How does shift-left security work?"
