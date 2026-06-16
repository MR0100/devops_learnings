# L04/C05 — Beyond Bash

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-When-To-Move-Beyond.md) | When to Move to Python/Go | 0.5 hr |
| [T02](T02-Makefile.md) | Makefile for Automation | 1 hr |
| [T03](T03-Just-Task-Mage.md) | just, task, mage Alternatives | 0.5 hr |

## When Bash Stops Being the Right Tool

Bash is great for:
- Pipelines of existing CLI tools
- One-off automation
- Quick wrappers
- Up to a few hundred lines

Bash is bad for:
- Complex data structures (no real types)
- JSON/YAML manipulation beyond what jq/yq cover easily
- Anything > 500 lines without strong refactoring
- Cross-platform (Windows)
- Multi-threaded I/O concurrency at scale
- Tests (bats works but limited)

**Switch when**: you find yourself reaching for `eval`, complex regex, multi-level dispatch, or your script grows past ~300 lines and needs maintenance.

| Replace With | When |
|---|---|
| Python | Glue scripts, API integrations, structured data, ML/data |
| Go | CLIs, daemons, controllers, anything distributed binary |
| Rust | Performance-critical, embedded |
| TypeScript / Node | CI scripts for JS ecosystems |

## Makefile

The original task runner. Still essential for C/C++ projects and as a common entry point.

```makefile
.PHONY: help build test clean deploy

IMAGE := myapp
VERSION := $(shell git describe --tags --dirty)
REGISTRY := registry.example.com

help:  ## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build:  ## Build the image
	docker build -t $(REGISTRY)/$(IMAGE):$(VERSION) .

test:  ## Run tests
	go test ./...

push: build  ## Push to registry
	docker push $(REGISTRY)/$(IMAGE):$(VERSION)

deploy: push  ## Deploy
	kubectl set image deployment/$(IMAGE) $(IMAGE)=$(REGISTRY)/$(IMAGE):$(VERSION)

clean:  ## Cleanup
	rm -rf dist/ bin/

.DEFAULT_GOAL := help
```

### Make Concepts

- **Target**: name on the left
- **Prerequisites**: targets that must be built first
- **Recipe**: tab-indented commands

```makefile
output.txt: input.txt
	process < input.txt > output.txt    # tab indent!
```

- `.PHONY` declares targets that aren't files (so they always run)
- `$@` = target name, `$<` = first prerequisite, `$^` = all prerequisites
- `$(VAR)` = variable reference
- `$$` = literal `$`

### Why Make Today
- Cross-platform (UNIX)
- Universal (developers know it)
- Dependency graph (only rebuild what changed)
- Good as a unified entry point: `make test`, `make build`, `make deploy`

### Why NOT Make
- Tab-only indentation (frequent confusion)
- Strange escape rules
- Variable expansion timing surprises
- Limited control flow

## just

A modern make replacement, focused on command running (not build dependencies).

```just
# justfile
default:
    @just --list

build:
    cargo build --release

test:
    cargo test

deploy version:
    kubectl set image deployment/app app=registry/app:{{version}}
```

```bash
just build
just deploy v1.2.3
```

Wins:
- Cleaner syntax (no tabs)
- Real argument passing
- Recipes as Bash by default
- Multiple OSes

## task (Taskfile)

YAML-based, popular in cloud-native.

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
```

```bash
task build
task deploy
```

## mage

Go-based build tool. Write tasks in Go.

```go
//go:build mage

package main

import (
    "github.com/magefile/mage/sh"
)

func Build() error {
    return sh.Run("go", "build", "-o", "bin/app", "./cmd/app")
}

func Test() error {
    return sh.Run("go", "test", "./...")
}
```

```bash
mage build
mage test
```

Wins: real types, real errors, real testing of build scripts.

## Decision

| Tool | When |
|---|---|
| **Bash** | < 100 lines, simple flow |
| **Make** | Universal entry point, build-dep semantics |
| **just** | Modern make replacement, simple command runner |
| **task** | YAML lovers, cloud-native projects |
| **mage** | Go projects, complex build logic |
| **Python script** | Anything needing real data structures |
| **Go binary** | Anything that ships |

## Interview Themes

- "When would you move from bash to Python?"
- "What does make do that bash doesn't?"
- "Compare make and just"
- "Walk through your project's Makefile"
