# L16/C08/T01 — Spinnaker: Pipelines, Pipeline Templates

## Learning Objectives

- Use Spinnaker
- Multi-cloud deploys

## Spinnaker

Netflix-origin; multi-cloud CD:
- Deploys to K8s, EC2, GCP, Azure
- Pipeline UI
- Canary built-in
- Pipeline templates

## Architecture

Multiple services:
- Deck (UI)
- Gate (API)
- Orca (orchestration)
- Clouddriver (cloud APIs)
- Kayenta (canary analysis)
- Echo (notifications)
- Front50 (storage)
- Igor (CI integration)
- Rosco (image baking)

## Install

```bash
# Halyard
hal deploy apply
```

Or Operator.

K8s-native install heavy; multi-component.

## Pipeline

UI-built:
```
Stages:
1. Configure (trigger)
2. Bake (image)
3. Deploy
4. Manual judgement
5. Production deploy
6. Notification
```

JSON underneath:
```json
{
  "stages": [
    {
      "type": "bakeManifest",
      "templateRenderer": "HELM2",
      ...
    },
    {
      "type": "deployManifest",
      ...
    }
  ]
}
```

## Triggers

- Git push
- Jenkins success
- Pipeline success (chain)
- Manual
- Cron
- Webhook
- Pub/Sub

## Stages

100+ stage types:
- Bake (image)
- Deploy
- Find Image
- Manual Judgement
- Pipeline
- Wait
- Canary Analysis
- Webhook
- Run Job (K8s)

## Pipeline Templates

```yaml
schema: "v2"
variables:
- name: appName
  type: string
- name: cluster
  type: string

pipeline:
  application: ${appName}
  stages:
  - type: deploy
    cluster: ${cluster}
```

For: standardize across services.

Instantiate:
```yaml
schema: "v2"
template:
  source: spinnaker://my-template
variables:
  appName: myapp
  cluster: prod
```

## Multi-Cloud Deploy

```
Spinnaker pipeline:
- Deploy to AWS us-east-1
- Deploy to GCP us-central1
- Deploy to Azure eastus2
```

Sequential or parallel.

## Canary Analysis (Kayenta)

```yaml
- type: kayentaCanary
  canaryConfig:
    metricsAccountName: prometheus
    storageAccountName: gcs
    configurationAccountName: ...
  ...
```

Statistical canary; Netflix pioneered.

For: data-driven promotions.

## Bake Stages

Old: Spinnaker built AMIs via Packer.
Now: Often skip; use pre-built images.

For: legacy AWS use cases.

## Find Image

Look up image by:
- Tag
- Build number
- Trigger

## Manual Judgement

Stage:
- Pause pipeline
- Notify
- User approves / aborts

For: human gate.

## Deploy Strategies

- Highlander (replace all)
- Red/Black (blue/green)
- Rolling
- Canary

Per stage choice.

## Notifications

- Slack
- Email
- Webhook
- PagerDuty

Per-stage.

## Decline

Spinnaker complex; declining vs:
- ArgoCD (simpler GitOps)
- GitHub Actions / GitLab CI (CI+CD)
- Flux

For new: rarely.
For existing: still major user.

## When Spinnaker

- Multi-cloud
- Canary critical
- Complex pipelines
- Already invested

## When Not

- Single cloud
- K8s-only
- Want GitOps
- Small team

## Real Users

- Netflix (origin)
- Salesforce
- Some financial / large enterprise

## Operational Cost

- Multiple services (Deck, Gate, Orca, ...)
- Memory heavy
- Maintenance burden

For: dedicated team.

## Alternatives

- ArgoCD (GitOps)
- Flux
- GitHub Actions / GitLab CI
- Tekton + Argo Rollouts

## Best Practices

- Pipeline templates for reuse
- Manual judgement on prod
- Canary for risky
- Notifications wired
- RBAC strict

## Common Mistakes

- Adopt for buzzword (don't need multi-cloud)
- No templates (each service different)
- Cluster-admin in Clouddriver
- Skip Spinnaker upgrades (operational debt)

## Quick Refs

```
UI: Deck (https://spinnaker.example.com)
CLI: spin (limited)
Halyard: install / config

Pipelines: UI or JSON
Templates: schema v2
```

## Interview Prep

**Mid**: "What's Spinnaker."

**Senior**: "When Spinnaker."

**Staff**: "Multi-cloud CD."

## Next Topic

→ [T02 — Multi-Cloud Deployments](T02-Multi-Cloud-Deploys.md)
