# L15/C03/T01 — Make, Bazel, Buck2

## Learning Objectives

- Compare build systems
- Choose for scale

## Make

Classic; GNU make:
```makefile
test:
	go test ./...

build: test
	go build -o myapp

deploy: build
	scp myapp prod:/opt/

.PHONY: test build deploy
```

Pros: ubiquitous, simple.
Cons: not incremental at scale, no hermeticity.

## When Make

- Small projects
- Glue layer
- CI entry points (`make test`, `make deploy`)

For: ~always present.

## Bazel

Google's build system; OSS:
- Hermetic (sandboxed builds)
- Parallel
- Cached (local + remote)
- Multi-language
- Deterministic outputs

```python
# BUILD.bazel
go_binary(
    name = "myapp",
    srcs = ["main.go"],
    deps = [":lib"],
)

go_library(
    name = "lib",
    srcs = ["lib.go"],
)
```

```bash
bazel build //myapp:myapp
bazel test //...
```

## Bazel Concepts

- **Targets**: things to build (`//pkg:name`)
- **Rules**: how to build (go_binary, java_library, ...)
- **Workspace**: root with WORKSPACE file
- **Packages**: directories with BUILD.bazel

## Hermetic

Inputs explicitly declared:
- Sources
- Deps
- Toolchain
- Env (limited)

Same inputs → same output. Cacheable.

## Remote Cache

```bash
bazel build --remote_cache=grpc://cache.example.com:8080 //...
```

Build outputs cached centrally. Reused by other devs / CI.

For: massive speedup.

## Remote Execution

```bash
bazel build --remote_executor=grpc://exec.example.com:8080 //...
```

Builds run on remote workers. Distributed.

For: huge codebases.

## When Bazel

- Monorepo
- > 1M LOC
- Multi-language
- Need reproducibility
- Strong build engineering team

For: Google, Stripe, Square, Snap, Uber.

## When Not Bazel

- Small codebase
- Single language
- Team unfamiliar (steep curve)
- Existing tool works

## Buck2

Meta's rewrite of Buck1; OSS:
- Rust-based
- Faster than Bazel for some workloads
- Hermetic
- Compatible with Bazel-style BUCK files

```python
# BUCK
go_binary(
    name = "myapp",
    srcs = ["main.go"],
)
```

```bash
buck2 build //myapp:myapp
```

## Buck2 vs Bazel

| | Buck2 | Bazel |
|---|---|---|
| Origin | Meta | Google |
| Language | Rust | Java |
| Performance | Faster (claimed) | Mature |
| Ecosystem | Growing | Huge |
| Rule authoring | Starlark | Starlark |
| Maturity | New (2023+) | Established |

## Starlark

Subset of Python for build files. Both Bazel and Buck2 use it.

## Pants

Twitter origin; OSS:
- Plugin-based
- Multi-language
- Good for Python

For: Python-heavy monorepos.

## Nx

JS/TS focused:
- Monorepo
- Affected detection
- Caching (cloud)

For: JS/TS monorepos.

## Turborepo

JS monorepo:
- Lightweight
- Caching
- Simpler than Bazel

For: small/medium JS.

## Comparison

| | Make | Bazel | Buck2 | Nx | Turborepo |
|---|---|---|---|---|---|
| Lang | Any | Multi | Multi | JS/TS | JS/TS |
| Scale | Small | Huge | Huge | Medium | Small/Med |
| Learning | Easy | Hard | Hard | Medium | Easy |
| Hermetic | No | Yes | Yes | Partial | Partial |
| Remote cache | No | Yes | Yes | Yes (paid) | Yes (paid) |
| Incremental | Manual | Yes | Yes | Yes | Yes |

## Migration to Bazel

Hard. Steps:
1. Pick small piece
2. Generate BUILD files (gazelle for Go)
3. Test
4. Expand
5. Years for large org

## Gazelle

Generates Bazel BUILD files from Go code:
```bash
gazelle update-repos -from_file=go.mod
gazelle
```

For: Go in Bazel.

## rules_*

Per-language rules:
- rules_go
- rules_python
- rules_rust
- rules_docker
- rules_nodejs

Available; community-maintained.

## Build Graph

Bazel sees entire dep graph.
- Changes: only affected re-build.
- Visualize: `bazel query --output=graph deps(//...)`.

For: efficiency at scale.

## Cost / Benefit

### Cost
- Bazel: huge upfront, ongoing maintenance
- Buck2: similar
- Nx / Turborepo: medium

### Benefit
- 10x faster builds at scale
- Reproducible
- Confidence

For: scale matters; small projects: overkill.

## Real Examples

### Google
Blaze (Bazel internal). Monorepo, billions LOC.

### Meta
Buck → Buck2.

### Stripe / Pinterest / Snap
Bazel adopters.

### Most startups
Make, npm scripts, basic.

## When to Adopt

Signals:
- Build times > 30 min
- Test times huge
- Polyglot codebase
- Multiple teams hitting build issues
- Engineer day mostly waiting

For: scale problem first; tool second.

## Best Practices

- Make for entry points
- Native tool first (npm, mvn, cargo)
- Bazel when scale demands
- Remote cache always (if Bazel)
- Incremental builds
- Test build system itself

## Common Mistakes

- Adopt Bazel for small project
- Hand-write BUILD files when tools exist
- No remote cache (Bazel without it: meh)
- Skip Gazelle / sync tools

## Quick Refs

```bash
# Make
make test
make build

# Bazel
bazel build //...
bazel test //...
bazel query "deps(//app:app)"

# Buck2
buck2 build //...
```

## Interview Prep

**Mid**: "Build system options."

**Senior**: "When Bazel."

**Staff**: "Build at scale."

## Next Topic

→ [T02 — Reproducible Builds](T02-Reproducible-Builds.md)
