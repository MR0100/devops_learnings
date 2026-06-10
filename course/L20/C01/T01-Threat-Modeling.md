# L20/C01/T01 — Threat Modeling (STRIDE, PASTA)

## Learning Objectives

- Do threat modeling
- Apply frameworks

## Threat Modeling

Identify threats before exploit:
- Systematic
- Documented
- Iterative

For: design security in.

## STRIDE

Microsoft framework:
- **S**poofing identity
- **T**ampering with data
- **R**epudiation
- **I**nformation disclosure
- **D**enial of service
- **E**levation of privilege

For: per-component analysis.

## STRIDE Application

For each component, ask:
- Can someone impersonate? (S)
- Can someone modify data? (T)
- Can someone deny actions? (R)
- Can someone read sensitive data? (I)
- Can someone disrupt? (D)
- Can someone gain higher priv? (E)

For: comprehensive.

## PASTA

7-stage:
1. Define objectives
2. Define technical scope
3. App decomposition
4. Threat analysis
5. Vulnerability analysis
6. Attack modeling
7. Risk + impact

For: rigorous.

## DREAD (Older)

Score risks:
- Damage
- Reproducibility
- Exploitability
- Affected users
- Discoverability

For: prioritize.

## LINDDUN

Privacy focus:
- **L**inkability
- **I**dentifiability
- **N**on-repudiation
- **D**etectability
- **D**isclosure of info
- **U**nawareness
- **N**oncompliance

For: GDPR / data.

## Data Flow Diagram

```
User → [Web Server] → [App] → [DB]
                            → [Cache]
                            → [3rd party]
```

Identify:
- Trust boundaries
- Data flows
- Components

## When to Threat Model

- New feature
- New service
- Architecture review
- Regulatory check

## Process

1. Diagram system
2. Identify threats (STRIDE per component)
3. Mitigations
4. Prioritize
5. Implement
6. Verify

## Threat Examples

### Spoofing
- User pretends to be another
- Mitigation: MFA, strong auth

### Tampering
- Modify request data
- Mitigation: signed requests, TLS

### Repudiation
- User denies action
- Mitigation: audit log

### Info Disclosure
- Sensitive data leaked
- Mitigation: encryption, access control

### DoS
- Overwhelm service
- Mitigation: rate limit, DDoS protection

### Elevation
- User gains admin
- Mitigation: least priv, RBAC

## Mitigations Per Threat

```
Threat: SQL injection (Tampering)
Mitigation:
- Parameterized queries
- ORM
- Input validation

Test:
- SQLMap
- Manual fuzz
```

## Tools

- Microsoft Threat Modeling Tool
- OWASP Threat Dragon
- IriusRisk
- Cairis

For: visualization.

## Output

```markdown
## Threat Model: Login Service

### Data Flow
[Diagram]

### Threats

| ID | Threat | STRIDE | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|---|---|
| 1 | Credential stuffing | S | High | High | Rate limit + MFA | Alice |
| 2 | Session hijack | T | Med | High | HttpOnly + Secure cookies | Bob |
| 3 | Password leak | I | Low | High | Hashing (bcrypt) + breach detection | Carol |
```

## Review

After change:
- Re-evaluate threats
- New mitigations needed?

## Continuous

Not one-time:
- Quarterly review
- After incidents
- After architecture changes

## Best Practices

- Diagram first
- STRIDE per component
- Mitigations prioritized
- Documented
- Reviewed regularly

## Common Mistakes

- Skip (focus on testing only)
- One-time
- No mitigation tracking
- Wrong scope

## Quick Refs

```
STRIDE: Spoof, Tamper, Repudiation, Info, DoS, Elevation
PASTA: 7 stages
LINDDUN: privacy
DREAD: scoring (legacy)
```

## Interview Prep

**Mid**: "What's threat modeling."

**Senior**: "STRIDE."

**Staff**: "Threat modeling at scale."

## Next Topic

→ [T02 — Defense in Depth](T02-Defense-in-Depth.md)
