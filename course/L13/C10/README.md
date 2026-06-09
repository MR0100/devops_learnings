# L13/C10 — Operators & CRDs

## Topics

- **T01 Custom Resource Definitions (CRDs)** — Extend K8s API with your own resources. OpenAPI v3 schema for validation, versioning, conversion webhooks.
- **T02 Controller Pattern** — Watch resources, compare desired vs actual, take action. The Operator pattern is "controller for a specific domain (DB, queue, etc.)"
- **T03 Operator SDK (Go, Ansible, Helm)** — Scaffolding for building Operators in Go (control), Ansible (use playbooks), or Helm (rendered).
- **T04 kubebuilder** — Lower-level than Operator SDK; produces controller-runtime projects.
- **T05 Writing Your First Operator** — Define CRD → generate types → write reconcile loop → register controller → install RBAC.

## The Reconcile Loop

```go
func (r *MyReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    obj := &myv1.MyResource{}
    if err := r.Get(ctx, req.NamespacedName, obj); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }
    // 1. Read desired state from obj.Spec
    // 2. Read actual state (query other resources, external APIs)
    // 3. Diff
    // 4. Apply changes
    // 5. Update obj.Status
    // 6. Return requeue or nil
    return ctrl.Result{}, nil
}
```

## Known Production Operators

| Domain | Operator |
|---|---|
| Postgres | Crunchy, Zalando, CloudNativePG |
| Kafka | Strimzi, Confluent for K8s |
| Redis | Redis Operator (various) |
| Prometheus | prometheus-operator |
| Cert management | cert-manager |
| Secrets | External Secrets, Vault |
| Backup | Velero |
| Storage | Rook (Ceph), OpenEBS |

## When to Build an Operator

- The lifecycle of your thing is non-trivial (more than `helm install`)
- You need to react to events (failovers, scaling, upgrades)
- Multiple teams use the same pattern (encode it once, expose as CR)

## When NOT to Build an Operator

- Simple Deployment + Service + ConfigMap → use Helm
- Once-per-cluster setup → use IaC
- Trivial automation → use a Job

## Interview Themes

- "What's a controller / operator pattern?"
- "Walk me through a CRD lifecycle"
- "When would you build an operator vs use Helm?"
- "How does watch + reconcile work under the hood?"
