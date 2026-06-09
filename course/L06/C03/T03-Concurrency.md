# L06/C03/T03 — Concurrency: Goroutines & Channels

## Learning Objectives

- Master Go concurrency primitives
- Avoid common pitfalls

## Goroutines

Lightweight threads managed by Go runtime. ~4 KB stack initially; grows.
```go
go expensiveCall()              // fire and forget
```

You can spawn millions; the runtime multiplexes onto OS threads.

## Synchronization

### WaitGroup
Wait for N goroutines:
```go
var wg sync.WaitGroup
for _, url := range urls {
    wg.Add(1)
    go func(u string) {
        defer wg.Done()
        process(u)
    }(u)
}
wg.Wait()
```

### Channels (Preferred)
```go
results := make(chan Result, len(urls))
for _, url := range urls {
    go func(u string) {
        results <- fetch(u)
    }(url)
}
for i := 0; i < len(urls); i++ {
    r := <-results
    handle(r)
}
```

### Mutex
For shared state:
```go
var mu sync.Mutex
var counter int

go func() {
    mu.Lock()
    counter++
    mu.Unlock()
}()
```

`sync.RWMutex` if many readers, few writers.

## Worker Pool Pattern

Limit concurrency:
```go
jobs := make(chan Job, 100)
results := make(chan Result, 100)

// Workers
for i := 0; i < 10; i++ {
    go worker(jobs, results)
}

// Submit jobs
for _, j := range allJobs {
    jobs <- j
}
close(jobs)

// Collect
for i := 0; i < len(allJobs); i++ {
    r := <-results
    handle(r)
}

func worker(jobs <-chan Job, results chan<- Result) {
    for j := range jobs {
        results <- process(j)
    }
}
```

Channel directions: `<-chan` recv only, `chan<-` send only.

## Pipeline

```go
func gen(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        for _, n := range nums {
            out <- n
        }
        close(out)
    }()
    return out
}

func square(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        for n := range in {
            out <- n * n
        }
        close(out)
    }()
    return out
}

for r := range square(gen(1, 2, 3, 4)) {
    fmt.Println(r)
}
```

## Select

Wait on multiple channels:
```go
select {
case msg := <-ch1:
    handle(msg)
case msg := <-ch2:
    handle(msg)
case <-time.After(5 * time.Second):
    log.Println("timeout")
case <-ctx.Done():
    return
}
```

`default:` for non-blocking:
```go
select {
case v := <-ch:
    use(v)
default:
    // no value available; don't block
}
```

## Context

Cancellation propagation:
```go
ctx, cancel := context.WithTimeout(ctx, 10*time.Second)
defer cancel()

go func() {
    select {
    case <-ctx.Done():
        return            // parent canceled or timed out
    case <-time.After(1 * time.Hour):
        // ...
    }
}()
```

Pass `ctx` as first arg to any function that might block or call out.

## Common Patterns

### Fan-Out / Fan-In
```go
func fanOut(in <-chan Job, n int) []<-chan Result {
    outs := make([]<-chan Result, n)
    for i := 0; i < n; i++ {
        out := make(chan Result)
        outs[i] = out
        go func() {
            for j := range in {
                out <- process(j)
            }
            close(out)
        }()
    }
    return outs
}

func fanIn(chs ...<-chan Result) <-chan Result {
    out := make(chan Result)
    var wg sync.WaitGroup
    for _, c := range chs {
        wg.Add(1)
        go func(ch <-chan Result) {
            defer wg.Done()
            for r := range ch {
                out <- r
            }
        }(c)
    }
    go func() {
        wg.Wait()
        close(out)
    }()
    return out
}
```

### Rate Limiting
```go
limiter := time.Tick(100 * time.Millisecond)   // 10/sec
for _, req := range requests {
    <-limiter
    go handle(req)
}
```

### Errgroup
Bundle errors across goroutines:
```go
import "golang.org/x/sync/errgroup"

g, ctx := errgroup.WithContext(ctx)
for _, url := range urls {
    u := url
    g.Go(func() error {
        return fetch(ctx, u)
    })
}
if err := g.Wait(); err != nil {
    log.Fatal(err)
}
```

If one returns error, ctx cancels; others abort.

## Race Detection

```bash
go run -race main.go
go test -race ./...
```

Reports data races at runtime; CRITICAL during testing.

## Common Pitfalls

### Loop Variable Capture
```go
// WRONG (pre-Go 1.22)
for _, x := range items {
    go func() {
        process(x)        // x captured by reference!
    }()
}

// RIGHT
for _, x := range items {
    x := x                // shadow
    go func() {
        process(x)
    }()
}

// Or pass as arg
for _, x := range items {
    go func(x T) {
        process(x)
    }(x)
}
```
Go 1.22+ fixes this in language; older code: be careful.

### Goroutine Leak
Goroutine that never exits:
```go
// BAD
go func() {
    v := <-ch          // ch never receives; goroutine stuck
}()
```
Always have an exit path (close channel, context cancel).

### Deadlock
Send/receive mismatch:
```go
ch := make(chan int)
ch <- 1               // BLOCKS forever (no receiver)
```
Use buffered channel or goroutine receiver.

### Double Close
```go
close(ch)
close(ch)             // PANIC
```
Only sender closes. Once.

## When NOT to Use Goroutines

- Sequential work (just call in main)
- Tiny tasks (overhead > benefit)
- Without synchronization plan
- Random parallelism without thinking about resource limits

## Interview Prep

**Mid**: "Goroutine vs OS thread."

**Senior**: "Worker pool implementation."

**Staff**: "Goroutine leak — detect / prevent."

## Next Topic

→ [T04 — Cobra for CLIs](T04-Cobra.md)
