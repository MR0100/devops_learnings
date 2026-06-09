# L15/C03 — Build Systems

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Make-Bazel-Buck.md) | Make, Bazel, Buck2 | 1 hr |
| [T02](T02-Reproducible-Builds.md) | Reproducible Builds | 0.5 hr |
| [T03](T03-Hermetic-Builds.md) | Hermetic Builds | 0.5 hr |

## Build System Spectrum

| | Make | Bazel | Buck2 |
|---|---|---|---|
| Language | Make | Starlark (Python-like) | Starlark |
| Hermetic | No | Yes | Yes |
| Remote cache | Manual | Built-in | Built-in |
| Remote execution | No | Yes | Yes |
| Incremental | File mtime | Content-based | Content-based |
| Multi-language | Yes | Yes | Yes |
| Learning curve | Low | High | High |

## Make

Universal but limited:
- Recompiles based on file timestamps (not content)
- No remote cache
- Easy to write incorrect dependencies

Good for: orchestrating wrapper scripts, simple builds.

## Bazel

Google's open-source build system (formerly Blaze internally).

### Concepts
- **WORKSPACE** — repo root
- **BUILD** files declare targets
- **Rules**: language-specific (rules_go, rules_python, rules_nodejs)
- **Targets**: `//path/to:name`

```python
# my/service/BUILD.bazel
load("@io_bazel_rules_go//go:def.bzl", "go_binary", "go_library", "go_test")

go_library(
    name = "service",
    srcs = ["service.go"],
    importpath = "github.com/myorg/myrepo/my/service",
    deps = ["//common/lib"],
)

go_binary(
    name = "myservice",
    embed = [":service"],
)

go_test(
    name = "service_test",
    srcs = ["service_test.go"],
    embed = [":service"],
)
```

```bash
bazel build //my/service:myservice
bazel test //...
bazel query 'rdeps(//..., //common/lib)'  # what depends on this lib?
```

### Wins
- **Hermetic**: builds only see declared inputs
- **Incremental**: only rebuilds what changed (content-based)
- **Remote cache**: share build outputs across team (huge time saver)
- **Remote execution**: distribute build across cluster
- **Polyglot**: one build tool for the entire monorepo

### Costs
- Steep learning curve
- BUILD files maintained alongside code
- Tools (Gazelle) auto-generate BUILD files for Go

## Buck2 (Meta)

Modern rewrite of Buck. Rust-based, fast.

- Compatible with most Bazel concepts
- Faster CLI
- Better error messages
- Open-sourced 2023

Same use cases as Bazel.

## Selective Builds in Monorepos

```bash
# What changed?
git diff --name-only origin/main...HEAD

# What depends on changed files?
bazel query 'rdeps(//..., set(changed_targets))'

# Build only the affected
bazel build [those targets]
```

CI integration: only build/test affected targets. Saves enormous CI time in large monorepos.

## Reproducible Builds

Building the same source produces byte-identical output.

### Why
- Verify supply chain (independent rebuild proves source matches binary)
- Confidence in compiler/dep determinism
- Debugging "it worked yesterday"

### Challenges
- Timestamps in output files
- Random hash maps order
- Build host info embedded
- Non-deterministic compilers
- Network access during build

### Tools / Languages
- **Go**: highly reproducible with `-trimpath` flag
- **Rust**: reasonably reproducible
- **C/C++**: usually not without effort
- **Nix**: most reproducible Linux build ecosystem
- **Bazel/Buck**: hermetic, with effort, can be reproducible

## Hermetic Builds

Build sees ONLY declared inputs.
- No internet
- No `$HOME`, `/tmp` leakage
- No system tools beyond declared
- Sandbox enforces

Hermetic ≠ reproducible. Hermetic builds tend toward reproducible but not guaranteed.

### Implementation
- Sandbox (chroot, namespaces)
- Mount only declared inputs
- Set deterministic timestamps
- No network

## ccache, sccache

For C/C++/Rust speed without full Bazel:
- Hashed compile inputs
- Cached outputs
- Distributed cache option
- Drop-in replacement for compiler

```bash
export RUSTC_WRAPPER=sccache
cargo build
```

## When to Adopt Bazel

You're in a monorepo with:
- Multiple languages
- 100K+ LoC
- Slow CI from rebuilding everything
- Team large enough to maintain BUILD files
- Capacity for the learning curve

For most teams: standard language build tools + caching is sufficient.

## Interview Themes

- "Bazel vs Make"
- "Hermetic builds — what and why?"
- "Reproducible builds — what blocks reproducibility?"
- "Selective CI builds in monorepo"
- "When Bazel?"
