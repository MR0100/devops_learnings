# L13/C10/T03 — Operator SDK (Go, Ansible, Helm)

## Learning Objectives

- Use Operator SDK
- Pick language strategy

## Operator SDK

Red Hat's toolkit for building Operators:
- Go (full control)
- Ansible (existing playbooks)
- Helm (wraps Helm chart)

Plus scaffolding, testing, CI integration.

## Install

```bash
brew install operator-sdk
# or
curl -LO https://github.com/operator-framework/operator-sdk/releases/...
```

## Initialize Project

```bash
mkdir my-operator && cd my-operator
operator-sdk init --domain mycompany.io --repo github.com/me/my-operator --plugins=go/v4
```

Sets up scaffolding.

## Create API

```bash
operator-sdk create api \
  --group apps \
  --version v1 \
  --kind WebService \
  --resource --controller
```

Generates:
- `api/v1/webservice_types.go` (CR struct)
- `controllers/webservice_controller.go` (reconcile)
- `config/crd/bases/...yaml` (CRD)
- `config/rbac/...yaml`

## CR Type (Go)

```go
type WebServiceSpec struct {
    Image    string `json:"image"`
    Replicas int32  `json:"replicas"`
}

type WebServiceStatus struct {
    AvailableReplicas int32 `json:"availableReplicas"`
    Conditions        []metav1.Condition `json:"conditions"`
}

// +kubebuilder:object:root=true
// +kubebuilder:subresource:status
type WebService struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`
    Spec   WebServiceSpec   `json:"spec,omitempty"`
    Status WebServiceStatus `json:"status,omitempty"`
}
```

## Reconcile

```go
func (r *WebServiceReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    var ws appsv1.WebService
    if err := r.Get(ctx, req.NamespacedName, &ws); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }
    
    // Desired Deployment
    desired := &appsv1.Deployment{
        ObjectMeta: metav1.ObjectMeta{
            Name:      ws.Name,
            Namespace: ws.Namespace,
        },
        Spec: appsv1.DeploymentSpec{
            Replicas: &ws.Spec.Replicas,
            Selector: &metav1.LabelSelector{
                MatchLabels: map[string]string{"app": ws.Name},
            },
            Template: corev1.PodTemplateSpec{
                ObjectMeta: metav1.ObjectMeta{
                    Labels: map[string]string{"app": ws.Name},
                },
                Spec: corev1.PodSpec{
                    Containers: []corev1.Container{{
                        Name:  "app",
                        Image: ws.Spec.Image,
                    }},
                },
            },
        },
    }
    
    // Owner ref
    ctrl.SetControllerReference(&ws, desired, r.Scheme)
    
    // Create or Update
    var existing appsv1.Deployment
    err := r.Get(ctx, types.NamespacedName{Name: ws.Name, Namespace: ws.Namespace}, &existing)
    if errors.IsNotFound(err) {
        r.Create(ctx, desired)
    } else {
        existing.Spec = desired.Spec
        r.Update(ctx, &existing)
    }
    
    // Update status
    ws.Status.AvailableReplicas = existing.Status.AvailableReplicas
    r.Status().Update(ctx, &ws)
    
    return ctrl.Result{}, nil
}
```

## Setup

```go
func (r *WebServiceReconciler) SetupWithManager(mgr ctrl.Manager) error {
    return ctrl.NewControllerManagedBy(mgr).
        For(&appsv1.WebService{}).
        Owns(&appsv1.Deployment{}).
        Complete(r)
}
```

## Build + Deploy

```bash
# Generate manifests
make manifests

# Build image
make docker-build docker-push IMG=myregistry.io/my-operator:v1

# Install CRDs
make install

# Deploy operator
make deploy IMG=myregistry.io/my-operator:v1
```

## Ansible Operator

For: Ansible users; no Go expertise.

```bash
operator-sdk init --plugins=ansible --domain mycompany.io
operator-sdk create api --group apps --version v1 --kind WebService --generate-role
```

Generates Ansible role. Edit:
```yaml
# roles/webservice/tasks/main.yml
- name: Create Deployment
  k8s:
    definition:
      apiVersion: apps/v1
      kind: Deployment
      metadata:
        name: "{{ ansible_operator_meta.name }}"
      spec:
        replicas: "{{ replicas }}"
        ...
```

Operator runs role on each Reconcile.

## Helm Operator

For: existing Helm charts.

```bash
operator-sdk init --plugins=helm --domain mycompany.io
operator-sdk create api --group apps --version v1 --kind WebService --helm-chart=./mychart
```

CR spec maps to Helm values. Operator renders + applies.

```yaml
apiVersion: apps.mycompany.io/v1
kind: WebService
metadata:
  name: my-app
spec:
  image: nginx
  replicas: 3
  # → Helm values
```

## When Each

| | Go | Ansible | Helm |
|---|---|---|---|
| Logic | Full | Tasks | Templates |
| State | Manual | Inferred | Helm-managed |
| Learning | Steep | Medium | Easy |
| Complex | Best | OK | Limited |
| Existing chart | n/a | n/a | Wrap |

For: production complex (DBs): Go.
For: existing scripts: Ansible.
For: existing chart: Helm.

## kubebuilder vs Operator SDK

Operator SDK builds on kubebuilder; adds tooling.

For pure controllers: kubebuilder.
For OperatorHub publishing: Operator SDK.

Both Go.

## Bundle Format (OLM)

For OperatorHub:
```bash
make bundle
```

Generates bundle manifests:
- CRDs
- Deployment
- ClusterServiceVersion (CSV)

Published to OperatorHub.

## OLM (Operator Lifecycle Manager)

K8s service for installing/managing operators:
- Subscriptions
- Approval policies
- Updates
- Channels (stable, alpha, beta)

```bash
operator-sdk olm install
```

For: managed operator lifecycle.

## Testing

```bash
make test
```

Uses envtest for integration.

```go
func TestReconcile(t *testing.T) {
    testEnv := &envtest.Environment{...}
    cfg, _ := testEnv.Start()
    
    // Create test client
    cl, _ := client.New(cfg, client.Options{})
    
    // Apply CR
    cl.Create(ctx, &WebService{...})
    
    // Trigger reconcile
    reconciler := &WebServiceReconciler{Client: cl}
    reconciler.Reconcile(ctx, ctrl.Request{...})
    
    // Verify Deployment created
    var dep appsv1.Deployment
    cl.Get(ctx, ..., &dep)
    assert.Equal(t, int32(3), *dep.Spec.Replicas)
}
```

## E2E Test

```bash
make test-e2e
```

Runs against real cluster.

## Versioning

CRs can have multiple versions:
```bash
operator-sdk create api --version v2
```

Generates conversion webhook stub.

## CI/CD

```yaml
# GitHub Actions
- run: make manifests
- run: make build
- run: make test
- uses: docker/build-push-action@v3
  with:
    tags: myregistry/my-operator:${{ github.sha }}
```

Per push: build + push image.

## Observability

Operator emits metrics:
- controller_runtime_reconcile_total
- controller_runtime_reconcile_errors_total
- workqueue_depth

Service for Prometheus:
```yaml
spec:
  ports:
  - name: metrics
    port: 8080
```

## Logging

```go
import "sigs.k8s.io/controller-runtime/pkg/log"

log := log.FromContext(ctx)
log.Info("reconciling", "name", req.Name)
log.Error(err, "failed")
```

Structured logs (logr).

## Distribution

Options:
- OperatorHub (community + commercial)
- Helm chart in repo
- Raw YAML
- OLM via Subscription

For internal: Helm or YAML.
For community: OperatorHub.

## Common Mistakes

- Reinventing K8s primitives
- Operator does too much
- No status updates
- No leader election
- Hardcoded values

## Best Practices

- Single responsibility CR
- Standard Conditions
- Leader election
- Metrics
- E2E tests
- Bundle for OperatorHub if public
- Document API thoroughly

## Real Examples

CloudNativePG, Strimzi (Kafka), Prometheus Operator, cert-manager — all Operator SDK or kubebuilder.

## Quick Refs

```bash
# Init
operator-sdk init --domain mycompany.io --repo github.com/me/op

# API
operator-sdk create api --group apps --version v1 --kind WebService

# Build
make docker-build docker-push IMG=...

# Deploy
make install   # CRDs
make deploy IMG=...

# Bundle (OperatorHub)
make bundle bundle-build bundle-push
```

## Interview Prep

**Mid**: "Operator SDK purpose."

**Senior**: "Go vs Helm operator."

**Staff**: "Publish operator to OperatorHub."

## Next Topic

→ [T04 — kubebuilder](T04-Kubebuilder.md)
