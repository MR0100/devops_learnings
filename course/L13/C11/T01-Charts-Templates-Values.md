# L13/C11/T01 — Charts, Templates, Values

## Learning Objectives

- Build Helm charts
- Use templates effectively

## Helm

Package manager for Kubernetes. Charts = packages.

```bash
helm install my-release ./mychart
helm upgrade my-release ./mychart
helm uninstall my-release
helm list
```

## Chart Structure

```
mychart/
├── Chart.yaml              # metadata
├── values.yaml             # defaults
├── values.schema.json      # JSON Schema
├── templates/
│   ├── _helpers.tpl        # named templates
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── ingress.yaml
│   ├── NOTES.txt           # install messages
│   └── tests/
│       └── test-connection.yaml
├── charts/                 # subcharts
└── README.md
```

## Chart.yaml

```yaml
apiVersion: v2
name: mychart
description: A web app
type: application
version: 0.1.0          # chart version
appVersion: "1.16.0"    # app version
keywords:
  - web
maintainers:
  - name: Alice
    email: alice@example.com
dependencies:
- name: redis
  version: 17.x.x
  repository: https://charts.bitnami.com/bitnami
  condition: redis.enabled
```

## values.yaml

```yaml
replicaCount: 1

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
  hosts:
  - host: example.com
    paths:
    - path: /
      pathType: Prefix

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 256Mi

redis:
  enabled: false
  master:
    persistence:
      size: 8Gi
```

Defaults; overridden via --set or -f.

## Templates

Go templates with Sprig functions:
```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "mychart.fullname" . }}
  labels:
    {{- include "mychart.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "mychart.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "mychart.selectorLabels" . | nindent 8 }}
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - name: http
          containerPort: {{ .Values.service.port }}
        resources:
          {{- toYaml .Values.resources | nindent 10 }}
```

## Built-in Objects

- `.Values`: from values.yaml + overrides
- `.Chart`: Chart.yaml fields
- `.Release`: Name, Namespace, Service, etc.
- `.Capabilities`: cluster info (Kubernetes version)
- `.Files`: access non-template files

## Functions

```yaml
{{ .Values.image.tag | default .Chart.AppVersion }}
{{ .Release.Name | quote }}
{{ .Values.tags | toYaml | nindent 4 }}
{{ now | date "2006-01-02" }}
{{ randAlphaNum 16 }}
{{ b64enc .Values.password }}
{{ include "mychart.fullname" . | trunc 63 | trimSuffix "-" }}
```

Sprig provides many: string, list, math, encoding, etc.

## Conditionals

```yaml
{{- if .Values.ingress.enabled }}
apiVersion: networking.k8s.io/v1
kind: Ingress
...
{{- end }}

{{- if .Values.serviceAccount.create }}
apiVersion: v1
kind: ServiceAccount
...
{{- end }}
```

## Loops

```yaml
{{- range .Values.ingress.hosts }}
- host: {{ .host | quote }}
  http:
    paths:
    {{- range .paths }}
    - path: {{ .path }}
      pathType: {{ .pathType }}
    {{- end }}
{{- end }}
```

## Named Templates

```yaml
# templates/_helpers.tpl
{{- define "mychart.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "mychart.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "mychart.name" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "mychart.labels" -}}
helm.sh/chart: {{ include "mychart.chart" . }}
{{ include "mychart.selectorLabels" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
```

Used via `include`:
```yaml
labels:
  {{- include "mychart.labels" . | nindent 4 }}
```

## Whitespace

`{{-`: trim leading whitespace.
`-}}`: trim trailing.

For clean YAML output:
```yaml
{{- range .Values.list }}
- {{ . }}
{{- end }}
```

vs (extra blank lines):
```yaml
{{ range .Values.list }}
- {{ . }}
{{ end }}
```

## Indentation

`nindent N`: newline + N spaces.
`indent N`: N spaces (no newline).

For mid-line:
```yaml
spec:
  selector:
    matchLabels: {{- include "labels" . | nindent 6 }}
```

## Install

```bash
helm install my-release ./mychart
helm install my-release ./mychart --values prod.yaml --set replicas=5
helm install my-release ./mychart -n my-namespace --create-namespace
```

## Override Order

1. values.yaml (chart default)
2. `--values file.yaml` (file override)
3. `--set key=val` (CLI override)

Later wins.

## Multiple Values Files

```bash
helm install my-release ./mychart \
  -f common.yaml \
  -f prod.yaml \
  --set image.tag=v1.2.3
```

Per environment.

## Dry Run

```bash
helm install my-release ./mychart --dry-run --debug
```

Renders templates without applying. For testing.

## Template

```bash
helm template my-release ./mychart > generated.yaml
```

Render to YAML. Apply manually if needed.

## Upgrade

```bash
helm upgrade my-release ./mychart --set replicas=5
```

Reapplies; updates resources.

## Rollback

```bash
helm history my-release
helm rollback my-release 2
```

Restore previous version.

## Lint

```bash
helm lint ./mychart
```

Checks syntax + best practices.

## Schema Validation

values.schema.json:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["replicaCount"],
  "properties": {
    "replicaCount": {
      "type": "integer",
      "minimum": 1
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

Validation on install/upgrade. Catches bad values.

## NOTES.txt

Shown after install:
```
{{- if .Values.ingress.enabled }}
1. Get the application URL by running:
  https://{{ (index .Values.ingress.hosts 0).host }}
{{- end }}
```

## Tests

```yaml
# templates/tests/test-connection.yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "mychart.fullname" . }}-test"
  annotations:
    "helm.sh/hook": test
spec:
  containers:
  - name: wget
    image: busybox
    command: ['wget']
    args: ['{{ include "mychart.fullname" . }}:{{ .Values.service.port }}']
  restartPolicy: Never
```

```bash
helm test my-release
```

## Hooks

Hooks for lifecycle:
```yaml
annotations:
  "helm.sh/hook": pre-install
  "helm.sh/hook-weight": "5"
  "helm.sh/hook-delete-policy": before-hook-creation
```

Phases:
- pre-install
- post-install
- pre-upgrade
- post-upgrade
- pre-delete
- post-delete
- pre-rollback
- post-rollback

For: migrations, custom setup.

## Dependencies

```bash
helm dependency update
```

Fetches subcharts to charts/.

## Values Generation

```bash
# Get current
helm get values my-release

# All including computed
helm get values my-release --all
```

## Common Mistakes

- Hardcoded values (no template)
- No NOTES.txt
- No schema validation
- Helper templates missing
- Forgot helm lint

## Best Practices

- _helpers.tpl for repeated names
- Schema validation
- NOTES.txt
- Tests
- Version semver
- Per-env values files
- Lint in CI

## Quick Refs

```bash
helm create mychart       # scaffold
helm install r ./mychart
helm upgrade r ./mychart
helm uninstall r
helm list
helm history r
helm rollback r 1
helm template r ./mychart
helm lint ./mychart
helm test r
```

## Interview Prep

**Junior**: "What's Helm."

**Mid**: "Templates and values."

**Senior**: "Chart for stateful workload."

**Staff**: "Chart strategy for 50-service platform."

## Next Topic

→ [T02 — Helm Repos & OCI Registries](T02-Repos-OCI.md)
