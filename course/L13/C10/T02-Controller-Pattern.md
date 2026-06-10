# L13/C10/T02 — Controller Pattern

## Learning Objectives

- Apply controller pattern
- Write idempotent reconcile

## Controller

Process watching resources; reconciling desired vs actual.

K8s built-in controllers:
- ReplicaSet controller
- Deployment controller
- StatefulSet controller
- Node controller
- ...

Operators: custom controllers for domain-specific resources.

## Reconcile Loop

```
1. Watch resources (via API Server)
2. Receive event (created/updated/deleted)
3. Reconcile:
   a. Read current state (Spec + Status + related)
   b. Compute desired state
   c. Compare
   d. Take action to converge
   e. Update Status
4. Loop
```

## Level Triggered

K8s controllers are level-triggered:
- Don't track each event
- Check current state vs desired
- Eventually converge

vs edge-triggered (per event): brittle.

## Properties

### Idempotent
Same input = same output. Run reconcile twice: same end state.

### Convergent
Eventually matches desired state.

### Resilient
Restart controller: continues from current state (read from API).

## Reconciler Skeleton

```go
func (r *MyReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    // 1. Fetch CR
    var obj myv1.MyResource
    if err := r.Get(ctx, req.NamespacedName, &obj); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }
    
    // 2. Handle deletion (finalizer)
    if !obj.DeletionTimestamp.IsZero() {
        return r.handleDelete(ctx, &obj)
    }
    
    // 3. Compute desired state
    desired := computeDesired(&obj)
    
    // 4. Read actual state
    var existing appsv1.Deployment
    err := r.Get(ctx, ..., &existing)
    
    // 5. Create or Update
    if errors.IsNotFound(err) {
        r.Create(ctx, desired)
    } else {
        existing.Spec = desired.Spec
        r.Update(ctx, &existing)
    }
    
    // 6. Update Status
    obj.Status.Phase = "Ready"
    r.Status().Update(ctx, &obj)
    
    // 7. Return
    return ctrl.Result{}, nil
}
```

## Watch + Cache

controller-runtime provides:
- Watch resources via Informer
- Cache for read operations (no API spam)
- Workqueue for processing

```go
func (r *MyReconciler) SetupWithManager(mgr ctrl.Manager) error {
    return ctrl.NewControllerManagedBy(mgr).
        For(&myv1.MyResource{}).
        Owns(&appsv1.Deployment{}).
        Complete(r)
}
```

`For`: watch this CR.
`Owns`: watch children (re-reconcile when changes).

## Owner Reference

Child resources owned by parent CR:
```go
ctrl.SetControllerReference(&obj, deployment, r.Scheme)
```

Sets `metadata.ownerReferences`. 

Effect:
- Garbage collection: delete CR → child auto-deleted
- Owns: parent reconciled when child changes

## Workqueue

Controller-runtime workqueue:
- Items added on events
- Multiple events for same item: deduped
- Retry on error with backoff

```go
return ctrl.Result{RequeueAfter: 30 * time.Second}, nil
```

Re-reconcile after delay.

## Return Values

```go
return ctrl.Result{}, nil              // done; no requeue (until next event)
return ctrl.Result{Requeue: true}, nil // requeue immediately
return ctrl.Result{RequeueAfter: 30 * time.Second}, nil
return ctrl.Result{}, err              // requeue with backoff (exponential)
```

## Status Update

```go
obj.Status.Phase = "Ready"
obj.Status.Conditions = append(obj.Status.Conditions, metav1.Condition{
    Type: "Ready",
    Status: metav1.ConditionTrue,
    Reason: "DeploymentAvailable",
    LastTransitionTime: metav1.Now(),
})
if err := r.Status().Update(ctx, &obj); err != nil {
    return ctrl.Result{}, err
}
```

`Status().Update`: updates only status subresource.

## Conditions Pattern

Standard:
```go
type Condition struct {
    Type               string
    Status             ConditionStatus  // True/False/Unknown
    LastTransitionTime metav1.Time
    Reason             string
    Message            string
}
```

Common types:
- Ready
- Progressing
- ReplicaFailure
- Degraded
- ResourceQuota

For: standardized status reporting.

## Finalizers

For pre-delete cleanup:
```go
const finalizer = "mycompany.io/cleanup"

if obj.DeletionTimestamp.IsZero() {
    // Add finalizer if not present
    if !contains(obj.Finalizers, finalizer) {
        controllerutil.AddFinalizer(&obj, finalizer)
        r.Update(ctx, &obj)
        return ctrl.Result{}, nil
    }
} else {
    // Cleanup external resources
    if err := cleanupExternalResources(&obj); err != nil {
        return ctrl.Result{}, err
    }
    
    // Remove finalizer
    controllerutil.RemoveFinalizer(&obj, finalizer)
    r.Update(ctx, &obj)
    return ctrl.Result{}, nil
}
```

K8s only deletes once all finalizers removed.

## Error Handling

```go
if err := r.Update(ctx, &obj); err != nil {
    log.Error(err, "update failed")
    return ctrl.Result{}, err   // requeue with backoff
}
```

Retry on transient.

For permanent: log + don't requeue:
```go
return ctrl.Result{}, nil
```

## Idempotency

Same Reconcile → same end state.

Example:
```go
// BAD: create every time
r.Create(ctx, deployment)   // fails on second call

// GOOD: check-then-create OR upsert
err := r.Get(ctx, ..., &existing)
if errors.IsNotFound(err) {
    r.Create(ctx, deployment)
} else {
    existing.Spec = deployment.Spec
    r.Update(ctx, &existing)
}
```

Or use controllerutil.CreateOrUpdate.

## Server-Side Apply

```go
err := r.Patch(ctx, deployment, client.Apply, client.FieldOwner("my-controller"), client.ForceOwnership)
```

Server merges; controller "owns" certain fields. Prevents conflict with user edits.

## RBAC

Controller needs permissions:
```yaml
- apiGroups: ["apps.mycompany.io"]
  resources: ["webservices", "webservices/status"]
  verbs: ["get", "list", "watch", "update", "patch"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
```

kubebuilder annotations generate:
```go
// +kubebuilder:rbac:groups=apps.mycompany.io,resources=webservices,verbs=get;list;watch;update;patch
```

## Leader Election

For HA controller (multiple replicas):
```go
mgr, _ := ctrl.NewManager(cfg, ctrl.Options{
    LeaderElection:          true,
    LeaderElectionID:        "my-controller",
    LeaderElectionNamespace: "my-namespace",
})
```

Only one active; others stand by.

For: avoid conflict + always running.

## Metrics

controller-runtime exposes:
- Reconciliation count
- Reconciliation duration
- Errors
- Workqueue depth

Prometheus scrape:
```yaml
spec:
  ports:
  - name: metrics
    port: 8080
```

For monitoring.

## Predicates

Filter events:
```go
controller.Watches(
    &source.Kind{Type: &appsv1.Deployment{}},
    handler.EnqueueRequestsFromMapFunc(mapDeploymentToCR),
    builder.WithPredicates(predicate.GenerationChangedPredicate{}),
)
```

Skip irrelevant events. Reduces noise.

## Common Mistakes

- Not idempotent (creates duplicates)
- Reconcile from status (loops)
- No backoff (overload)
- Tight loop (Requeue: true always)
- Update + reconcile event loop
- No leader election (multiple controllers)
- Owner refs wrong (garbage collection issues)

## Best Practices

- Idempotent
- Use Owns for children
- Server-side apply
- Conditions pattern
- Finalizers for cleanup
- Leader election
- Metrics
- Predicates
- Backoff on error
- Resource limits

## Testing

```go
import "sigs.k8s.io/controller-runtime/pkg/envtest"

testEnv := &envtest.Environment{
    CRDDirectoryPaths: []string{"config/crd/bases"},
}
cfg, _ := testEnv.Start()
defer testEnv.Stop()
```

envtest: in-memory API Server + etcd. Test reconciler.

## Real Operators

### Cert-Manager
Watches Certificate CRs; creates ACME order; updates Secret.

### Prometheus Operator
Watches Prometheus, ServiceMonitor; creates StatefulSets, configures.

### CloudNativePG
Watches Cluster (PG); creates StatefulSets, configures, manages backups.

### Velero
Watches Backup, Restore CRs; performs backups.

Pattern: same. Controller per domain.

## Inspection

```bash
# Controller logs
kubectl logs -n operator-system controller-xxx

# Events for CR
kubectl describe webservice my-app

# Status
kubectl get webservice my-app -o jsonpath='{.status}'
```

## Quick Refs

```bash
# Operator install
kubectl apply -f operator.yaml

# CR
kubectl apply -f my-cr.yaml

# Status watch
kubectl get webservice -w

# Events
kubectl get events --field-selector involvedObject.kind=WebService
```

## Interview Prep

**Mid**: "Controller pattern."

**Senior**: "Reconcile idempotency."

**Staff**: "Design controller for X domain."

## Next Topic

→ [T03 — Operator SDK (Go, Ansible, Helm)](T03-Operator-SDK.md)
