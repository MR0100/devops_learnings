# L30/C04/T02 — Golden Path Templates

## Learning Objectives

- Build templates
- Self-service

## Template

```yaml
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: webapp-template
  title: Create New Web Service
spec:
  parameters:
    - title: Service Info
      properties:
        name:
          type: string
          title: Service Name
        team:
          type: string
          title: Owner Team
  steps:
    - id: fetch
      action: fetch:template
      input:
        url: ./skeleton
        values:
          name: ${{ parameters.name }}
          team: ${{ parameters.team }}
    - id: publish
      action: publish:github
      input:
        repoUrl: github.com?owner=org&repo=${{ parameters.name }}
    - id: register
      action: catalog:register
      input:
        repoContentsUrl: ${{ steps.publish.output.repoContentsUrl }}
```

## Skeleton

```
skeleton/
  catalog-info.yaml
  README.md
  src/
    main.go
  .github/
    workflows/
      ci.yml
  Dockerfile
  deploy/
    chart/
      ...
```

## Values

```yaml
# In catalog-info.yaml
metadata:
  name: ${{ values.name }}
spec:
  owner: ${{ values.team }}
```

Replaced when scaffolded.

## Multiple Templates

```
templates/
  webapp/
  worker/
  cli/
  library/
```

Per use case.

## Use

Backstage UI:
1. Pick template
2. Fill params
3. Create
4. Auto: repo + register

## Update

Template owners:
- Update skeleton
- Existing services don't auto-update
- Or sync via tooling

## Best Practices

- Cover top use cases
- Include CI/CD
- Include observability
- Include IaC
- Document

## Common Mistakes

- Too rigid
- Stale skeleton
- No CI/CD
- No observability

## Quick Refs

```yaml
kind: Template
spec:
  parameters: ...
  steps:
    - fetch:template
    - publish:github
    - catalog:register
```

## Next Topic

→ [T03 — Self-Service Provisioning](T03-Self-Service.md)
