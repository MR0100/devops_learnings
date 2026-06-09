# L30/C04 — Project 4: Internal Developer Platform (Backstage)

## Topics

- **T01 Service Catalog** — All services in one place
- **T02 Golden Path Templates** — Scaffold new services
- **T03 Self-Service Provisioning** — Devs don't need tickets

## Goal

Build a Backstage instance with golden-path templates that scaffold new services end-to-end. Demonstrate "time to first deploy" < 30 minutes for a new service.

## Architecture

```
[Backstage UI]
├── Service Catalog (Components, Systems, APIs)
├── Templates (golden paths)
├── TechDocs (auto-generated docs)
├── Plugins:
│   - Kubernetes (pod status, logs)
│   - Grafana (dashboards)
│   - PagerDuty (oncall)
│   - GitHub
│   - Cost Insights
└── Auth (Google OIDC)

   ↓ Templates use Backstage scaffolder

[GitHub] — repo created
[GitHub Actions] — CI configured
[K8s manifests] — generated
[ArgoCD] — Application registered
[Grafana] — dashboard provisioned
[PagerDuty] — service registered
```

## Backstage Setup

```bash
npx @backstage/create-app
cd my-backstage
yarn dev
```

For production: containerize, deploy to K8s.

## Catalog Entities

```yaml
# catalog-info.yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: payments-api
  description: Handles payment processing
  annotations:
    github.com/project-slug: org/payments-api
    backstage.io/kubernetes-id: payments-api
    pagerduty.com/integration-key: <key>
    grafana/dashboard-selector: "type=service AND service=payments-api"
  links:
    - { url: https://runbook.example.com/payments, title: Runbook }
spec:
  type: service
  lifecycle: production
  owner: team-payments
  system: payments
---
apiVersion: backstage.io/v1alpha1
kind: System
metadata:
  name: payments
spec:
  owner: team-payments
---
apiVersion: backstage.io/v1alpha1
kind: Group
metadata:
  name: team-payments
spec:
  type: team
  members: [alice, bob, carol]
```

Bulk import from GitHub repos.

## Golden Path Template

```yaml
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: go-service
  title: Go HTTP Service
  description: Production-ready Go service
  tags: [go, service, backend]
spec:
  owner: team-platform
  type: service
  
  parameters:
    - title: Service Details
      required: [name, owner, description]
      properties:
        name:
          title: Name
          type: string
          pattern: '^[a-z0-9-]+$'
        owner:
          title: Owner Team
          type: string
          ui:field: OwnerPicker
        description:
          title: Description
          type: string
    - title: Deployment
      properties:
        port:
          title: HTTP Port
          type: integer
          default: 8080
        replicas:
          title: Default Replicas
          type: integer
          default: 3
  
  steps:
    - id: fetch
      name: Fetch base template
      action: fetch:template
      input:
        url: ./content
        values:
          name: ${{ parameters.name }}
          owner: ${{ parameters.owner }}
          description: ${{ parameters.description }}
          port: ${{ parameters.port }}
          replicas: ${{ parameters.replicas }}
    
    - id: publish
      name: Publish to GitHub
      action: publish:github
      input:
        repoUrl: github.com?owner=org&repo=${{ parameters.name }}
        defaultBranch: main
        repoVisibility: private
        protectDefaultBranch: true
        requiredApprovingReviewCount: 1
    
    - id: register
      name: Register in catalog
      action: catalog:register
      input:
        repoContentsUrl: ${{ steps.publish.output.repoContentsUrl }}
        catalogInfoPath: '/catalog-info.yaml'
    
    - id: argo-app
      name: Create ArgoCD Application
      action: http:backstage:request
      input:
        method: POST
        path: '/api/argocd/applications'
        body:
          name: ${{ parameters.name }}
          source: { repoURL: '${{ steps.publish.output.remoteUrl }}', path: 'k8s' }
  
  output:
    links:
      - title: Repository
        url: ${{ steps.publish.output.remoteUrl }}
      - title: Catalog entry
        icon: catalog
        entityRef: ${{ steps.register.output.entityRef }}
```

## Template Content

```
content/
├── catalog-info.yaml          # auto-registers in catalog
├── README.md                  # service docs
├── .github/workflows/ci.yml   # pre-built CI
├── go.mod
├── main.go                    # /healthz, /metrics, /readyz
├── Dockerfile                 # multi-stage, distroless
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── servicemonitor.yaml
│   └── kustomization.yaml
├── grafana/
│   └── dashboard.json
└── runbook.md
```

All pre-templated with `${{values.name}}`-style substitution.

## Devs Flow

1. Open Backstage
2. Click "Create Component" → "Go HTTP Service"
3. Fill form (name, owner, description)
4. Click Create
5. Backstage:
   - Creates GitHub repo
   - Adds CI workflow
   - Registers in catalog
   - Creates ArgoCD app
   - Provisions Grafana dashboard
6. Engineer clones repo, writes business logic
7. Pushes → CI runs → ArgoCD deploys

Time from "click" to "deployed sample service": ~10 minutes.

## Plugins Worth Adding

- **Kubernetes**: shows pod status from catalog page
- **Grafana**: embedded dashboards
- **PagerDuty**: incidents
- **GitHub Pull Requests**: PR queue
- **Cost Insights**: per-service cost
- **TechDocs**: auto-generated docs

## Catalog Discovery

```yaml
# app-config.yaml
catalog:
  providers:
    github:
      organizations: [org]
      catalogPath: /catalog-info.yaml
      schedule: { frequency: { minutes: 30 } }
```

Auto-discovers `catalog-info.yaml` across all org repos.

## RBAC

Backstage permissions framework (or default):
- Read catalog: all engineers
- Edit catalog entry: entity owner
- Create from templates: all engineers
- Modify templates: platform team

## Demo Script

10-min Loom:
1. Backstage tour (1 min)
2. Browse catalog (2 min)
3. Service detail page with K8s + Grafana embedded (2 min)
4. "Create new service" template (2 min)
5. Show generated repo + auto-deployed pod (2 min)
6. Lessons (1 min)

## What to Highlight

- Time to first deploy reduced from days to minutes
- Standardization without forcing
- Self-service (no platform team tickets)
- Catalog as single source of truth

## Lessons Learned

- Templates are hard to make truly reusable
- Adoption requires engagement, not mandate
- Backstage UX limits some use cases
- Customization requires React knowledge

## README Template

```markdown
# Internal Developer Platform (Backstage)

## What This Demonstrates
- Service catalog for 100s of services
- Golden path templates (Go, Python, async worker)
- Self-service service creation
- Embedded observability + on-call links

## Time-to-First-Deploy
< 15 minutes for new Go service

## How to Run
[steps]

## What I Learned
[specifics]
```

## Interview Themes

- "What's an IDP?"
- "Golden paths — what are they?"
- "Adoption strategy"
- "Backstage limitations"
- "Time-to-first-deploy improvement"
