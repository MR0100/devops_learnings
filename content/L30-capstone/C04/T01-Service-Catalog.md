# L30/C04/T01 — Service Catalog

## Learning Objectives

- Build Backstage catalog
- Service discovery

## Why a Service Catalog

The problem an IDP solves is **cognitive load at scale**: at 100 services nobody
knows who owns what, where the runbook is, or which dashboard to open during an
incident. The catalog is the single source of truth that answers "what services
exist, who owns them, and how are they wired together." Everything else in
Backstage (templates, plugins, TechDocs) hangs off catalog entities — so this is
the foundation of the IDP capstone.

The capstone's headline metric is **time-to-first-deploy** dropping from days to
minutes; the catalog is what makes that measurable and what keeps the generated
services discoverable afterward.

### Rationale & Trade-offs

- **`catalog-info.yaml` in each repo + auto-discovery** over a central registry —
  ownership lives next to the code, so it's updated in the same PR and can't rot
  into a stale central spreadsheet. Trade-off: you depend on every repo having
  the file (enforce it in the golden-path template).
- **Entity model (Component / System / API / Group)** — models reality:
  Components belong to Systems, expose APIs, owned by Groups. It's more upfront
  modeling than a flat list, but it's what powers dependency views and ownership
  routing.

## Backstage

```bash
npx @backstage/create-app
```

## Catalog

```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: my-service
  description: My service
  tags: [web, api]
  links:
    - url: https://github.com/org/my-service
      title: Repo
spec:
  type: service
  lifecycle: production
  owner: team-a
  system: main
```

## Auto-Discovery

```yaml
# app-config.yaml
catalog:
  locations:
    - type: github-discovery
      target: https://github.com/org/*
```

Scans repos for catalog-info.yaml.

## API Spec

```yaml
apiVersion: backstage.io/v1alpha1
kind: API
metadata:
  name: my-api
spec:
  type: openapi
  lifecycle: production
  owner: team-a
  definition: |
    openapi: 3.0.0
    ...
```

For: API discovery.

## System / Domain

```yaml
kind: System
metadata:
  name: payments
spec:
  owner: team-a
  domain: ecommerce
```

For: hierarchy.

## Owner Display

```yaml
kind: Group
metadata:
  name: team-a
spec:
  type: team
  children: []
```

## Best Practices

- catalog-info.yaml mandatory
- Auto-discovery
- Standard structure
- Ownership clear

## Common Mistakes

- Stale entries
- No ownership
- Missing API specs

## Acceptance Criteria

- Auto-discovery imports every repo's `catalog-info.yaml` (no manual entry)
- Each Component has a real owner (a Group), not "unknown"
- Systems/APIs are modeled so the catalog shows ownership and relationships
- A new service created by the template (T02) appears in the catalog
  automatically

## Quick Refs

```yaml
kinds: Component / API / System / Domain / Group / User / Resource
Discovery: github-discovery / github-org
catalog-info.yaml lives in each repo; auto-discovered (ownership next to code)
```

## Interview Prep

**Junior**: "What is a service catalog?" — It's a single place that lists all
your services with who owns them, links to their repo, docs, and dashboards. In
Backstage it's built from a `catalog-info.yaml` file in each repo.

**Mid**: "Why keep ownership in the repo instead of a central registry?" — Putting
`catalog-info.yaml` in each repo means ownership and metadata are updated in the
same PR as the code, by the people who own it, so it stays current.
Auto-discovery then pulls it all into Backstage. A central spreadsheet or
registry drifts because updating it is a separate, easily-skipped step.

**Senior**: "How does the catalog become the backbone of the whole platform?" —
Every other capability keys off catalog entities: templates register new
Components into it, plugins (Kubernetes, Grafana, PagerDuty) read a Component's
annotations to show pods, dashboards, and on-call on its page, and ownership
routing (who to page, who approves) comes from the Group relationships. So the
catalog isn't a directory — it's the index that lets the platform answer "for
*this* service, show me everything" during an incident or a change. Get the
entity model right (Components in Systems, owned by Groups, exposing APIs) and
those features compose; get it wrong and every plugin shows half the picture.

**Staff**: "The catalog is full of stale and unowned entries. How do you fix it
systemically?" — Stale catalogs are a process problem, not a data problem.
First, make correct metadata the path of least resistance: the golden-path
template emits a complete `catalog-info.yaml`, so every *new* service is right by
construction. Second, enforce it — a CI check (or admission-style gate) that
fails if a repo has no owner or an invalid entity, so 'unowned' can't merge.
Third, automate decay detection: flag Components with no recent commits or
deploys for an ownership review, and tie the catalog to real signals (deploys,
PagerDuty services) so an entry that nothing maps to surfaces as a candidate for
archival. The principle is that metadata which isn't enforced and isn't derived
from reality will always rot — so you either generate it or gate on it, never
rely on humans to remember.

## Next Topic

→ [T02 — Golden Path Templates](T02-Golden-Templates.md)
