# L04/C05/T02 — Makefile for Automation

## Learning Objectives

- Write Makefiles for project automation
- Understand make's dependency model
- Use as a unified entry point

## Basic Makefile

```makefile
.PHONY: help build test clean

help:  ## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build:  ## Build the image
	docker build -t myapp:latest .

test:  ## Run tests
	go test ./...

clean:  ## Cleanup
	rm -rf dist/

.DEFAULT_GOAL := help
```

Run: `make` (shows help), `make build`, `make test`.

## Target Syntax

```makefile
target: prerequisites
	command
	command
```

- Target on its own line
- Recipe lines indented with TAB (not spaces!)
- Prerequisites: targets that must build first

## Tab vs Spaces

The #1 makefile error: recipes must start with TAB. Spaces fail.

```makefile
build:
	echo hi      # TAB before echo
```

## Variables

```makefile
IMAGE := myapp
TAG := $(shell git describe --tags --dirty)
REGISTRY := registry.example.com

build:
	docker build -t $(REGISTRY)/$(IMAGE):$(TAG) .
```

- `:=` simple expansion (evaluated once)
- `=` recursive expansion (evaluated each use; can be slow)
- `?=` only if not set
- `+=` append

## Auto-Variables

In recipes:
- `$@` target name
- `$<` first prerequisite
- `$^` all prerequisites
- `$?` prerequisites newer than target

```makefile
%.gz: %
	gzip -k $<
# Build foo.gz from foo: $< = foo, $@ = foo.gz
```

## Patterns / Wildcards

```makefile
%.o: %.c
	gcc -c $<

SOURCES := $(wildcard src/*.c)
OBJECTS := $(SOURCES:.c=.o)

build: $(OBJECTS)
	gcc -o app $(OBJECTS)
```

## .PHONY

Targets that aren't files:
```makefile
.PHONY: build test clean
```

Without `.PHONY`, `make build` skips if a file named "build" exists.

## File Dependencies

For build systems, make does intelligent rebuilds:
```makefile
output.txt: input.txt processor
	./processor input.txt > output.txt
```

If `input.txt` or `processor` changed → rebuild output.txt. Otherwise skip.

## Conditionals

```makefile
ifeq ($(ENV), prod)
    REPLICAS := 10
else
    REPLICAS := 1
endif

deploy:
	kubectl scale deployment myapp --replicas=$(REPLICAS)
```

## Including Other Makefiles

```makefile
include common.mk
-include optional.mk    # don't error if missing
```

## Self-Documenting Help

The grep+awk pattern at top of file extracts `## ` comments:
```makefile
deploy: ## Deploy to production
	./deploy.sh
```

`make help` shows: `deploy           Deploy to production`.

## Common Targets

```makefile
.PHONY: help install build test lint format clean deploy

install: ## Install deps
	go mod download
	pip install -r requirements.txt

build: ## Build artifact
	go build -o bin/app ./cmd/app

test: ## Run tests
	go test -v ./...

lint: ## Lint code
	golangci-lint run

format: ## Format code
	gofmt -w .

clean: ## Cleanup
	rm -rf bin/ dist/

deploy: build ## Build + deploy
	./deploy.sh
```

## Recursive Make

Subdirs:
```makefile
SUBDIRS := svc-a svc-b svc-c

build:
	for d in $(SUBDIRS); do \
	  $(MAKE) -C $$d build; \
	done
```

Beware: parallel make with sub-makes can be tricky.

## Parallel Make

```bash
make -j 4              # 4 parallel jobs
make -j$(nproc)        # use all cores
```

Only safe if targets are independent.

## Debugging Makefiles

```bash
make -n                 # dry run (show commands without executing)
make -d                 # debug
make --print-data-base  # show all variables and rules
make -p                 # print database; no execution
```

## Production Patterns

### Cross-Platform Cleanup
```makefile
clean:
	@rm -rf bin dist *.tmp
```

Works on Mac/Linux. For Windows: use just / task / nx.

### Set Default Goal
```makefile
.DEFAULT_GOAL := help
```

Without this, `make` uses first target.

### Echo vs Silent
```makefile
build:
	echo "Building..."    # prints command
	@echo "Building..."   # silent
```

`@` suppresses echoing the command.

## When NOT to Use Make

- Not for application logic (use Python/Go)
- Not for complex orchestration (use task/just)
- Not for DAGs (use Airflow/Dagster)

Make is for: simple automation, build pipelines, project entry points.

## Alternatives (Brief)

- **just** — modern make replacement
- **task** — YAML-based
- **mage** — Go-based
- **scripts/** with shell — works too

For most teams: Makefile is the lingua franca for `make build` / `make test`.

## Common Mistakes

- **Indenting recipes with spaces**: recipe lines must begin with a literal TAB; spaces give `*** missing separator`. The #1 Makefile error.
- **Forgetting `.PHONY`**: a target named `test`/`build` is skipped if a file/dir of that name exists; declare command targets phony.
- **Using `=` where `:=` is meant**: recursive `=` re-evaluates `$(shell ...)` on every reference (slow, surprising); `:=` evaluates once.
- **`cd` on its own recipe line**: each line runs in a fresh shell, so the `cd` is lost — chain with `&&` or use `$(MAKE) -C dir`.
- **Assuming `make -j` is always safe**: parallel builds need correct prerequisite ordering; otherwise targets race.
- **Treating Make as a scripting language**: complex conditionals and loops belong in a real script or task runner, not in Make.

## Best Practices

- Declare every non-file target `.PHONY` and set `.DEFAULT_GOAL := help` so a bare `make` is discoverable.
- Add a self-documenting `help` target that greps `## ` comments, so `make help` lists available commands.
- Prefer `:=` for variables, `?=` for overridable defaults, and pass overrides on the command line (`make deploy ENV=prod`).
- Model real file dependencies (`output: input`) when Make is doing builds, so unchanged targets are skipped.
- Use `make -n` to preview commands and `make -p` to inspect the resolved rule database when debugging.
- Keep recipes thin — delegate non-trivial logic to `scripts/*.sh` and call them from the target.

## Quick Refs

```makefile
.PHONY: help build test clean
.DEFAULT_GOAL := help

IMAGE := myapp
TAG   := $(shell git describe --tags --always --dirty)
ENV   ?= dev                  # overridable: make deploy ENV=prod

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
	  awk 'BEGIN{FS=":.*?## "}{printf "  %-12s %s\n", $$1, $$2}'

build: ## Build the image (recipe lines start with a TAB)
	docker build -t $(IMAGE):$(TAG) .

deploy: build ## Build then deploy
	./scripts/deploy.sh $(ENV) $(IMAGE):$(TAG)

clean: ## Remove artifacts
	@rm -rf bin/ dist/
```

```bash
# Automatic variables in recipes
#   $@ target   $< first prereq   $^ all prereqs   $? newer prereqs

make            # runs .DEFAULT_GOAL (help here)
make build
make deploy ENV=prod
make -j"$(nproc)"   # parallel (only if prereqs are correct)

# Debugging
make -n target      # dry-run: print commands, don't execute
make -p             # print the rule/variable database
make --warn-undefined-variables
```

## Interview Prep

**Junior**: "What's a Makefile?"

**Mid**: "Why use TAB vs spaces?"

**Senior**: "Dependency-based vs phony targets."

## Next Topic

→ [T03 — just, task, mage Alternatives](T03-Just-Task-Mage.md)
