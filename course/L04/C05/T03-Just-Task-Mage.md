# L04/C05/T03 — just, task, mage Alternatives

## Learning Objectives

- Compare Make alternatives
- Choose right tool

## just

Modern Make replacement focused on running commands.

```just
# justfile
default:
    @just --list

build:
    cargo build --release

test:
    cargo test

deploy VERSION:
    kubectl set image deployment/app app=registry/app:{{VERSION}}
```

```bash
just build
just deploy v1.2.3
```

### Strengths
- Cleaner syntax (no tab issues)
- Real argument passing
- Better error messages
- Recipes are real shell scripts
- Cross-platform

### Install
```bash
brew install just
cargo install just
```

## task (Taskfile)

YAML-based. Popular in cloud-native.

```yaml
# Taskfile.yml
version: '3'

tasks:
  build:
    cmds:
      - go build -o bin/app ./cmd/app
    sources:
      - "**/*.go"
    generates:
      - bin/app

  test:
    cmds:
      - go test ./...

  deploy:
    deps: [build]
    cmds:
      - ./scripts/deploy.sh
    vars:
      VERSION:
        sh: git describe --tags
```

```bash
task build
task deploy
```

### Strengths
- YAML (familiar)
- Built-in caching (sources/generates)
- Variables + templating
- Cross-platform

## mage

Go-based. Write tasks in Go.

```go
//go:build mage

package main

import "github.com/magefile/mage/sh"

func Build() error {
    return sh.Run("go", "build", "-o", "bin/app", "./cmd/app")
}

func Test() error {
    return sh.Run("go", "test", "./...")
}

func Deploy() error {
    if err := Build(); err != nil {
        return err
    }
    return sh.Run("./deploy.sh")
}
```

```bash
mage build
mage test
mage deploy
```

### Strengths
- Real Go (types, errors, testing)
- Strong for complex build logic
- Native cross-platform

### Weaknesses
- Need Go installed
- Heavier than just/task for simple cases

## scripts/

Sometimes the simplest:
```
scripts/
├── build.sh
├── test.sh
└── deploy.sh
```

```bash
./scripts/build.sh
./scripts/deploy.sh
```

Pros: zero deps, easy to grep. Cons: no caching, no DAG.

## Comparison

| | Make | just | task | mage |
|---|---|---|---|---|
| Language | Make DSL | just DSL | YAML | Go |
| Args | Awkward | Native | Native | Native |
| Cross-platform | Linux/Mac | Yes | Yes | Yes |
| Caching | File-based | No | Yes (sources) | DIY |
| DAG / deps | Yes | Yes | Yes | Yes |
| Setup | None | install just | install task | install mage + Go |
| Famous use | C/C++ | Modern projects | Cloud-native | Hugo, k0s |

## Choosing

### Use Make when
- Universal entry point needed (`make build` everyone knows)
- Build dependency semantics matter
- Cross-platform isn't a concern (Linux/Mac)

### Use just when
- Modern projects starting fresh
- Want clean syntax + args
- Don't need build-system features

### Use task when
- YAML lovers
- Cloud-native projects (similar feel to K8s)
- Want caching out of box

### Use mage when
- Go project; want type-safe build logic
- Complex orchestration

### Use scripts/ when
- Minimal deps
- Each script is self-contained
- Team prefers shell

## Example Migration: Make → just

Before:
```makefile
.PHONY: build deploy

VERSION := $(shell git describe --tags)
IMAGE := myapp

build:
	docker build -t $(IMAGE):$(VERSION) .

deploy: build
	kubectl set image deployment/app app=$(IMAGE):$(VERSION)
```

After (justfile):
```just
version := `git describe --tags`
image := "myapp"

build:
    docker build -t {{image}}:{{version}} .

deploy: build
    kubectl set image deployment/app app={{image}}:{{version}}
```

Cleaner; no tab issues.

## Real World

Most modern Go projects: mage or task.
Most modern Rust/JS projects: just.
Most legacy/universal: Make.

Don't get religious. Pick what's clean for your team.

## Convenience Wrappers

Some teams use a "metascript" that delegates:
```bash
#!/usr/bin/env bash
# bin/m  (call from anywhere)
case "$1" in
    build) docker build ... ;;
    test) ... ;;
esac
```

Sometimes simpler than any "task runner."

## Interview Prep

**Mid**: "just vs Make."

**Senior**: "task — what's its caching model?"

**Staff**: "Pick a task runner for a 10-team org."

## End of L04

Next lecture: Version Control with Git.

## Next Lecture

→ [L05 — Version Control & Git Internals](../../L05/README.md)
