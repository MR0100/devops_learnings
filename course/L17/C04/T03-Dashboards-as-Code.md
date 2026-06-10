# L17/C04/T03 — Provisioning Dashboards as Code

## Learning Objectives

- Version dashboards in Git
- Auto-load via provisioning

## Why

- Versioned (Git history)
- Reviewable (PR)
- Reusable (templates)
- Recoverable (re-create)

## Provisioning Config

```yaml
# /etc/grafana/provisioning/dashboards/default.yml
apiVersion: 1
providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 30
    options:
      path: /var/lib/grafana/dashboards
```

Grafana watches path; auto-loads JSON.

## Dashboard JSON

Export from UI:
```
Settings → JSON Model → Copy / Save
```

Or:
```bash
curl http://grafana/api/dashboards/uid/UID
```

## Commit

```bash
git add dashboards/api.json
git commit -m "Update API dashboard"
git push
```

CI deploys to Grafana path.

## ConfigMap (K8s)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: dashboards
  labels:
    grafana_dashboard: "1"
data:
  api.json: |
    { ... full dashboard JSON ... }
```

Sidecar:
- watches ConfigMaps with label
- copies to Grafana

For: K8s-native.

## helm chart

```yaml
# values.yaml
dashboards:
  default:
    api:
      json: |
        {...}
```

Helm injects.

## Grafonnet (Jsonnet)

DSL for dashboards:
```jsonnet
local grafana = import 'grafonnet/grafana.libsonnet';
local dashboard = grafana.dashboard;

dashboard.new('API')
.addPanel(
  graph.new('Requests')
  .addTarget(prometheus.target('rate(http_requests_total[5m])'))
)
```

For: DRY.

## Mixins

Pre-built dashboards + alerts:
```bash
git clone https://github.com/prometheus-operator/kube-prometheus
```

Mixins for: kubernetes, etcd, nginx, etc.

## Grizzly

Kubectl-like for Grafana:
```bash
grr apply -f dashboards/
```

Manages dashboards, datasources, alerts.

## ManagedDashboards

CRD (Operator):
```yaml
apiVersion: grafana.integreatly.org/v1beta1
kind: GrafanaDashboard
metadata:
  name: api
spec:
  json: ...
```

K8s-native.

## CI Update Flow

```yaml
# .github/workflows/grafana.yml
- name: Apply dashboards
  run: |
    for f in dashboards/*.json; do
      curl -X POST http://grafana/api/dashboards/db \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "@$f"
    done
```

Or use Grafana provider for Terraform:
```hcl
resource "grafana_dashboard" "api" {
  config_json = file("dashboards/api.json")
}
```

## Workflow

```
Dev edits dashboard in UI (sandbox)
→ Export JSON
→ Commit
→ PR
→ Merge
→ CI deploys to prod Grafana
```

For: no manual prod edits.

## Locked Prod

Disable edits in prod Grafana:
```ini
[users]
viewers_can_edit = false
```

Force changes via Git.

## Mixins Workflow

```bash
# kube-prometheus has rules + dashboards
make manifests/grafana-dashboard-*.json
kubectl apply -f manifests/
```

## Template Override

```jsonnet
local myDashboard = (import 'mixins/k8s.libsonnet') + {
  // customize
  panels: ...
};
```

## Drift Detection

Compare deployed vs Git:
```bash
diff <(curl /api/dashboards/uid/X | jq -S) <(cat dashboards/x.json | jq -S)
```

For: catch UI changes.

## Best Practices

- All dashboards in Git
- Provisioning ConfigMap (K8s)
- Sidecar pattern
- Disable UI edits in prod
- Sandbox env for dev
- Mixins for stack basics

## Common Mistakes

- UI-only edits (lost on restart)
- No version control
- No tests (broken dashboard ships)
- Hard to apply uniformly

## Test Dashboards

```bash
# grafana-tools (lint)
dashboard-cli lint dashboards/

# Run with mock data
```

## Folder Structure

```
dashboards/
  service/
    api.json
    db.json
  infra/
    k8s.json
    nodes.json
  business/
    revenue.json
```

Maps to Grafana folders.

## Quick Refs

```yaml
# Provisioning
providers:
  - name: default
    type: file
    options:
      path: /var/lib/grafana/dashboards

# K8s ConfigMap
labels:
  grafana_dashboard: "1"
```

```bash
# Apply via API
curl -X POST http://grafana/api/dashboards/db -d "@dashboard.json"

# Grizzly
grr apply -f dashboards/

# Terraform
resource "grafana_dashboard"
```

## Interview Prep

**Mid**: "Dashboards as code."

**Senior**: "Provisioning."

**Staff**: "Observability code."

## Next Topic

→ [T04 — Grafana Loki, Tempo, Mimir](T04-Grafana-Stack.md)
