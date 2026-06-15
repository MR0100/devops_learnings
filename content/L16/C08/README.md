# L16/C08 — Spinnaker

## Topics

- **T01 Pipelines, Pipeline Templates** — Spinnaker's pipeline model.
- **T02 Multi-Cloud Deployments** — Cross-cloud, cross-region orchestration.

## What Spinnaker Is

Multi-cloud continuous delivery platform from Netflix (open-sourced 2015). Battle-tested at scale.

### Core Concepts
- **Application**: top-level org unit
- **Pipeline**: ordered stages
- **Stage**: a step (deploy, manual judgment, run job, etc.)
- **Trigger**: pipeline start (CI, Docker, manual, schedule)
- **Cluster**: a group of similar instances/pods
- **Server group**: ASG / Deployment

### Stages
- Bake (Packer)
- Deploy (rolling, BG, canary)
- Manual Judgment
- Run Job (Kubernetes Job, Lambda, etc.)
- Wait
- Find Image From Tags / Cluster
- Disable / Enable / Destroy Cluster
- Pipeline (call another)

## Pipeline as Code

JSON-based; can be stored in Git via Dinghy plugin.

```json
{
  "name": "deploy-prod",
  "triggers": [{"type": "docker", "tag": "v.*"}],
  "stages": [
    {"type": "deploy", "name": "Deploy", "clusters": [...]},
    {"type": "manualJudgment", "name": "Confirm", "judgmentInputs": [{"value": "rollback"}]},
    {"type": "destroyServerGroup", "name": "Cleanup old"}
  ]
}
```

## Strengths

- **Multi-cloud first-class** (AWS + GCP + K8s + Azure in one pipeline)
- **Battle-tested at Netflix-scale**
- **Sophisticated deploy strategies** (red/black, canary with analysis)
- **Rich UI**

## Weaknesses

- **Heavyweight** to operate (microservice architecture with many components: Clouddriver, Orca, Deck, Gate, Echo, Fiat, Igor, etc.)
- **Complex to set up**
- **Java-based** (significant memory)
- **Steep learning curve**
- **Adoption declining** in favor of simpler GitOps tools

## When Spinnaker

- Truly multi-cloud, multi-region, complex deploys
- Netflix-scale ops team
- Heritage Spinnaker investment

## When NOT Spinnaker

- Smaller teams (overkill)
- K8s-only — Argo/Flux easier
- Modern preference for declarative GitOps

## Interview Themes

- "Spinnaker — why use it?"
- "Multi-cloud deploy pipeline"
- "Red/black vs canary"
- "When NOT Spinnaker"
