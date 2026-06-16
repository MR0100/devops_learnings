# L05/C06/T02 — Tools (Bazel, Nx, Turborepo, Pants)

## Learning Objectives

- Compare monorepo build systems
- Choose right tool

## Bazel

Google's open-source build system.

- Polyglot (Go, Java, Python, C++, JS, Rust)
- Hermetic + reproducible builds
- Remote cache + remote execution
- Steep learning curve
- BUILD files everywhere

```python
go_binary(name="myapp", srcs=["main.go"], deps=["//lib:lib"])
```

```bash
bazel build //my/service:myservice
bazel test //...
```

## Buck2 (Meta)

Bazel-like, Rust-based, very fast. Meta's newer system.

## Nx

JS/TS-focused monorepo manager.
- React, Vue, Angular, Node, NestJS
- Computation caching
- Affected: only run changed
- Good DX

```bash
nx run-many --target=test --all
nx affected:test
```

## Turborepo

Vercel's. Lightweight Nx-alternative.
- JS/TS-focused
- Cache build outputs
- Easy setup

```json
// turbo.json
{
  "pipeline": {
    "build": { "dependsOn": ["^build"] },
    "test": {}
  }
}
```

```bash
turbo run build
turbo run test --filter=my-app
```

## Pants

Python-friendly Bazel competitor. Multi-language.

## Comparison

| | Bazel | Buck2 | Nx | Turborepo | Pants |
|---|---|---|---|---|---|
| Languages | Polyglot | Polyglot | JS/TS focused | JS/TS focused | Polyglot |
| Speed | Fast | Fastest | Fast | Fast | Fast |
| Setup | Complex | Complex | Easy | Easy | Medium |
| Remote cache | Yes | Yes | Yes (Nx Cloud) | Yes | Yes |
| Best for | Large polyglot orgs | Same | JS/TS teams | JS/TS teams | Python-heavy |

## Selective Builds

Common pattern: only build/test what changed.

```bash
# Bazel
changed=$(git diff --name-only origin/main...HEAD)
bazel query 'rdeps(//..., set(...))'  # affected targets

# Nx
nx affected:build --base=origin/main

# Turborepo
turbo run build --filter=...[origin/main]
```

Massive CI time savings.

## When Bazel

- 50K+ engineers
- Many languages
- Strong caching/distribution needs
- Capable to maintain BUILD files

## When Lighter Tools

- < 50 engineers
- Single-language stacks (JS, Python)
- Want fast onboarding
- Less ops capacity

## Real Examples

- **Google**: Bazel
- **Meta**: Buck2
- **Shopify**: Nx (for frontends)
- **Vercel**: Turborepo (eat own food)
- **Datadog**: mixed; Bazel for libraries

## Migration Cost

Moving large repo to Bazel: ~6-12 months of platform work.
Moving to Nx/Turborepo: weeks.

## CI Integration

```yaml
- run: nx affected:test --base=$(git merge-base HEAD origin/main)
```

Only runs affected tests. Critical for large monorepos.

## Cache Strategy

Local cache: speeds dev rebuilds.
Remote cache: shares across team / CI.

```
You: make a change
Bazel: builds target X
Builds target Y (untouched) → reads from cache
```

## Common Mistakes

- Under-declaring dependencies (especially in Bazel/Pants), which produces non-hermetic builds and stale cache hits — the build "works on my machine" because it secretly used an undeclared input.
- Treating the remote cache as trustworthy without content-addressing discipline; a poisoned or non-deterministic cache entry silently serves wrong artifacts.
- Reaching for Bazel on a small JS/TS repo where Turborepo or Nx would deliver 90% of the benefit at a fraction of the setup cost.
- Computing "affected" targets from the wrong git base (e.g. against `HEAD~1` on a squash-merge trunk) so CI either rebuilds everything or misses changes.
- Letting `BUILD`/project graph files drift from reality, so the dependency graph the tool uses no longer matches the actual imports.
- Enabling `--aggressive`-style full rebuilds or skipping caching in CI, throwing away the entire reason to adopt these tools.

## Best Practices

- Compute affected targets against the real merge base (`git merge-base origin/main HEAD`) so CI builds exactly what changed and its dependents.
- Make builds hermetic: declare all inputs explicitly and pin toolchains, so remote cache hits are correct and reproducible.
- Enable remote caching shared between CI and developers — the cross-team cache is where most of the speedup comes from.
- Start with the lightest tool that fits the stack (Turborepo/Nx for JS/TS) and graduate to Bazel/Buck2/Pants only when you have polyglot, large-scale, hermeticity needs and the expertise to maintain it.
- Keep the project/dependency graph honest with periodic graph audits or generators so "affected" detection stays accurate.
- Gate CI on per-project tasks (lint/test/build of affected projects) rather than a single monolithic job.

## Quick Refs

```bash
# Determine what changed (feeds "affected" builds)
BASE=$(git merge-base origin/main HEAD)

# Bazel — build/test only what's affected (via query on changed files)
bazel build //...                                  # everything (avoid in CI)
bazel test  $(bazel query "rdeps(//..., set($CHANGED_TARGETS))")
bazel build //services/api:server --remote_cache=grpc://cache:9092

# Nx — affected graph + remote cache (Nx Cloud)
npx nx affected -t build test lint --base=$BASE --head=HEAD
npx nx graph                                       # visualize project graph

# Turborepo — task pipeline + remote cache
npx turbo run build test --filter='...[origin/main]'   # changed + dependents
npx turbo run build --remote-only

# Pants — affected via changed files
pants --changed-since=$BASE --changed-dependents=transitive test
```

| Tool | Best for | Affected flag |
|------|----------|---------------|
| Bazel / Buck2 | huge polyglot, hermetic builds | `bazel query rdeps(...)` |
| Pants | Python/JVM/Go polyglot | `--changed-since` |
| Nx | JS/TS (and beyond) with graph | `nx affected --base` |
| Turborepo | JS/TS task pipelines | `--filter='...[ref]'` |

## Interview Prep

**Mid**: "Why Bazel?"

**Senior**: "Selective CI in monorepo — how?"

**Staff**: "Build system choice for new monorepo."

## Next Topic

→ [T03 — Code Owners & Branch Protection](T03-Code-Owners.md)
