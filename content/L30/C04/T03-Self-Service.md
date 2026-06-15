# L30/C04/T03 — Self-Service Provisioning

## Learning Objectives

- Self-service infra
- No tickets

## Goal

Dev:
- Need DB → click button → get DB

No:
- Ticket
- Wait
- Manual setup

## Why Self-Service (Eliminate the Ticket Queue)

The deepest value of an IDP is removing the platform team from the critical path
of everyday requests. "I need a database" should not become a Jira ticket that
sits for three days. Self-service turns common infrastructure requests into a
button: the developer declares what they want, and an automated, **governed**
system provisions it. The win is velocity *with* guardrails — not a free-for-all.

### The Core Idea: Declarative + Governed

Crossplane lets you expose a simplified, opinionated API (a `PostgreSQLInstance`
CRD) whose **Composition** the platform team controls — so a dev asks for "a 100
GB Postgres" and the platform decides it's an encrypted, backed-up, right-sized
RDS in the right subnet. The developer gets simplicity; the platform keeps the
policy. That separation is the whole point.

### Rationale & Trade-offs

- **Crossplane over a Terraform-ticket** — provisioning happens through the K8s
  API the developer already uses, reconciled continuously like everything else,
  with the platform owning the Composition. Trade-off: you operate Crossplane and
  author Compositions (real upfront work).
- **Guardrails are not optional** — quotas, cost tags, and TTLs for ephemeral
  resources are what keep self-service from becoming a runaway bill. Self-service
  without governance is just a faster way to overspend.

## Crossplane

```yaml
apiVersion: example.org/v1alpha1
kind: PostgreSQLInstance
metadata:
  name: my-app-db
spec:
  parameters:
    storageGB: 100
```

The developer sees this simple CRD; the platform-owned Composition translates it
into a properly-configured AWS RDS (encryption, backups, subnet, sizing) — dev
simplicity, platform control.

## Backstage Integration

Template creates Crossplane resource:
```yaml
steps:
  - id: create-resource
    action: kubernetes:apply
    input:
      manifest: |
        apiVersion: example.org/v1alpha1
        kind: PostgreSQLInstance
        metadata:
          name: ${{ parameters.name }}
        spec:
          ...
```

## Workflow

```
Backstage UI
  → Pick template "PostgreSQL DB"
  → Fill: size, name
  → Submit
  → Backstage creates Crossplane CR
  → Crossplane creates AWS RDS
  → DB ready
  → Connection info → Vault → app reads
```

## Without Crossplane

Alternative:
- Argo Workflows
- Terraform Cloud API
- Custom controllers

## Policy

```yaml
# Limit dev resources
kind: ResourceQuota
spec:
  hard:
    pods: "10"
    persistentvolumeclaims: "5"
```

For: prevent runaway.

## Cost Visibility

- Tag created resources
- Per-team
- Per-service

## Auto-Cleanup

For ephemeral:
```yaml
spec:
  ttl: 7d   # auto-destroy after
```

For: dev environments.

## Best Practices

- Self-service common needs
- Quotas
- Cost visible
- Auto-cleanup ephemeral
- Document

## Common Mistakes

- Too rigid (defeats purpose)
- No quotas
- No cost tracking
- Permanent ephemeral

## Acceptance Criteria

- A developer requests a resource (e.g. a database) from Backstage with no
  ticket and no platform-team involvement
- The resource is provisioned via a platform-owned Composition with encryption,
  backups, and cost tags applied automatically
- Quotas prevent runaway creation; ephemeral resources auto-expire via TTL
- Connection details are delivered to the app securely (e.g. via Vault/secret),
  not pasted by hand

## Quick Refs

```
Tools: Crossplane (K8s-native) / Argo Workflows / TF Cloud API
Dev sees simple CRD; platform owns the Composition (policy)
Guardrails: ResourceQuota + cost tags + TTL on ephemeral
```

## Interview Prep

**Junior**: "What does self-service provisioning mean?" — Developers get the
infrastructure they need (a database, a bucket) by requesting it through a portal
or API, instead of filing a ticket and waiting for the platform team to set it up
manually.

**Mid**: "How does Crossplane enable self-service safely?" — Crossplane lets the
platform team define a simple custom resource (like `PostgreSQLInstance`) backed
by a Composition they control. The developer asks for a database with a couple of
parameters; the Composition turns that into a properly configured RDS —
encrypted, backed up, correctly sized. The developer gets simplicity and the
platform keeps control of how it's actually built, all through the Kubernetes API
they already use.

**Senior**: "What stops self-service from becoming a cost or security disaster?"
— Governance baked into the platform, not bolted on. The Composition enforces
security defaults (encryption, private subnets, backups) so a developer *can't*
provision an insecure database even if they wanted to. Quotas (ResourceQuota,
Crossplane usage limits) cap how much anyone can create, cost tags make every
resource attributable for showback, and TTLs auto-destroy ephemeral environments
so dev sandboxes don't live forever. Self-service without these is just a faster
way to overspend and misconfigure — the guardrails are what make 'no ticket'
responsible rather than reckless.

**Staff**: "How do you decide what to make self-service versus keep gated, and how
does this scale across an org?" — Not everything should be a button. I'd
self-service the high-frequency, low-risk, well-understood requests (a standard
database, a cache, a dev namespace) where a good Composition can encode all the
right decisions — that's where removing the platform team from the loop pays off
most. I'd keep a human in the loop for low-frequency, high-blast-radius, or
poorly-bounded requests (a new VPC, anything touching prod data, novel
architectures) where judgment matters more than speed. The organizing principle
is: automate the decision once you can encode it safely; until then, the ticket
is doing real risk work. At org scale, the platform team's job shifts from
fulfilling requests to *authoring and owning Compositions* — they're building the
paved roads, and the metric of success is what fraction of infra requests never
reach a human. That's leverage: a handful of platform engineers enabling hundreds
of developers, instead of being their queue.

## Next Topic

→ Move to [L30/C05 — Project 5: Cost-Optimized Spot-Heavy Workload Platform](../C05/README.md)
