# L06/C03/T07 — Testing Go Code (table tests, mocks, fuzzing)

## Learning Objectives

- Write idiomatic Go tests
- Use table-driven tests
- Mock + fuzz

## Basics

Test file: `*_test.go` next to code.

```go
// adder.go
func Add(a, b int) int { return a + b }
```

```go
// adder_test.go
package adder

import "testing"

func TestAdd(t *testing.T) {
    got := Add(1, 2)
    want := 3
    if got != want {
        t.Errorf("Add(1,2) = %d; want %d", got, want)
    }
}
```

Run:
```bash
go test
go test -v
go test -run TestAdd
go test ./...
```

## Table-Driven Tests (Idiomatic)

```go
func TestAdd(t *testing.T) {
    tests := []struct {
        name    string
        a, b    int
        want    int
    }{
        {"positive", 1, 2, 3},
        {"negative", -1, -2, -3},
        {"zero", 0, 0, 0},
        {"mixed", 5, -3, 2},
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := Add(tt.a, tt.b)
            if got != tt.want {
                t.Errorf("Add(%d,%d) = %d; want %d", tt.a, tt.b, got, tt.want)
            }
        })
    }
}
```

`t.Run` makes subtests; named output; can run individually.

## Assertions

Standard lib has no assert; just `t.Errorf`/`t.Fatalf`. For richer:
```go
import "github.com/stretchr/testify/assert"
import "github.com/stretchr/testify/require"

assert.Equal(t, expected, actual)
assert.NoError(t, err)
require.NoError(t, err)             // halts test on fail
```

Many prefer std lib; testify is divisive.

## Setup / Teardown

```go
func TestMain(m *testing.M) {
    setup()
    code := m.Run()
    teardown()
    os.Exit(code)
}

func TestX(t *testing.T) {
    t.Cleanup(func() {
        // runs after test (like defer but better)
    })
}
```

## Mocking

No built-in framework; common approaches:

### Interface-Based
```go
type DB interface {
    Get(id string) (*User, error)
}

type Service struct {
    db DB
}

func (s *Service) Process(id string) error {
    u, err := s.db.Get(id)
    // ...
}
```

In test:
```go
type fakeDB struct {
    users map[string]*User
}
func (f *fakeDB) Get(id string) (*User, error) {
    return f.users[id], nil
}

svc := &Service{db: &fakeDB{users: map[string]*User{"1": {Name: "alice"}}}}
svc.Process("1")
```

### gomock
```bash
go install github.com/golang/mock/mockgen@latest
mockgen -source=db.go -destination=mocks/db_mock.go
```

In test:
```go
ctrl := gomock.NewController(t)
defer ctrl.Finish()

mockDB := mocks.NewMockDB(ctrl)
mockDB.EXPECT().Get("1").Return(&User{Name: "alice"}, nil)

svc := &Service{db: mockDB}
svc.Process("1")
```

## httptest

Mock HTTP servers:
```go
func TestClient(t *testing.T) {
    server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.Write([]byte(`{"status":"ok"}`))
    }))
    defer server.Close()
    
    client := NewClient(server.URL)
    status, _ := client.GetStatus()
    if status != "ok" {
        t.Errorf("got %s; want ok", status)
    }
}
```

## envtest (for K8s)

```go
testEnv := &envtest.Environment{
    CRDDirectoryPaths: []string{"../config/crd/bases"},
}
cfg, _ := testEnv.Start()
defer testEnv.Stop()
```

Spins up etcd + apiserver locally; controllers can be tested against real API.

## Coverage

```bash
go test -cover
go test -coverprofile=coverage.out
go tool cover -html=coverage.out      # browser view
```

## Benchmarks

```go
func BenchmarkAdd(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Add(1, 2)
    }
}
```

```bash
go test -bench=.
go test -bench=. -benchmem            # alloc info
```

## Fuzzing (Go 1.18+)

```go
func FuzzReverse(f *testing.F) {
    f.Add("hello")               // seed
    f.Add("")
    f.Fuzz(func(t *testing.T, s string) {
        rev := Reverse(s)
        revrev := Reverse(rev)
        if revrev != s {
            t.Errorf("Reverse(Reverse(%q)) = %q", s, revrev)
        }
    })
}
```

```bash
go test -fuzz=FuzzReverse
```

Go generates random inputs; finds crashes.

## Race Detection

```bash
go test -race ./...
```

Reports concurrent access without sync. CRITICAL.

## Parallel Tests

```go
func TestX(t *testing.T) {
    t.Parallel()
    // runs concurrently with other t.Parallel() tests
}
```

Speeds up suite; ensure tests don't share mutable state.

## Examples

```go
func ExampleAdd() {
    fmt.Println(Add(1, 2))
    // Output: 3
}
```

Both documentation (renders in godoc) and test (compares output).

## Test Organization

- Same package (`package mypkg`): full access
- External (`package mypkg_test`): only public API; black-box test
- Mix in same dir; both valid

## Testdata Directory

```
mypkg/
├── handler.go
├── handler_test.go
└── testdata/
    └── sample.json
```

`testdata/` is special: Go tools ignore it.

## CI

```yaml
- name: Test
  run: go test -race -coverprofile=coverage.out ./...
- uses: codecov/codecov-action@v3
```

## Common Mistakes

- No table tests for branching logic
- Tests dependent on order (use `t.Parallel`)
- Missing `t.Helper()` in helper funcs (wrong line on failure)
- Mocking with mocks of mocks (rewrite to interface)
- Long test suite slowing CI

## Interview Prep

**Mid**: "Write a table-driven test."

**Senior**: "Mock vs interface-based."

**Staff**: "Fuzz testing — when?"

## Next Topic

→ Move to [L06/C04 — REST APIs, OpenAPI, gRPC](../C04/README.md)
