# L13/C10/T05 — Writing Your First Operator

## Learning Objectives

- Build operator end-to-end
- Deploy + test

## Goal

Build operator for `WebService` CR:
- User creates WebService(image, replicas)
- Operator creates Deployment + Service
- Updates status with ready replicas

## Step 1: Bootstrap

```bash
mkdir webservice-operator && cd webservice-operator
go mod init github.com/me/webservice-operator
kubebuilder init --domain mycompany.io
kubebuilder create api --group apps --version v1 --kind WebService
```

## Step 2: Define API

```go
// api/v1/webservice_types.go

type WebServiceSpec struct {
    // +kubebuilder:validation:Required
    Image string `json:"image"`
    
    // +kubebuilder:validation:Minimum=1
    // +kubebuilder:validation:Maximum=20
    // +kubebuilder:default=1
    Replicas int32 `json:"replicas,omitempty"`
    
    // +kubebuilder:default=80
    Port int32 `json:"port,omitempty"`
}

type WebServiceStatus struct {
    AvailableReplicas int32 `json:"availableReplicas,omitempty"`
    URL               string `json:"url,omitempty"`
    Conditions        []metav1.Condition `json:"conditions,omitempty"`
}

// +kubebuilder:object:root=true
// +kubebuilder:subresource:status
// +kubebuilder:printcolumn:name="Image",type=string,JSONPath=`.spec.image`
// +kubebuilder:printcolumn:name="Replicas",type=integer,JSONPath=`.spec.replicas`
// +kubebuilder:printcolumn:name="Available",type=integer,JSONPath=`.status.availableReplicas`
// +kubebuilder:printcolumn:name="URL",type=string,JSONPath=`.status.url`
type WebService struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`
    Spec   WebServiceSpec   `json:"spec,omitempty"`
    Status WebServiceStatus `json:"status,omitempty"`
}
```

## Step 3: Generate CRD

```bash
make manifests
```

Inspect `config/crd/bases/apps.mycompany.io_webservices.yaml`.

## Step 4: Implement Controller

```go
// internal/controller/webservice_controller.go

// +kubebuilder:rbac:groups=apps.mycompany.io,resources=webservices,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=apps.mycompany.io,resources=webservices/status,verbs=get;update;patch
// +kubebuilder:rbac:groups=apps,resources=deployments,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups="",resources=services,verbs=get;list;watch;create;update;patch;delete

func (r *WebServiceReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    log := log.FromContext(ctx)
    
    // 1. Fetch CR
    var ws appsv1.WebService
    if err := r.Get(ctx, req.NamespacedName, &ws); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }
    
    // 2. Reconcile Deployment
    if err := r.reconcileDeployment(ctx, &ws); err != nil {
        log.Error(err, "deployment reconcile failed")
        return ctrl.Result{}, err
    }
    
    // 3. Reconcile Service
    if err := r.reconcileService(ctx, &ws); err != nil {
        log.Error(err, "service reconcile failed")
        return ctrl.Result{}, err
    }
    
    // 4. Update status
    if err := r.updateStatus(ctx, &ws); err != nil {
        log.Error(err, "status update failed")
        return ctrl.Result{}, err
    }
    
    return ctrl.Result{}, nil
}

func (r *WebServiceReconciler) reconcileDeployment(ctx context.Context, ws *appsv1.WebService) error {
    deployment := &appsv1.Deployment{
        ObjectMeta: metav1.ObjectMeta{
            Name:      ws.Name,
            Namespace: ws.Namespace,
        },
    }
    
    _, err := ctrl.CreateOrUpdate(ctx, r.Client, deployment, func() error {
        deployment.Spec = appsv1.DeploymentSpec{
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
                        Ports: []corev1.ContainerPort{{
                            ContainerPort: ws.Spec.Port,
                        }},
                    }},
                },
            },
        }
        return ctrl.SetControllerReference(ws, deployment, r.Scheme)
    })
    return err
}

func (r *WebServiceReconciler) reconcileService(ctx context.Context, ws *appsv1.WebService) error {
    service := &corev1.Service{
        ObjectMeta: metav1.ObjectMeta{
            Name:      ws.Name,
            Namespace: ws.Namespace,
        },
    }
    
    _, err := ctrl.CreateOrUpdate(ctx, r.Client, service, func() error {
        service.Spec = corev1.ServiceSpec{
            Selector: map[string]string{"app": ws.Name},
            Ports: []corev1.ServicePort{{
                Port:       ws.Spec.Port,
                TargetPort: intstr.FromInt(int(ws.Spec.Port)),
            }},
        }
        return ctrl.SetControllerReference(ws, service, r.Scheme)
    })
    return err
}

func (r *WebServiceReconciler) updateStatus(ctx context.Context, ws *appsv1.WebService) error {
    var deployment appsv1.Deployment
    err := r.Get(ctx, types.NamespacedName{Name: ws.Name, Namespace: ws.Namespace}, &deployment)
    if err != nil {
        return err
    }
    
    ws.Status.AvailableReplicas = deployment.Status.AvailableReplicas
    ws.Status.URL = fmt.Sprintf("http://%s.%s.svc.cluster.local:%d", ws.Name, ws.Namespace, ws.Spec.Port)
    
    // Update condition
    meta.SetStatusCondition(&ws.Status.Conditions, metav1.Condition{
        Type:    "Ready",
        Status:  metav1.ConditionStatus(condStatus(deployment.Status.AvailableReplicas, ws.Spec.Replicas)),
        Reason:  "DeploymentReconciled",
        Message: fmt.Sprintf("%d/%d available", deployment.Status.AvailableReplicas, ws.Spec.Replicas),
    })
    
    return r.Status().Update(ctx, ws)
}

func condStatus(actual, desired int32) string {
    if actual == desired {
        return "True"
    }
    return "False"
}

func (r *WebServiceReconciler) SetupWithManager(mgr ctrl.Manager) error {
    return ctrl.NewControllerManagedBy(mgr).
        For(&appsv1.WebService{}).
        Owns(&appsv1.Deployment{}).
        Owns(&corev1.Service{}).
        Complete(r)
}
```

## Step 5: Test Locally

```bash
make install      # install CRDs to cluster
make run          # run operator locally
```

Apply CR in another terminal:
```yaml
# sample.yaml
apiVersion: apps.mycompany.io/v1
kind: WebService
metadata:
  name: my-app
  namespace: default
spec:
  image: nginx:1.27
  replicas: 3
  port: 80
```

```bash
kubectl apply -f sample.yaml
kubectl get webservice
# NAME    IMAGE        REPLICAS   AVAILABLE   URL                                        
# my-app  nginx:1.27   3          3           http://my-app.default.svc.cluster.local:80

kubectl get deployment
# my-app   3/3     ...

kubectl get svc
# my-app   ClusterIP  ...
```

## Step 6: Edit and Observe

```bash
kubectl edit webservice my-app
# Change replicas: 5
```

Operator sees change → reconciles → Deployment scales to 5.

```bash
kubectl get webservice -w
```

## Step 7: Delete CR

```bash
kubectl delete webservice my-app
```

Owner refs → Deployment + Service auto-deleted.

## Step 8: Build + Deploy

```bash
make docker-build docker-push IMG=myregistry/op:v1
make deploy IMG=myregistry/op:v1
```

Operator now runs in cluster.

## Add Finalizer (Optional)

For external cleanup (e.g., DNS record, cloud resource):
```go
const finalizer = "mycompany.io/cleanup"

func (r *WebServiceReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    var ws appsv1.WebService
    if err := r.Get(ctx, req.NamespacedName, &ws); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }
    
    // Deletion handling
    if !ws.DeletionTimestamp.IsZero() {
        if controllerutil.ContainsFinalizer(&ws, finalizer) {
            // External cleanup
            if err := cleanupExternal(&ws); err != nil {
                return ctrl.Result{}, err
            }
            controllerutil.RemoveFinalizer(&ws, finalizer)
            r.Update(ctx, &ws)
        }
        return ctrl.Result{}, nil
    }
    
    // Add finalizer if missing
    if !controllerutil.ContainsFinalizer(&ws, finalizer) {
        controllerutil.AddFinalizer(&ws, finalizer)
        r.Update(ctx, &ws)
        return ctrl.Result{}, nil
    }
    
    // Normal reconciliation
    // ...
}
```

## Add Webhook (Optional)

```bash
kubebuilder create webhook --group apps --version v1 --kind WebService --defaulting --programmatic-validation
```

Implement:
```go
func (r *WebService) Default() {
    if r.Spec.Image == "" {
        r.Spec.Image = "nginx"
    }
}

func (r *WebService) ValidateCreate() (admission.Warnings, error) {
    if r.Spec.Replicas > 10 {
        return nil, errors.New("max 10 replicas")
    }
    return nil, nil
}
```

## Testing

```go
// internal/controller/webservice_controller_test.go

var _ = Describe("WebService Controller", func() {
    It("creates deployment when CR is created", func() {
        ws := &appsv1.WebService{
            ObjectMeta: metav1.ObjectMeta{
                Name: "test-ws",
                Namespace: "default",
            },
            Spec: appsv1.WebServiceSpec{
                Image: "nginx",
                Replicas: 2,
                Port: 80,
            },
        }
        Expect(k8sClient.Create(ctx, ws)).Should(Succeed())
        
        Eventually(func() error {
            var dep apps2v1.Deployment
            return k8sClient.Get(ctx, types.NamespacedName{Name: "test-ws", Namespace: "default"}, &dep)
        }, timeout, interval).Should(Succeed())
    })
})
```

```bash
make test
```

## Observability

Operator exposes metrics:
- `controller_runtime_reconcile_total`
- `controller_runtime_reconcile_errors_total`
- `controller_runtime_reconcile_time_seconds`

Add custom:
```go
var webServiceCreations = prometheus.NewCounter(...)
webServiceCreations.Inc()
```

## Logging

```go
log := log.FromContext(ctx)
log.Info("reconciling", "name", req.Name, "namespace", req.Namespace)
log.Error(err, "failed to update")
```

Structured logs (logr); shipped via standard pipeline.

## Production Considerations

- Leader election (multi-replica HA)
- Resource limits
- ServiceAccount + RBAC
- Network policies
- Health probes
- Graceful shutdown

## Deploy Production

```bash
helm install my-op ./helm-chart --set image.tag=v1
# or
kubectl apply -f deploy/operator.yaml
```

For OperatorHub: bundle + submit.

## Iteration

Operator development cycle:
1. Modify Spec / Status types
2. `make manifests`
3. Run / deploy
4. Test
5. Repeat

For fast: Tilt for live-reload.

## Best Practices Recap

- Markers everywhere (auto CRD)
- CreateOrUpdate (or server-side apply)
- Owner references
- Status updates
- Conditions pattern
- Finalizers if external cleanup needed
- Leader election
- Tests (unit + envtest + E2E)
- Metrics + logging

## Common Mistakes

- Forgot `make manifests`
- Not idempotent (creates duplicates)
- Status update loops (re-triggers reconcile)
- No owner reference (orphan resources)
- Privileged unnecessarily

## Real-World Comparison

What you built is simpler than:
- CloudNativePG (handles backups, failover, etc.)
- Strimzi (Kafka with brokers, topics, users)
- Prometheus Operator (multiple CRs interacting)

Each takes months of dev; your skeleton is start.

## Quick Refs

```bash
# Iterate
make manifests
make run

# Build + deploy
make docker-build docker-push IMG=...
make deploy IMG=...

# Test
make test

# Sample
kubectl apply -f config/samples/
kubectl get webservices
```

## Interview Prep

**Mid**: "Build operator for X (high-level)."

**Senior**: "Reconcile loop walkthrough."

**Staff**: "Operator architecture decision tree."

## Next Topic

→ Move to [L13/C11 — Helm](../C11/README.md)
