# L13/C11/T04 — Helm Best Practices

## Learning Objectives

- Apply Helm best practices
- Avoid common pitfalls

## Naming

### Chart Name
Lowercase, hyphens:
- ✓ `my-app`
- ✗ `MyApp`, `my_app`

### Resource Names
Use template helpers:
```yaml
metadata:
  name: {{ include "mychart.fullname" . }}
```

`fullname` includes release name → unique per release.

## Labels

Standard K8s labels:
```yaml
labels:
  app.kubernetes.io/name: {{ include "mychart.name" . }}
  app.kubernetes.io/instance: {{ .Release.Name }}
  app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
  app.kubernetes.io/managed-by: {{ .Release.Service }}
  helm.sh/chart: {{ include "mychart.chart" . }}
```

For: filtering, ownership, discovery.

## Required Files

Always have:
- README.md
- Chart.yaml with description + maintainers
- values.yaml with comments
- values.schema.json for validation
- NOTES.txt for post-install
- templates/_helpers.tpl

## Templates

### Use Helpers
```yaml
metadata:
  name: {{ include "mychart.fullname" . }}
  labels:
    {{- include "mychart.labels" . | nindent 4 }}
```

vs duplicating logic.

### Default Values
```yaml
{{ .Values.image.tag | default .Chart.AppVersion }}
```

Sensible defaults.

### Conditional Inclusion
```yaml
{{- if .Values.ingress.enabled }}
apiVersion: networking.k8s.io/v1
kind: Ingress
...
{{- end }}
```

For optional features.

## Values Structure

Group logically:
```yaml
image:
  repository: nginx
  tag: 1.27
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: false
  className: nginx

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 256Mi

nodeSelector: {}
tolerations: []
affinity: {}
```

Flat: hard to use. Grouped: clear.

## Schema Validation

values.schema.json:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["image"],
  "properties": {
    "replicaCount": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100
    },
    "image": {
      "type": "object",
      "required": ["repository"],
      "properties": {
        "repository": {"type": "string"},
        "tag": {"type": "string"}
      }
    }
  }
}
```

Catches bad values at install.

## Idempotency

Helm should produce same output for same inputs:
- Avoid `randAlphaNum` (each install differs)
- Or use deterministic seeds

For initial passwords: use Secret with `helm.sh/hook: pre-install` + check for existence.

## Subcharts vs Dependencies

Subcharts:
- In charts/ directory
- Versioned
- Updated via helm dependency update

For: reuse common building blocks (DB, cache).

## Aliasing

Same chart used twice:
```yaml
dependencies:
- name: redis
  alias: cache
- name: redis
  alias: queue
```

Two Redis instances.

## Conditions

Subchart only if enabled:
```yaml
dependencies:
- name: postgresql
  version: 12.x.x
  condition: postgresql.enabled
```

Values:
```yaml
postgresql:
  enabled: true
  ...
```

## Tags

Group subcharts:
```yaml
dependencies:
- name: postgresql
  tags: [db]
- name: redis
  tags: [cache]
```

```yaml
tags:
  db: true
  cache: false
```

For: enable groups together.

## Values Override Strategy

For multi-env:
```
values.yaml          # defaults
values-dev.yaml      # dev overrides
values-staging.yaml  # staging
values-prod.yaml     # prod
```

```bash
helm install -f values-prod.yaml my-release ./mychart
```

## CI Integration

```yaml
- run: helm lint ./mychart
- run: helm template ./mychart --validate
- run: helm install --dry-run my-release ./mychart -f values-prod.yaml
```

For PR: validate.

## Atomic Install

```bash
helm install my-release ./mychart --atomic --timeout 5m
```

Rollback on failure. For CI/CD.

## Diff Before Apply

```bash
helm diff upgrade my-release ./mychart
```

Plugin shows what changes. Review before apply.

## Resource Requests + Limits

Always:
```yaml
resources:
  requests:
    cpu: {{ .Values.resources.requests.cpu }}
    memory: {{ .Values.resources.requests.memory }}
  limits:
    cpu: {{ .Values.resources.limits.cpu }}
    memory: {{ .Values.resources.limits.memory }}
```

For: predictable scheduling.

## Probes

```yaml
{{- if .Values.livenessProbe }}
livenessProbe:
  {{- toYaml .Values.livenessProbe | nindent 12 }}
{{- end }}

{{- if .Values.readinessProbe }}
readinessProbe:
  {{- toYaml .Values.readinessProbe | nindent 12 }}
{{- end }}
```

For: configurable health.

## Pod Disruption Budget

```yaml
{{- if .Values.pdb.enabled }}
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: {{ include "mychart.fullname" . }}
spec:
  minAvailable: {{ .Values.pdb.minAvailable }}
  selector:
    matchLabels:
      {{- include "mychart.selectorLabels" . | nindent 6 }}
{{- end }}
```

For prod HA.

## NetworkPolicy

```yaml
{{- if .Values.networkPolicy.enabled }}
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
spec:
  ...
{{- end }}
```

For security.

## ServiceAccount

```yaml
{{- if .Values.serviceAccount.create }}
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {{ include "mychart.serviceAccountName" . }}
  {{- with .Values.serviceAccount.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
{{- end }}
```

For IRSA / Workload Identity annotations.

## ConfigMap Checksum

Trigger pod restart on ConfigMap change:
```yaml
spec:
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
```

Hash changes → annotation changes → pod template changes → rollout.

## Secret Rotation

Same pattern with Secret:
```yaml
checksum/secret: {{ include (print $.Template.BasePath "/secret.yaml") . | sha256sum }}
```

## Pre-Existing Resources

Avoid creating Secret if exists:
```yaml
{{- if not (lookup "v1" "Secret" .Release.Namespace "my-secret") }}
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
data:
  password: {{ randAlphaNum 16 | b64enc | quote }}
{{- end }}
```

For: initial password not overwritten on upgrade.

## Multiple Environments

Use values files; don't fork charts:
```
mychart/
├── Chart.yaml
├── values.yaml
└── ...

deploy/
├── values-dev.yaml
├── values-staging.yaml
└── values-prod.yaml
```

Same chart; different values per env.

## Versioning

Semver:
- Patch (1.0.x): bug fix
- Minor (1.x.0): backward-compat additions
- Major (x.0.0): breaking

Bump chart version on any change.

## Chart Testing

ct (chart testing):
```bash
ct lint
ct install
```

In CI for PRs.

## helmfile for Multi-Release

```yaml
# helmfile.yaml
releases:
- name: redis
  chart: bitnami/redis
- name: my-app
  chart: ./charts/my-app
  needs: [redis]
```

Order + dependencies.

```bash
helmfile apply
```

## Common Mistakes

- Hardcoded values
- No NOTES.txt
- Missing schema
- No defaults
- Subcharts not aliased
- No checksum annotations (changes not rolled out)
- Forgot helm-diff

## Anti-Patterns

- Forking community charts (use values overrides)
- Big monolithic chart (split if independent)
- Manual edit values via Helm (use --set / -f)
- Skip lint
- No version bump per change

## Best Practices Summary

1. Use helpers
2. Schema validation
3. Sensible defaults
4. Per-env values files
5. ConfigMap/Secret checksum
6. PDB + NetworkPolicy + ServiceAccount support
7. --atomic in CI
8. helm-diff before apply
9. helmfile for many releases
10. CI lint + dry-run
11. Semver
12. README + NOTES

## Testing Charts

```yaml
# templates/tests/test.yaml
apiVersion: v1
kind: Pod
metadata:
  annotations:
    "helm.sh/hook": test
spec:
  containers:
  - name: wget
    image: busybox
    command: [wget]
    args: ['{{ include "mychart.fullname" . }}:{{ .Values.service.port }}']
  restartPolicy: Never
```

```bash
helm test my-release
```

## Documentation

README per chart:
- What it does
- Values reference
- Examples
- Common patterns

For consumers.

## Quick Refs

```bash
helm lint
helm template
helm install --dry-run
helm diff upgrade
helm test RELEASE
helmfile apply
```

## Interview Prep

**Mid**: "Helm best practices."

**Senior**: "Chart for 5-microservice app."

**Staff**: "Chart strategy for 100-service platform."

## Next Topic

→ Move to [L13/C12 — Multi-Cluster](../C12/README.md)
