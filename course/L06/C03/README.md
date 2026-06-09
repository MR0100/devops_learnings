# L06/C03 — Go for DevOps

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Why-Go.md) | Why Go Dominates Cloud-Native Tooling | 0.5 hr |
| [T02](T02-Modules-Workspaces.md) | Modules, Packages, Workspaces | 1 hr |
| [T03](T03-Concurrency.md) | Concurrency (Goroutines, Channels, sync) | 2 hr |
| [T04](T04-Standard-Library.md) | Standard Library (net/http, context, os/exec) | 1.5 hr |
| [T05](T05-Cobra-Viper.md) | Writing CLIs with Cobra & Viper | 1 hr |
| [T06](T06-Client-Go.md) | client-go for Kubernetes | 1.5 hr |
| [T07](T07-Controller-Runtime.md) | controller-runtime for Operators | 2 hr |

## Why Go Won Cloud-Native

- Single static binary (no runtime, no deps)
- Fast compile, fast startup
- Goroutines for trivial concurrency
- Strong standard library (especially net/http)
- Simple syntax (small surface area)
- Used by Google internally
- Right place at right time (2012)

Result: Kubernetes, Docker, Terraform, Prometheus, etcd, all written in Go.

## Modules

```bash
go mod init github.com/me/myproj
go get github.com/spf13/cobra@latest
go mod tidy
go mod vendor                # optional vendoring
```

`go.mod` declares dependencies; `go.sum` is the lockfile (checksums).

### Workspaces (Go 1.18+)
For multi-module repos:
```
go.work
└── use ./svc-a ./svc-b ./libs/shared
```

## Concurrency

### Goroutines
```go
go someFunc()    // run concurrently
```

Cheap (~few KB stack, grows on demand). Spawn millions.

### Channels
```go
ch := make(chan int, 10)   // buffered, capacity 10

go func() {
    for i := 0; i < 5; i++ {
        ch <- i
    }
    close(ch)
}()

for v := range ch {
    fmt.Println(v)
}
```

### Select
```go
select {
case v := <-ch1:
    fmt.Println("from ch1:", v)
case v := <-ch2:
    fmt.Println("from ch2:", v)
case <-time.After(5 * time.Second):
    fmt.Println("timeout")
case <-ctx.Done():
    fmt.Println("cancelled")
}
```

### sync.WaitGroup
```go
var wg sync.WaitGroup
for _, item := range items {
    wg.Add(1)
    go func(it Item) {
        defer wg.Done()
        process(it)
    }(item)
}
wg.Wait()
```

### errgroup (more useful)
```go
import "golang.org/x/sync/errgroup"

g, ctx := errgroup.WithContext(context.Background())
for _, url := range urls {
    url := url
    g.Go(func() error {
        return fetch(ctx, url)
    })
}
if err := g.Wait(); err != nil {
    log.Fatal(err)
}
```

### sync.Mutex / RWMutex
```go
type Counter struct {
    mu sync.Mutex
    n  int
}

func (c *Counter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.n++
}
```

### Context

```go
ctx, cancel := context.WithTimeout(parent, 5*time.Second)
defer cancel()

req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
resp, err := http.DefaultClient.Do(req)
```

Every function that does I/O should take `ctx context.Context` as first arg.

## net/http

```go
// Server
mux := http.NewServeMux()
mux.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
    w.WriteHeader(200)
    fmt.Fprintln(w, "ok")
})

srv := &http.Server{
    Addr:         ":8080",
    Handler:      mux,
    ReadTimeout:  5 * time.Second,
    WriteTimeout: 10 * time.Second,
    IdleTimeout:  60 * time.Second,
}

go srv.ListenAndServe()

// graceful shutdown
<-ctx.Done()
shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
defer cancel()
srv.Shutdown(shutdownCtx)
```

```go
// Client
client := &http.Client{Timeout: 5 * time.Second}
resp, err := client.Get(url)
if err != nil { ... }
defer resp.Body.Close()
body, _ := io.ReadAll(resp.Body)
```

## os/exec

```go
cmd := exec.CommandContext(ctx, "kubectl", "get", "pods")
cmd.Stdout = os.Stdout
cmd.Stderr = os.Stderr
err := cmd.Run()
```

## Cobra CLI

```go
package main

import (
    "github.com/spf13/cobra"
    "github.com/spf13/viper"
)

var rootCmd = &cobra.Command{
    Use:   "mytool",
    Short: "Description",
}

var deployCmd = &cobra.Command{
    Use:   "deploy [service] [version]",
    Args:  cobra.ExactArgs(2),
    RunE: func(cmd *cobra.Command, args []string) error {
        service, version := args[0], args[1]
        dryRun := viper.GetBool("dry-run")
        // ...
        return nil
    },
}

func init() {
    rootCmd.AddCommand(deployCmd)
    deployCmd.Flags().Bool("dry-run", false, "")
    viper.BindPFlag("dry-run", deployCmd.Flags().Lookup("dry-run"))
}

func main() {
    rootCmd.Execute()
}
```

## client-go (Kubernetes)

```go
import (
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/tools/clientcmd"
)

config, _ := clientcmd.BuildConfigFromFlags("", kubeconfig)
clientset, _ := kubernetes.NewForConfig(config)

pods, _ := clientset.CoreV1().Pods("").List(ctx, metav1.ListOptions{})
for _, p := range pods.Items {
    fmt.Println(p.Namespace, p.Name)
}

// In-cluster (when running in a pod):
config, _ := rest.InClusterConfig()
```

### Informer pattern (for controllers/watchers)
```go
factory := informers.NewSharedInformerFactory(clientset, time.Minute*5)
podInformer := factory.Core().V1().Pods().Informer()
podInformer.AddEventHandler(cache.ResourceEventHandlerFuncs{
    AddFunc:    func(obj interface{}) { ... },
    UpdateFunc: func(old, new interface{}) { ... },
    DeleteFunc: func(obj interface{}) { ... },
})
factory.Start(stopCh)
```

## controller-runtime

Higher level than client-go. Use kubebuilder to scaffold:

```go
type MyReconciler struct {
    client.Client
    Scheme *runtime.Scheme
}

func (r *MyReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    var obj myv1.MyResource
    if err := r.Get(ctx, req.NamespacedName, &obj); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }
    // reconcile logic
    return ctrl.Result{RequeueAfter: time.Minute}, nil
}

func (r *MyReconciler) SetupWithManager(mgr ctrl.Manager) error {
    return ctrl.NewControllerManagedBy(mgr).
        For(&myv1.MyResource{}).
        Owns(&appsv1.Deployment{}).
        Complete(r)
}
```

## Testing in Go

```go
func TestAdd(t *testing.T) {
    if got := Add(2, 3); got != 5 {
        t.Errorf("Add(2,3) = %d, want 5", got)
    }
}

// Table-driven
func TestAddTable(t *testing.T) {
    tests := []struct {
        name        string
        a, b, want int
    }{
        {"positive", 2, 3, 5},
        {"zero", 0, 0, 0},
        {"negative", -1, -2, -3},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            if got := Add(tt.a, tt.b); got != tt.want {
                t.Errorf("Add(%d,%d) = %d, want %d", tt.a, tt.b, got, tt.want)
            }
        })
    }
}
```

## Interview Themes

- "Why is Go dominant in cloud-native?"
- "Walk through Go's concurrency (goroutines, channels, select)"
- "Write a concurrent HTTP fetcher with rate limiting"
- "How would you write a K8s operator?"
- "Context — what is it and why pass it everywhere?"
- "Error handling in Go — defend the design"
