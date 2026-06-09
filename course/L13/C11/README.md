# L13/C11 — Helm

## Topics

- **T01 Charts, Templates, Values** — Chart = package. Templates use Go template with Sprig functions. values.yaml supplies defaults; --set / -f overrides.
- **T02 Helm Repos & OCI Registries** — Traditional repo (index.yaml) or OCI (push to ECR/GAR). `helm pull oci://...`.
- **T03 Helm 3 Architecture (No Tiller)** — Client-only. State stored as Secret in target namespace per release.
- **T04 Best Practices** — Use semantic versioning. Subcharts for reusable building blocks. helmfile/Helm releases for multi-chart deployments.

## Chart Structure

```
mychart/
├── Chart.yaml          # metadata, version
├── values.yaml         # defaults
├── values.schema.json  # JSON Schema for values
├── templates/
│   ├── _helpers.tpl    # named templates
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── NOTES.txt       # post-install messages
│   └── tests/
└── charts/             # subchart dependencies
```

## Common Helm Patterns

```yaml
{{- if .Values.ingress.enabled }}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "mychart.fullname" . }}
  labels:
    {{- include "mychart.labels" . | nindent 4 }}
spec:
  rules:
  {{- range .Values.ingress.hosts }}
  - host: {{ .host }}
    http:
      paths:
      {{- range .paths }}
      - path: {{ .path }}
        pathType: {{ .pathType | default "Prefix" }}
        backend:
          service:
            name: {{ include "mychart.fullname" $ }}
            port:
              number: {{ $.Values.service.port }}
      {{- end }}
  {{- end }}
{{- end }}
```

## Useful Commands

```bash
helm install myrelease ./mychart -n myns -f values.prod.yaml
helm upgrade --install myrelease ./mychart -n myns
helm rollback myrelease 1
helm history myrelease
helm template ./mychart > out.yaml   # render without install
helm lint ./mychart
helm test myrelease
```

## Helm vs Kustomize

| Helm | Kustomize |
|---|---|
| Templating | Patching |
| Conditional logic in templates | Pure YAML overlays |
| Packageable, distributable | Just files |
| Has releases/history | Stateless |
| Complex but powerful | Simple but explicit |

Use **both**: Helm for installing 3rd-party charts; Kustomize for your own services.

## Interview Themes

- "Compare Helm and Kustomize"
- "Why was Tiller removed in Helm 3?"
- "Walk me through a Helm chart you've authored"
