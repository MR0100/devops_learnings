# L06/C03/T02 — Modules, Structs, Interfaces, Errors

## Learning Objectives

- Write idiomatic Go basics
- Handle errors the Go way

## Modules

Module = Go's dependency unit. `go.mod`:
```
module github.com/me/mytool

go 1.21

require (
    github.com/spf13/cobra v1.7.0
    k8s.io/client-go v0.28.0
)
```

Init: `go mod init github.com/me/mytool`
Add dep: `go get github.com/spf13/cobra`
Update: `go get -u ./...`
Tidy: `go mod tidy`

## Project Layout

```
mytool/
├── go.mod
├── go.sum
├── cmd/
│   └── mytool/
│       └── main.go
├── internal/                  # private to this module
│   └── parser/
│       └── parser.go
├── pkg/                       # exported (used by other modules)
│   └── api/
│       └── api.go
└── README.md
```

`cmd/` for executables; `internal/` for private code (Go enforces); `pkg/` for shared libraries.

## Variables / Types

```go
var x int = 5
y := 10                  // short, type inferred
const pi = 3.14
var (
    a int = 1
    b string = "hi"
)
```

## Functions

```go
func add(a, b int) int {
    return a + b
}

// Multiple returns
func divmod(a, b int) (int, int) {
    return a / b, a % b
}

// Named returns
func split(s string) (head, tail string) {
    head = s[:1]
    tail = s[1:]
    return
}
```

## Structs

```go
type Server struct {
    Name string
    Port int
}

s := Server{Name: "web", Port: 8080}
fmt.Println(s.Name)
```

Methods:
```go
func (s *Server) Start() error {
    fmt.Printf("starting %s:%d\n", s.Name, s.Port)
    return nil
}

s.Start()
```

`*Server` (pointer receiver) for mutation or efficiency; `Server` (value receiver) for immutable small structs.

## Interfaces

Implicitly satisfied (no `implements` keyword).

```go
type Greeter interface {
    Greet() string
}

type English struct{}
func (e English) Greet() string { return "Hello" }

type Spanish struct{}
func (s Spanish) Greet() string { return "Hola" }

func sayHi(g Greeter) {
    fmt.Println(g.Greet())
}

sayHi(English{})    // Hello
sayHi(Spanish{})    // Hola
```

`io.Reader`, `io.Writer`, `error` are foundational.

## Errors

No exceptions. Errors are values:
```go
file, err := os.Open("config.yaml")
if err != nil {
    return fmt.Errorf("open config: %w", err)
}
defer file.Close()
```

`%w` wraps; `errors.Is`/`errors.As` unwrap:
```go
if errors.Is(err, os.ErrNotExist) {
    // file missing
}
```

Custom errors:
```go
type NotFoundError struct {
    Resource string
}
func (e *NotFoundError) Error() string {
    return fmt.Sprintf("%s not found", e.Resource)
}
```

## Slices / Maps

```go
nums := []int{1, 2, 3}
nums = append(nums, 4)

ages := map[string]int{"alice": 30, "bob": 25}
ages["carol"] = 28
age, ok := ages["dave"]      // ok=false if missing
delete(ages, "alice")

for k, v := range ages {
    fmt.Println(k, v)
}
```

## Goroutines

Cheap concurrency:
```go
go func() {
    fmt.Println("background")
}()

// Need sync to wait
var wg sync.WaitGroup
for i := 0; i < 5; i++ {
    wg.Add(1)
    go func(n int) {
        defer wg.Done()
        fmt.Println(n)
    }(i)
}
wg.Wait()
```

## Channels

Goroutine communication:
```go
ch := make(chan int)
go func() {
    ch <- 42        // send
}()
v := <-ch           // receive
```

Buffered:
```go
ch := make(chan int, 10)
```

Close to signal done:
```go
close(ch)
for v := range ch {
    fmt.Println(v)
}
```

Select for multiple channels:
```go
select {
case v := <-ch1:
    handle(v)
case <-time.After(5 * time.Second):
    log.Println("timeout")
}
```

## Context

Cancellation / deadlines:
```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
resp, err := http.DefaultClient.Do(req)
```

## Defer

Cleanup; runs when function returns:
```go
file, _ := os.Open("x")
defer file.Close()

// At function exit, Close runs (even on panic).
```

## Idiomatic Patterns

```go
// Zero values: types have safe defaults
var s string         // ""
var n int            // 0
var sl []string      // nil; OK to append

// Early returns
func process(x int) error {
    if x < 0 {
        return errors.New("negative")
    }
    if x > 100 {
        return errors.New("too big")
    }
    // Main logic
    return nil
}

// Don't panic in libraries; return errors
```

## Build / Run

```bash
go run main.go              # quick test
go build                    # binary in current dir
go install                  # to $GOPATH/bin
go test ./...               # all tests
go vet ./...                # static check
gofmt -w .                  # format
```

## Common Mistakes

- Ignoring errors (`_ =`)
- Goroutines without sync
- Channel deadlocks
- Pointer vs value receiver confusion
- Mutating slice header in loops

## Best Practices

- Return errors as the last value and handle them immediately with `if err != nil`; wrap with `fmt.Errorf("...: %w", err)` to preserve the chain.
- Accept interfaces, return concrete types; keep interfaces small (one or two methods) and define them where they're consumed.
- Pass a `context.Context` as the first parameter to anything that does I/O, and check `ctx.Err()`/`ctx.Done()`.
- Use `defer` for cleanup (`defer f.Close()`) right after acquiring the resource so it can't be forgotten.
- Be consistent with receivers: pointer receivers for types that mutate or are large; value receivers for small immutable types.
- Keep modules tidy with `go mod tidy`, and let `gofmt`/`goimports` own formatting.

## Quick Refs

```go
// Errors: wrap, check, inspect
if err != nil {
    return fmt.Errorf("load config %q: %w", path, err)
}
var nf *NotFoundError
if errors.As(err, &nf) { ... }      // typed match
if errors.Is(err, os.ErrNotExist) { ... }  // sentinel match

// Small interface, defined at the consumer
type Store interface {
    Get(ctx context.Context, key string) ([]byte, error)
}

// Context with timeout
ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
defer cancel()
```

```bash
go mod init github.com/me/tool   # new module
go mod tidy                       # sync go.mod / go.sum
go build ./...                    # build all packages
go run .                          # compile + run
gofmt -w . && go vet ./...        # format + static checks
```

## Interview Prep

**Mid**: "How errors work in Go."

**Senior**: "Goroutine vs thread."

**Staff**: "Sync.Pool — when?"

## Next Topic

→ [T03 — Concurrency: Goroutines & Channels](T03-Concurrency.md)
