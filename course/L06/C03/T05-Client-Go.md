# L06/C03/T05 — client-go for Kubernetes

## Learning Objectives

- Talk to K8s API from Go
- Use informers + workqueues

## Setup

```go
import (
    "context"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/tools/clientcmd"
    "k8s.io/client-go/rest"
)

// Out-of-cluster (local dev)
config, _ := clientcmd.BuildConfigFromFlags("", os.Getenv("KUBECONFIG"))

// In-cluster (running in pod)
config, _ := rest.InClusterConfig()

clientset, _ := kubernetes.NewForConfig(config)
```

## Basic Operations

```go
ctx := context.Background()

// List pods
pods, _ := clientset.CoreV1().Pods("default").List(ctx, metav1.ListOptions{})
for _, p := range pods.Items {
    fmt.Println(p.Name, p.Status.Phase)
}

// Get
pod, _ := clientset.CoreV1().Pods("default").Get(ctx, "mypod", metav1.GetOptions{})

// Create
clientset.CoreV1().Pods("default").Create(ctx, pod, metav1.CreateOptions{})

// Update
clientset.CoreV1().Pods("default").Update(ctx, pod, metav1.UpdateOptions{})

// Delete
clientset.CoreV1().Pods("default").Delete(ctx, "mypod", metav1.DeleteOptions{})

// Patch (preferred for partial updates)
clientset.CoreV1().Pods("default").Patch(ctx, "mypod", types.MergePatchType, patchData, metav1.PatchOptions{})
```

## Other Resources

```go
clientset.AppsV1().Deployments("ns").List(...)
clientset.BatchV1().Jobs("ns").Create(...)
clientset.NetworkingV1().Ingresses("ns").Get(...)
clientset.CoreV1().Services("ns").List(...)
clientset.CoreV1().ConfigMaps("ns").Get(...)
clientset.CoreV1().Secrets("ns").Create(...)
clientset.RbacV1().Roles("ns").Get(...)
```

## Label Selectors

```go
pods, _ := clientset.CoreV1().Pods("").List(ctx, metav1.ListOptions{
    LabelSelector: "app=web,env=prod",
})

// Field selector
pods, _ := clientset.CoreV1().Pods("").List(ctx, metav1.ListOptions{
    FieldSelector: "status.phase=Running",
})
```

## Watch

Stream events:
```go
watch, err := clientset.CoreV1().Pods("").Watch(ctx, metav1.ListOptions{})
defer watch.Stop()

for event := range watch.ResultChan() {
    pod := event.Object.(*v1.Pod)
    fmt.Println(event.Type, pod.Name)
}
```

Event.Type: Added, Modified, Deleted, Error.

## Informers (Production Pattern)

Watch raw is fragile (disconnect on idle). Informers:
- Cache in memory
- Auto-reconnect
- Index by namespace, label, etc.
- Foundation for controllers

```go
import "k8s.io/client-go/informers"

factory := informers.NewSharedInformerFactory(clientset, time.Minute)
podInformer := factory.Core().V1().Pods()

podInformer.Informer().AddEventHandler(cache.ResourceEventHandlerFuncs{
    AddFunc: func(obj interface{}) {
        pod := obj.(*v1.Pod)
        fmt.Println("Added:", pod.Name)
    },
    UpdateFunc: func(oldObj, newObj interface{}) {
        oldPod := oldObj.(*v1.Pod)
        newPod := newObj.(*v1.Pod)
        fmt.Println("Updated:", newPod.Name)
    },
    DeleteFunc: func(obj interface{}) {
        pod := obj.(*v1.Pod)
        fmt.Println("Deleted:", pod.Name)
    },
})

stopCh := make(chan struct{})
factory.Start(stopCh)
factory.WaitForCacheSync(stopCh)

<-stopCh    // run forever
```

## Lister

Read from informer cache (zero API calls):
```go
podLister := podInformer.Lister()
pods, _ := podLister.Pods("default").List(labels.Everything())

// With selector
selector, _ := labels.Parse("app=web")
pods, _ := podLister.Pods("default").List(selector)
```

## WorkQueue

Process changes asynchronously with retry:
```go
import "k8s.io/client-go/util/workqueue"

queue := workqueue.NewRateLimitingQueue(workqueue.DefaultControllerRateLimiter())

// Add work
podInformer.Informer().AddEventHandler(cache.ResourceEventHandlerFuncs{
    AddFunc: func(obj interface{}) {
        key, _ := cache.MetaNamespaceKeyFunc(obj)
        queue.Add(key)
    },
})

// Process
go func() {
    for {
        key, quit := queue.Get()
        if quit {
            return
        }
        err := processItem(key.(string))
        if err != nil {
            queue.AddRateLimited(key)   // retry
        } else {
            queue.Forget(key)
        }
        queue.Done(key)
    }
}()
```

## Custom Resources

Generated clientset for CRDs (or use dynamic client):
```go
import "k8s.io/client-go/dynamic"

dynClient, _ := dynamic.NewForConfig(config)
gvr := schema.GroupVersionResource{Group: "example.com", Version: "v1", Resource: "myresources"}
list, _ := dynClient.Resource(gvr).Namespace("default").List(ctx, metav1.ListOptions{})
```

For typed CRD clientset: use code-generator or kubebuilder.

## Authentication

In-cluster: ServiceAccount token mounted at `/var/run/secrets/kubernetes.io/serviceaccount/`.

ClusterRoleBinding needed for the SA.

Out-of-cluster: kubeconfig, file-based, AKS/EKS plugin, etc.

## RetryOnConflict

For Update conflicts (Resource Version):
```go
import "k8s.io/client-go/util/retry"

err := retry.RetryOnConflict(retry.DefaultRetry, func() error {
    pod, err := client.CoreV1().Pods("ns").Get(ctx, "name", metav1.GetOptions{})
    if err != nil {
        return err
    }
    pod.Spec.Containers[0].Image = "new"
    _, err = client.CoreV1().Pods("ns").Update(ctx, pod, metav1.UpdateOptions{})
    return err
})
```

## controller-runtime (Higher-Level)

Used by Operator SDK / Kubebuilder; wraps client-go with conveniences:
```go
import "sigs.k8s.io/controller-runtime/pkg/client"

c, _ := client.New(config, client.Options{})
var pods v1.PodList
c.List(ctx, &pods, client.InNamespace("default"))
```

Most operators use controller-runtime.

## Common Mistakes

- Using `Watch` directly instead of Informer
- No RBAC for ServiceAccount
- Update without conflict retry
- Long lived watch without timeout
- Reading from API server every loop (use Lister)

## Interview Prep

**Mid**: "Informer vs raw Watch."

**Senior**: "Resource conflict — handle."

**Staff**: "Build an operator from scratch (high-level)."

## Next Topic

→ [T06 — controller-runtime](T06-Controller-Runtime.md)
