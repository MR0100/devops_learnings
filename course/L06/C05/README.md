# L06/C05 — Building Production Tools

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Configuration.md) | Configuration (Env Vars, Files, Secrets) | 1 hr |
| [T02](T02-Observability-Tools.md) | Observability in Your Own Tools | 1 hr |
| [T03](T03-Distribution.md) | Distribution (Homebrew, apt, Docker) | 0.5 hr |
| [T04](T04-Goreleaser.md) | Releasing with GoReleaser | 0.5 hr |

## Configuration Hierarchy

```
Defaults (in code)
   ↑
Config file (~/.config/app/config.yaml)
   ↑
Environment variables (APP_KEY=value)
   ↑
Command-line flags (--key=value)
   ↑
   highest priority
```

Use viper (Go), Pydantic Settings (Python), or roll your own. Order matters; flags override env, env overrides file, file overrides defaults.

### 12-Factor App Config

> Store config in the environment.

- No secrets in code or repo
- No environment-specific code (`if env == 'prod'`)
- Config differs per env via env vars or env-specific files

### Secrets

Never:
- Bake into image
- Commit (even encrypted unless via SOPS-style)
- Pass on command line (visible in `ps`)

Do:
- Mount as files (K8s Secrets, Vault)
- Env vars at runtime (avoid for very high secrecy)
- IAM roles (no static creds)

## Observability in Your Own Tools

Even internal CLIs benefit from:

### Structured Logging
```go
// Go (slog)
import "log/slog"
log := slog.New(slog.NewJSONHandler(os.Stderr, nil))
log.Info("processing", "service", svc, "count", n)
```

```python
# Python (structlog)
import structlog
log = structlog.get_logger()
log.info("processing", service=svc, count=n)
```

### Metrics for Daemons
```go
import "github.com/prometheus/client_golang/prometheus"

reqsTotal := prometheus.NewCounterVec(
    prometheus.CounterOpts{Name: "myapp_requests_total"},
    []string{"method", "status"},
)
prometheus.MustRegister(reqsTotal)
http.Handle("/metrics", promhttp.Handler())
```

### Tracing
```go
import "go.opentelemetry.io/otel"

tracer := otel.Tracer("mytool")
ctx, span := tracer.Start(ctx, "process-item")
defer span.End()
span.SetAttributes(attribute.String("item.id", id))
```

### Useful Flags
```
--verbose, -v       enable debug logging
--log-format       json|text
--metrics-addr     :9090
--profile          enable pprof
--dry-run
--no-color
```

## Distribution

### Homebrew (macOS, Linux)
```bash
# Tap: github.com/me/homebrew-mytool
brew tap me/mytool
brew install mytool
```

Cask formula generates from GoReleaser config.

### apt / yum
- Package as .deb / .rpm
- Self-host with `aptly` / `createrepo`
- Or use Cloudsmith, Artifactory, Bintray-replacement

### Docker
```dockerfile
FROM gcr.io/distroless/static:nonroot
COPY mytool /usr/local/bin/
USER nonroot
ENTRYPOINT ["mytool"]
```

```bash
docker run myorg/mytool --help
```

### One-line installer
```bash
curl -sSfL https://example.com/install.sh | sh
```

(Be a citizen: support `INSTALL_DIR`, `VERSION`, allow dry-run, sign your script.)

### Krew (kubectl plugins)
```bash
kubectl krew install myplugin
```

## GoReleaser

Automates Go release pipeline.

```yaml
# .goreleaser.yml
project_name: mytool

builds:
- env: [CGO_ENABLED=0]
  goos: [linux, darwin, windows]
  goarch: [amd64, arm64]
  ldflags:
  - -s -w
  - -X main.version={{.Version}}

archives:
- format: tar.gz
  format_overrides:
  - goos: windows
    format: zip

checksum:
  name_template: 'checksums.txt'

snapshot:
  name_template: "{{ incpatch .Version }}-next"

changelog:
  sort: asc
  filters:
    exclude:
    - '^docs:'
    - '^test:'

brews:
- repository:
    owner: me
    name: homebrew-mytool

dockers:
- image_templates:
  - "ghcr.io/me/mytool:{{ .Version }}"
  - "ghcr.io/me/mytool:latest"

sboms:
- artifacts: archive

signs:
- cmd: cosign
  args: ["sign-blob", "--yes", "--output-signature=${signature}", "${artifact}"]
  artifacts: all
```

On tag push:
```bash
git tag v1.2.3
git push --tags
# GoReleaser builds binaries for all OS/arch, makes archives, updates Homebrew,
# publishes Docker image, generates SBOM, signs artifacts.
```

## Versioning

Semantic versioning:
- MAJOR.MINOR.PATCH
- Auto-generated from conventional commits via release-please/semantic-release

Embed version in binary:
```go
var version = "dev"   // overridden at build time

func main() {
    if showVersion {
        fmt.Println(version)
    }
}
```

```bash
go build -ldflags "-X main.version=$(git describe --tags --dirty)"
```

## Interview Themes

- "Walk me through how you'd ship an internal CLI"
- "Configuration hierarchy and why it matters"
- "Distribution options for a tool"
- "Why instrument internal tools?"
- "What is GoReleaser and what does it automate?"
