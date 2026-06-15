# L15/C01 — CI/CD Concepts

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Continuous-Integration.md) | Continuous Integration | 0.5 hr |
| [T02](T02-CD-vs-Deploy.md) | Continuous Delivery vs Continuous Deployment | 0.5 hr |
| [T03](T03-Deployment-Pipeline.md) | The Deployment Pipeline (Humble & Farley) | 1 hr |

## Continuous Integration

> Every commit is built, tested, and integrated with mainline at least daily.

Originated with eXtreme Programming (Kent Beck). Core idea: merge often to avoid integration hell.

### Practices
- Commit at least daily to mainline
- Every commit triggers an automated build
- Every commit triggers automated tests
- Keep the build green
- Fix broken builds immediately (whole team's priority)
- Run tests in the build environment, not just locally

### Anti-Patterns
- Long-lived feature branches (1 week+)
- "Tests pass on my machine"
- Ignored CI failures
- Manual integration phase

## Continuous Delivery vs Continuous Deployment

| | Continuous Delivery | Continuous Deployment |
|---|---|---|
| Every change is | Releasable | Released |
| Production deploy | Manual button click | Automated |
| Reversibility | Required | Required |
| Adoption | Common at high-performing | Less common; requires very high confidence |

Most "elite" teams practice continuous delivery; some go to continuous deployment for trusted services.

## The Deployment Pipeline

From Humble & Farley's *Continuous Delivery* (2010):

```
Commit
  ↓
Commit Stage         (build, unit tests, static analysis) — < 5 min
  ↓
Auto Acceptance      (integration tests, contract tests) — < 30 min
  ↓
Manual Acceptance    (QA, exploratory)
  ↓
Manual Release       (approval gate; if continuous deploy, no gate)
  ↓
Production
```

### Key Principles
- **Build once, deploy many times**: same artifact promoted through environments
- **Each stage gates the next**
- **Visibility**: pipeline state public
- **Fast feedback at each stage**

## Pipeline Patterns

### Linear
```
Build → Test → Stage → Prod
```

### Fan-Out / Fan-In
```
              ┌── Unit tests ──┐
Build →      │── Lint ──────  │ → Deploy
              ├── Integration ┤
              └── Security ───┘
```

Parallelism reduces wall time.

### Multi-Branch
PR builds + main builds + release builds, all from same pipeline definition.

## Build Once, Deploy Many

Artifact created once on commit; same artifact deployed to dev → staging → prod.

```
Build → my-app:abc123 → push to registry
Deploy to dev → my-app:abc123
Deploy to staging → my-app:abc123
Deploy to prod → my-app:abc123
```

If you rebuild for prod, you might build different code (dependency changes, etc.). Don't.

## Pipeline as Code

Pipeline definition in version control (not configured via UI).

- `.github/workflows/*.yml`
- `.gitlab-ci.yml`
- `Jenkinsfile`
- `tekton/`

Benefits: review, history, branchable.

## Trunk-Based Development + CI/CD

The DORA-correlated practice:
- Commit to trunk many times per day
- Short-lived branches (<1 day)
- Feature flags hide incomplete work
- CI on every commit
- Deploy frequently from trunk

This is the foundation of high-performing teams.

## Interview Themes

- "Difference between continuous delivery and deployment"
- "What's the deployment pipeline?"
- "Why build once, deploy many?"
- "Trunk-based dev — why?"
- "What gates do you put in your pipeline?"
