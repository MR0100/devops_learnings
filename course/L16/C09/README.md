# L16/C09 — Drone & Other CI Tools

## Other CI Tools

| Tool | Notes |
|---|---|
| **Drone** | Go-based, lightweight, container-native, easy to self-host. Good for OSS / small teams. |
| **Buildkite** | Hybrid: SaaS UI + your runners. Strong test analytics. |
| **TeamCity** | JetBrains, heavyweight enterprise, mature. |
| **Bamboo** | Atlassian, fading. |
| **Concourse** | Pipeline-as-code (YAML), unique resource/task model, niche. |
| **Woodpecker** | Drone fork; community-driven. |
| **Earthly** | Containerized builds defined like Dockerfiles + Makefiles. |
| **Dagger** | CI as code via language SDK (Go, Python, etc.); runs anywhere. |
| **GoCD** | ThoughtWorks; advanced pipeline graphs. |
| **Codefresh** | K8s-native; GitOps-friendly. |

## Drone

```yaml
# .drone.yml
kind: pipeline
type: docker
name: default

steps:
- name: test
  image: golang:1.22
  commands: [go test ./...]

- name: build
  image: plugins/docker
  settings:
    repo: myorg/myapp
    tags: ["${DRONE_COMMIT_SHA:0:8}"]
    username: { from_secret: docker_user }
    password: { from_secret: docker_token }
  when:
    branch: [main]
```

Simple, container-native. Self-host on K8s or any Docker.

## Buildkite

Hybrid: pipeline definition + UI on Buildkite SaaS; agents run wherever you put them (your AWS, on-prem, etc.).

### Pros
- You control the build environment (security + speed)
- Strong test analytics (flake detection, slow test reports)
- Massive parallelism support

### Cons
- Paid only
- Agent ops on you

## Dagger

```go
// CI as Go code
import "dagger.io/dagger"

func test(ctx context.Context, client *dagger.Client) error {
  return client.Container().
    From("golang:1.22").
    WithDirectory("/src", client.Host().Directory(".")).
    WithWorkdir("/src").
    WithExec([]string{"go", "test", "./..."}).
    Sync(ctx)
}
```

Run anywhere (locally, in any CI). Composable. Reproducible.

## Choosing

For most teams in 2025:
- **GitHub Actions** if on GitHub
- **GitLab CI** if on GitLab
- **ArgoCD/Flux** for K8s CD
- **Tekton** if you want K8s-native CI
- **Buildkite** if you need self-managed agents with hosted UI
- **Drone** if you want simple self-hosted

The "best" depends on your stack and team size. **Don't over-engineer.**

## Interview Themes

- "Choose a CI for X scenario"
- "Buildkite hybrid model — why?"
- "Dagger — what does it solve?"
- "Drone — when?"
