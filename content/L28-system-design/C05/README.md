# L28/C05 — Platform Engineering

## Topics

- **T01 What an IDP Actually Is** — Internal Developer Platform
- **T02 Golden Paths** — Paved roads for common patterns
- **T03 Backstage for Service Catalog** — De-facto standard
- **T04 Crossplane & Compositions** — K8s-native cloud resources

## What an IDP Is

> An Internal Developer Platform: a productized set of self-service abstractions over infrastructure that enables product engineers to focus on business logic.

NOT:
- A wiki of best practices
- A shared K8s cluster
- A Jenkins server with shared library

YES:
- A web portal + APIs + CLI
- Templates for common service types
- Pre-built CI/CD with sensible defaults
- Observability auto-instrumented
- Cost dashboards per team
- Security gates baked in
- Catalog of services with ownership, runbooks, SLOs

## Why Build an IDP

At 100+ engineers, friction adds up:
- New service onboarding takes weeks
- Each team reinvents observability
- Inconsistent security posture
- Each team manages their own infra

At 500+ engineers, friction is dominant:
- Most time spent on undifferentiated work
- Slow time-to-first-deploy
- Bug surfaces multiply across team-specific implementations

IDP standardizes the "boring" parts.

## Components of an IDP

### Service Catalog
- List of all services
- Owner, on-call, runbook, SLOs, dependencies
- Tools: Backstage, OpsLevel, Cortex, Effx

### Templates (Golden Paths)
- "Create new service" templates
- Scaffolds: code skeleton, CI, manifests, dashboards, alerts
- Per service type: CRUD, gRPC, async worker, ML inference, etc.

### Self-Service Provisioning
- Dev: "I need a new Redis"
- IDP: provisions via Crossplane / Terraform
- No ticket; minutes not weeks

### CI/CD Pipelines
- Pre-built per service type
- Security gates (image scan, signing)
- Multi-env promotion

### Observability
- Auto-instrumented (OTel)
- Pre-built dashboards
- SLO tracking
- Burn-rate alerts

### Security
- Pod Security Standards enforced
- NetworkPolicy templates
- Image signing required
- Secrets via Vault / External Secrets

### Cost
- Per-service cost dashboard
- Budget alerts
- Optimization recommendations

### Compliance
- Audit log centralized
- Compliance evidence auto-collected
- Tagged for cost allocation + ownership

## Backstage

Spotify's OSS platform. CNCF Incubating.

```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: payments-api
  description: Handles payment processing
  annotations:
    github.com/project-slug: org/payments-api
    grafana/dashboard-selector: "type=service AND service=payments"
    pagerduty.com/integration-key: ...
  links:
    - url: https://runbook.example.com/payments
      title: Runbook
spec:
  type: service
  lifecycle: production
  owner: team-payments
  system: payments
```

### Plugins
- Source control
- CI/CD
- K8s
- Cloud cost
- PagerDuty
- Tech docs
- Custom internal

### Templates
```yaml
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: go-service
  title: Create a Go HTTP service
spec:
  parameters:
    - title: Basics
      properties:
        name: {type: string, title: "Service name"}
  steps:
    - id: fetch
      action: fetch:template
      input:
        url: ./skeleton
    - id: github
      action: publish:github
      input:
        repoUrl: github.com?owner=org&repo=${{ parameters.name }}
    - id: register
      action: catalog:register
```

Engineer fills form; Backstage creates repo, registers in catalog, sets up CI.

## Golden Paths

> The paved road that "just works" for 80% of cases.

Examples:
- **CRUD service**: REST + Postgres + caching + standard observability
- **gRPC service**: protobuf + load balancing + observability
- **Async worker**: Kafka consumer + idempotency + dead-letter
- **Batch job**: K8s CronJob + retries + observability
- **ML inference**: model serving + autoscaling + monitoring

Each golden path:
- Template generates everything
- Pre-vetted security, observability, deploy
- Maintained by platform team
- Engineers can deviate (with cost/justification)

## Crossplane

K8s-native cloud resource provisioning. Manage AWS/GCP/Azure resources via K8s API.

```yaml
apiVersion: rds.aws.crossplane.io/v1alpha1
kind: DBInstance
metadata:
  name: payments-db
spec:
  forProvider:
    region: us-east-1
    dbInstanceClass: db.t4g.medium
    engine: postgres
    allocatedStorage: 100
  writeConnectionSecretToRef:
    name: payments-db-creds
    namespace: payments
```

Apply via `kubectl apply`. Crossplane provisions the RDS instance.

### Compositions
Bundle: VPC + Subnet + SG + RDS as "DBCluster" composite resource. Devs use simple abstraction; platform owns details.

```yaml
apiVersion: platform.example.com/v1alpha1
kind: PostgresInstance
metadata:
  name: payments-db
spec:
  size: small
  team: payments
```

Composition translates to actual cloud resources.

## Engineering Culture for IDP

### Product Mindset
- Engineers are "customers"
- Discover their pain (interviews, surveys)
- Build what they need
- Measure: adoption, satisfaction, time-to-first-deploy

### Bad: "Build it and they will come"
Just because you built it doesn't mean teams use it. Marketing + onboarding + iteration matter.

### Internal NPS
Measure developer satisfaction. Track per quarter.

## Platform Team Structure

### Size
- 5-10 engineers for IDP team
- Plus 1 PM (Product Manager for the platform)
- Plus 1 designer for the portal

### Sub-Teams
- Catalog + Portal
- CI/CD platform
- K8s platform
- Observability platform
- Cost / FinOps platform
- Security platform

## Measuring Success

- **Adoption rate** (% of services using IDP)
- **Time to first deploy** for new service
- **Developer NPS / satisfaction**
- **Toil reduction** (toil before vs after IDP)
- **Incidents prevented** by IDP guard-rails
- **Cost saved** (standardization eliminates duplicate infra)

## Anti-Patterns

- IDP without product manager → built in vacuum
- IDP that mirrors AWS console (no abstraction)
- "Take it or leave it" — not adoption-friendly
- IDP team isolated from product teams (no feedback)
- Over-abstraction (devs can't escape)
- Under-abstraction (devs still bothered with details)

## Interview Themes

- "What's an IDP?"
- "Backstage — what does it provide?"
- "Golden path — example"
- "Crossplane — what does it solve?"
- "Adoption strategy for new IDP"
