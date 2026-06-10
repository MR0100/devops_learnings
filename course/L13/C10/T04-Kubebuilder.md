# L13/C10/T04 — kubebuilder

## Learning Objectives

- Use kubebuilder
- Distinguish from Operator SDK

## kubebuilder

K8s SIG tool for building Operators in Go.

Lower-level than Operator SDK (which adds OperatorHub features).

Both build on controller-runtime.

## Install

```bash
brew install kubebuilder
# or
curl -L -o kubebuilder https://go.kubebuilder.io/dl/latest/$(go env GOOS)/$(go env GOARCH)
chmod +x kubebuilder && sudo mv kubebuilder /usr/local/bin/
```

## Initialize

```bash
mkdir my-op && cd my-op
go mod init github.com/me/my-op
kubebuilder init --domain mycompany.io
```

Generates:
- main.go (entry point)
- Makefile
- config/ (manifests)
- go.mod with deps

## Create API

```bash
kubebuilder create api --group apps --version v1 --kind WebService
```

Prompts:
- Create Resource? (yes)
- Create Controller? (yes)

Generates:
- api/v1/webservice_types.go
- api/v1/groupversion_info.go
- internal/controller/webservice_controller.go
- Updated config/crd/bases/...

## Types File

```go
// api/v1/webservice_types.go

type WebServiceSpec struct {
    // +kubebuilder:validation:Required
    Image string `json:"image"`
    
    // +kubebuilder:validation:Minimum=1
    // +kubebuilder:validation:Maximum=100
    // +kubebuilder:default=1
    Replicas int32 `json:"replicas,omitempty"`
}

type WebServiceStatus struct {
    AvailableReplicas int32 `json:"availableReplicas,omitempty"`
    Conditions []metav1.Condition `json:"conditions,omitempty"`
}

// +kubebuilder:object:root=true
// +kubebuilder:subresource:status
// +kubebuilder:subresource:scale:specpath=.spec.replicas,statuspath=.status.availableReplicas
// +kubebuilder:printcolumn:name="Image",type=string,JSONPath=`.spec.image`
// +kubebuilder:printcolumn:name="Replicas",type=integer,JSONPath=`.spec.replicas`
type WebService struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`
    Spec   WebServiceSpec   `json:"spec,omitempty"`
    Status WebServiceStatus `json:"status,omitempty"`
}
```

## kubebuilder Markers

Comments starting `+kubebuilder:` are markers; generate CRD YAML.

Common:
- `+kubebuilder:validation:Required`
- `+kubebuilder:validation:Minimum=N`
- `+kubebuilder:default=X`
- `+kubebuilder:validation:Enum=a;b;c`
- `+kubebuilder:object:root=true`
- `+kubebuilder:subresource:status`
- `+kubebuilder:subresource:scale:...`
- `+kubebuilder:printcolumn:...`
- `+kubebuilder:resource:scope=Cluster`

Run `make manifests` → updates CRD YAML.

## Controller

```go
type WebServiceReconciler struct {
    client.Client
    Scheme *runtime.Scheme
}

// +kubebuilder:rbac:groups=apps.mycompany.io,resources=webservices,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=apps.mycompany.io,resources=webservices/status,verbs=get;update;patch
// +kubebuilder:rbac:groups=apps.mycompany.io,resources=webservices/finalizers,verbs=update
// +kubebuilder:rbac:groups=apps,resources=deployments,verbs=get;list;watch;create;update;patch;delete

func (r *WebServiceReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    log := log.FromContext(ctx)
    
    var ws appsv1.WebService
    if err := r.Get(ctx, req.NamespacedName, &ws); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }
    
    // Build desired Deployment
    deployment := &appsv1.Deployment{
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
    
    // Set owner reference
    if err := ctrl.SetControllerReference(&ws, deployment, r.Scheme); err != nil {
        return ctrl.Result{}, err
    }
    
    // Create or Update
    op, err := ctrl.CreateOrUpdate(ctx, r.Client, deployment, func() error {
        deployment.Spec.Replicas = &ws.Spec.Replicas
        deployment.Spec.Template.Spec.Containers[0].Image = ws.Spec.Image
        return nil
    })
    if err != nil {
        return ctrl.Result{}, err
    }
    log.Info("Deployment", "operation", op)
    
    // Update status
    ws.Status.AvailableReplicas = deployment.Status.AvailableReplicas
    if err := r.Status().Update(ctx, &ws); err != nil {
        return ctrl.Result{}, err
    }
    
    return ctrl.Result{}, nil
}

func (r *WebServiceReconciler) SetupWithManager(mgr ctrl.Manager) error {
    return ctrl.NewControllerManagedBy(mgr).
        For(&appsv1.WebService{}).
        Owns(&appsv1.Deployment{}).
        Complete(r)
}
```

## Build

```bash
make manifests   # regenerate CRD YAML, RBAC from markers
make generate    # update DeepCopy
make build       # build binary
make docker-build IMG=myregistry/op:v1
make docker-push IMG=myregistry/op:v1
```

## Run Locally

```bash
make run
```

Runs against current kubeconfig cluster. Fast iteration.

## Deploy

```bash
make install   # install CRDs
make deploy IMG=myregistry/op:v1
```

Deploys to cluster.

## Uninstall

```bash
make undeploy
make uninstall
```

## Webhook Setup

```bash
kubebuilder create webhook --group apps --version v1 --kind WebService --defaulting --programmatic-validation
```

Generates webhook stubs. Implement:

```go
func (r *WebService) Default() {
    if r.Spec.Replicas == 0 {
        r.Spec.Replicas = 1
    }
}

func (r *WebService) ValidateCreate() (admission.Warnings, error) {
    if r.Spec.Image == "" {
        return nil, errors.New("image required")
    }
    return nil, nil
}
```

## Multiple APIs

```bash
kubebuilder create api --group apps --version v1 --kind Database
```

Add more APIs to same operator. Multi-API operators common.

## API Versioning

```bash
kubebuilder create api --group apps --version v2 --kind WebService
```

Multi-version CR with conversion webhook (generated stub).

## Project Layout

```
my-op/
├── main.go                  # entry point
├── api/v1/                  # CR types
├── internal/controller/     # controllers
├── config/                  # K8s manifests
│   ├── crd/                 # CRD YAMLs
│   ├── rbac/                # RBAC
│   ├── manager/             # operator Deployment
│   ├── default/             # composed install
│   └── samples/             # example CRs
├── Dockerfile
├── Makefile
└── go.mod
```

## Makefile Targets

- make manifests: regenerate CRD + RBAC
- make generate: update DeepCopy
- make fmt vet: format + vet
- make test: unit tests
- make build: binary
- make docker-build: image
- make install: install CRDs
- make deploy: deploy operator
- make undeploy: remove

## envtest

Built-in for testing:
```go
import "sigs.k8s.io/controller-runtime/pkg/envtest"

testEnv := &envtest.Environment{
    CRDDirectoryPaths: []string{"config/crd/bases"},
}
cfg, _ := testEnv.Start()
defer testEnv.Stop()
```

In-memory API Server + etcd. Run tests fast.

## Ginkgo + Gomega

kubebuilder uses BDD style:
```go
var _ = Describe("WebService", func() {
    Context("when created", func() {
        It("creates a Deployment", func() {
            ws := &appsv1.WebService{...}
            Expect(k8sClient.Create(ctx, ws)).Should(Succeed())
            
            // Wait + check
            Eventually(func() bool {
                var dep appsv1.Deployment
                err := k8sClient.Get(ctx, ..., &dep)
                return err == nil
            }, timeout, interval).Should(BeTrue())
        })
    })
})
```

For integration tests.

## kubebuilder vs Operator SDK

| | kubebuilder | Operator SDK |
|---|---|---|
| Languages | Go | Go, Ansible, Helm |
| OperatorHub | Manual | Native |
| OLM bundling | Manual | Native |
| Maturity | Stable | Stable |
| Use | Pure Go ops | Polyglot, OperatorHub |

For Go-only: kubebuilder simpler.
For OperatorHub: Operator SDK.

## Controller-Runtime

The library both use:
- Manager (lifecycle, leader election)
- Client (read/write resources)
- Cache (informer)
- Builder (declarative setup)

Knowing controller-runtime = knowing both.

## Tilt for Dev Iteration

```bash
tilt up
```

Live-reload operator on code change. Fast feedback.

## Common Mistakes

- Forgot `make manifests` after marker changes
- Status update fails (resource version conflict; reread)
- Owner reference missing (no garbage collection)
- No RBAC (operator can't act)

## Best Practices

- Markers for everything
- Use CreateOrUpdate or server-side apply
- Status conditions
- Leader election
- Metrics
- E2E tests
- Operator runs in own namespace

## Real Operators Using kubebuilder

- cert-manager
- CloudNativePG
- Prometheus Operator
- Crossplane
- Knative

## Quick Refs

```bash
# Init
kubebuilder init --domain mycompany.io

# API
kubebuilder create api --group g --version v1 --kind X

# Webhook
kubebuilder create webhook --group g --version v1 --kind X --defaulting

# Run
make run                # local
make deploy IMG=img:tag # deploy

# Regenerate
make manifests generate
```

## Interview Prep

**Mid**: "kubebuilder vs Operator SDK."

**Senior**: "Markers and code generation."

**Staff**: "Operator architecture for X."

## Next Topic

→ [T05 — Writing Your First Operator](T05-Writing-Operator.md)
