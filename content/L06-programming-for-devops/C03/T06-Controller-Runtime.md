# L06/C03/T06 — controller-runtime, kubebuilder scaffolding

## Learning Objectives

- Build a K8s controller / operator
- Use kubebuilder

## Operators Recap

A K8s operator is a controller that manages a Custom Resource (CR) — encoding operational knowledge in code. Example: a `PostgresCluster` CR; controller watches it; creates StatefulSets, Services, PVCs accordingly.

Pattern: **Watch → Reconcile → Update Status**.

## controller-runtime

Library for writing controllers. Built on client-go; simpler abstractions.

```go
import (
    "sigs.k8s.io/controller-runtime/pkg/manager"
    "sigs.k8s.io/controller-runtime/pkg/reconcile"
    "sigs.k8s.io/controller-runtime/pkg/client"
)
```

## Minimal Controller

```go
type PodReconciler struct {
    client.Client
}

func (r *PodReconciler) Reconcile(ctx context.Context, req reconcile.Request) (reconcile.Result, error) {
    var pod corev1.Pod
    if err := r.Get(ctx, req.NamespacedName, &pod); err != nil {
        if errors.IsNotFound(err) {
            return reconcile.Result{}, nil   // ignore deleted
        }
        return reconcile.Result{}, err
    }
    
    // Do something based on observed state
    log.Info("Reconciling", "pod", pod.Name)
    
    return reconcile.Result{}, nil
}

// Wire up
func main() {
    mgr, _ := manager.New(rest.GetConfigOrDie(), manager.Options{})
    
    builder.ControllerManagedBy(mgr).
        For(&corev1.Pod{}).
        Complete(&PodReconciler{Client: mgr.GetClient()})
    
    mgr.Start(ctrl.SetupSignalHandler())
}
```

## kubebuilder

Scaffolding tool for operators. Generates types, controllers, manifests.

```bash
# Install
brew install kubebuilder

# Init project
mkdir myop && cd myop
kubebuilder init --domain mycompany.io --repo github.com/me/myop

# Add API (CRD + Controller)
kubebuilder create api --group apps --version v1 --kind WebService
```

Generates:
- `api/v1/webservice_types.go` (CR types)
- `controllers/webservice_controller.go` (reconciler)
- `config/crd/bases/...yaml` (CRD)
- `config/rbac/...yaml` (Roles)

## CR Type

```go
type WebServiceSpec struct {
    Image    string `json:"image"`
    Replicas int32  `json:"replicas"`
}

type WebServiceStatus struct {
    AvailableReplicas int32 `json:"availableReplicas"`
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

## Reconcile Loop

```go
func (r *WebServiceReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    // 1. Fetch CR
    var ws appsv1.WebService
    if err := r.Get(ctx, req.NamespacedName, &ws); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }
    
    // 2. Build desired Deployment
    desired := &appsv1.Deployment{
        ObjectMeta: metav1.ObjectMeta{
            Name:      ws.Name,
            Namespace: ws.Namespace,
        },
        Spec: appsv1.DeploymentSpec{
            Replicas: &ws.Spec.Replicas,
            // ... container with ws.Spec.Image
        },
    }
    
    // 3. Set ownership (auto-delete on CR delete)
    ctrl.SetControllerReference(&ws, desired, r.Scheme)
    
    // 4. Create or Update
    var existing appsv1.Deployment
    err := r.Get(ctx, types.NamespacedName{Name: ws.Name, Namespace: ws.Namespace}, &existing)
    if errors.IsNotFound(err) {
        r.Create(ctx, desired)
    } else if err == nil {
        existing.Spec = desired.Spec
        r.Update(ctx, &existing)
    } else {
        return ctrl.Result{}, err
    }
    
    // 5. Update Status
    ws.Status.AvailableReplicas = existing.Status.AvailableReplicas
    r.Status().Update(ctx, &ws)
    
    return ctrl.Result{}, nil
}
```

## Setup Function

```go
func (r *WebServiceReconciler) SetupWithManager(mgr ctrl.Manager) error {
    return ctrl.NewControllerManagedBy(mgr).
        For(&appsv1.WebService{}).
        Owns(&appsv1.Deployment{}).       // watch owned Deployments too
        Complete(r)
}
```

`Owns()` ensures re-reconcile when child Deployment changes.

## Reconcile Idempotency

Reconcile may run many times for the same state. Must be:
- Idempotent (same input → same output)
- Tolerant of partial state
- Don't assume previous Reconcile completed

## Result Types

```go
return ctrl.Result{}, nil                          // done; no requeue
return ctrl.Result{Requeue: true}, nil             // requeue immediately
return ctrl.Result{RequeueAfter: 30 * time.Second}, nil   // requeue later
return ctrl.Result{}, err                          // requeue with backoff
```

## Status Subresource

Separate from Spec; users set Spec, controller sets Status:
```go
r.Status().Update(ctx, &ws)
```

Don't put Spec changes here; permissions differ.

## RBAC Annotations

```go
// +kubebuilder:rbac:groups=apps.mycompany.io,resources=webservices,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=apps.mycompany.io,resources=webservices/status,verbs=get;update;patch
// +kubebuilder:rbac:groups=apps,resources=deployments,verbs=get;list;watch;create;update;patch;delete
func (r *WebServiceReconciler) Reconcile(...) { ... }
```

Run `make manifests` → generates Roles.

## Webhooks

Validating: reject bad CRs.
Mutating: defaulting / inject values.
```bash
kubebuilder create webhook --group apps --version v1 --kind WebService --programmatic-validation --defaulting
```

## Testing

EnvTest: runs etcd + API server locally:
```go
testEnv := &envtest.Environment{
    CRDDirectoryPaths: []string{"../config/crd/bases"},
}
cfg, _ := testEnv.Start()
defer testEnv.Stop()
```

Then create/get CRs, assert behavior. Fast; no real cluster needed.

## Operator SDK

Alternative to kubebuilder; similar; CloudNative-CN-CF; supports Helm, Ansible operators too.

## Common Patterns

- **Finalizer**: prevent CR deletion until cleanup runs
- **Conditions**: structured status (Ready, Progressing)
- **Owner refs**: cascade delete
- **Predicates**: filter events to avoid unnecessary reconciles

## Common Mistakes

- Non-idempotent Reconcile
- Setting both Spec and Status in same call
- Long Reconcile blocks
- No backoff on transient errors

## Operator Lifecycle Manager (OLM)

Standard install: deploy to cluster as a Deployment + CRDs + RBAC. Bundle as OLM if publishing to OperatorHub.

## Best Practices

- Make `Reconcile` idempotent and level-triggered: compute desired state from the spec and converge to it; never assume which event fired.
- Use `CreateOrUpdate`/server-side apply to own child objects, and set owner references so they cascade-delete with the CR.
- Update spec and status in separate calls; use the status subresource (`Status().Update`) so spec and status don't clobber each other.
- Return `ctrl.Result{RequeueAfter: ...}` (or an error) to retry transient failures with backoff instead of blocking inside Reconcile.
- Use finalizers for external cleanup, and remove the finalizer only after teardown succeeds.
- Filter noise with predicates/`GenerationChangedPredicate` and keep RBAC kubebuilder markers in sync with what the controller touches.

## Quick Refs

```go
func (r *AppReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    var app v1alpha1.App
    if err := r.Get(ctx, req.NamespacedName, &app); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)   // deleted: nothing to do
    }

    // Desired child object, owned by the CR (idempotent create-or-update)
    dep := desiredDeployment(&app)
    if err := ctrl.SetControllerReference(&app, dep, r.Scheme); err != nil {
        return ctrl.Result{}, err
    }
    if _, err := ctrl.CreateOrUpdate(ctx, r.Client, dep, func() error {
        dep.Spec.Replicas = &app.Spec.Replicas
        return nil
    }); err != nil {
        return ctrl.Result{}, err   // controller-runtime requeues with backoff
    }

    app.Status.Ready = true
    if err := r.Status().Update(ctx, &app); err != nil {  // status subresource
        return ctrl.Result{}, err
    }
    return ctrl.Result{}, nil
}
```

```go
//+kubebuilder:rbac:groups=apps.example.com,resources=apps,verbs=get;list;watch;update
//+kubebuilder:rbac:groups=apps,resources=deployments,verbs=get;list;watch;create;update
```

```bash
kubebuilder init --domain example.com --repo github.com/me/op
kubebuilder create api --group apps --version v1alpha1 --kind App
make manifests        # regenerate CRDs + RBAC from markers
make install run      # apply CRDs, run controller locally
```

## Interview Prep

**Mid**: "What is Reconcile?"

**Senior**: "Design operator for X."

**Staff**: "Idempotency in Reconcile."

## Next Topic

→ [T07 — Testing Go Code](T07-Testing-Go.md)
