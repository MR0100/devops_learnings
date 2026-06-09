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

## Interview Prep

**Mid**: "Why Bazel?"

**Senior**: "Selective CI in monorepo — how?"

**Staff**: "Build system choice for new monorepo."

## Next Topic

→ [T03 — Code Owners & Branch Protection](T03-Code-Owners.md)
