# L12/C08 — Container Security

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Rootless.md) | Rootless Containers | 0.5 hr |
| [T02](T02-Image-Scanning.md) | Image Scanning (Trivy, Grype, Snyk) | 1 hr |
| [T03](T03-Image-Signing.md) | Signed Images (Cosign, Notary v2) | 1 hr |
| [T04](T04-Runtime-Security.md) | Runtime Security (Falco, Tetragon) | 1 hr |

## Threat Model

```
Image:
  - Malicious base image
  - CVEs in dependencies
  - Embedded secrets
  - Misconfigured (root, no security context)

Build:
  - Supply chain compromise
  - Build environment exploited
  - Tampered artifacts

Registry:
  - Stolen image (private leak)
  - Image substitution

Runtime:
  - Container escape (kernel CVE)
  - Privilege escalation
  - Lateral movement
  - Data exfiltration
```

Defense in depth across the chain.

## Rootless Containers

Containers running as a non-root user — both inside the container AND on the host.

### Why
- Container escape → unprivileged host user (less damage)
- Defense in depth against kernel CVEs

### Docker Rootless
```bash
dockerd-rootless-setuptool.sh install
systemctl --user start docker
```

Limitations: no privileged ports, no overlay networking, performance hit.

### Podman Rootless (default)
- User namespaces map container UIDs to subordinate UIDs on host
- Containers can use IDs 1-65k inside; mapped to e.g. 100000-165000 on host

## Dockerfile Hardening

```dockerfile
FROM gcr.io/distroless/static-debian12:nonroot
USER nonroot:nonroot                # non-root
# No shell (distroless)
# Read-only root filesystem at runtime
COPY --from=builder /out/app /usr/local/bin/app
ENTRYPOINT ["/usr/local/bin/app"]
```

## Runtime Hardening

```bash
docker run \
  --read-only \                       # no writes to image FS
  --tmpfs /tmp:rw,noexec,nosuid \    # writable but no exec
  --cap-drop ALL \                    # drop all caps
  --cap-add NET_BIND_SERVICE \        # add minimal needed
  --security-opt no-new-privileges \  # block privilege escalation
  --security-opt seccomp=default.json \
  --security-opt apparmor=default \
  --user 10001:10001 \                # non-root UID
  --memory 256m --cpus 0.5 \          # resource limits
  --pids-limit 100 \                  # max processes
  myimage
```

## K8s Equivalent

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 10001
  runAsGroup: 10001
  fsGroup: 10001
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop: ["ALL"]
    add: ["NET_BIND_SERVICE"]
  seccompProfile:
    type: RuntimeDefault
```

## Image Scanning

### Trivy (Aqua, free, great)
```bash
trivy image myimage:tag
trivy image --severity HIGH,CRITICAL --exit-code 1 myimage:tag

# Scan IaC, secrets, K8s manifests
trivy config terraform/
trivy fs --scanners vuln,secret,misconfig .

# In CI
- uses: aquasecurity/trivy-action@master
  with:
    image-ref: myimage:tag
    severity: 'HIGH,CRITICAL'
    exit-code: '1'
```

### Grype
```bash
grype myimage:tag
grype dir:. --fail-on high
```

### Snyk
Commercial; great UX; integrates with GitHub.

### AWS ECR Inspector / GCP / Azure
Cloud-native scanning at registry push.

## What to Do with Findings

| Severity | Action |
|---|---|
| Critical | Block merge; patch immediately |
| High | Block merge unless waivered with timeline |
| Medium | Track; patch within sprint |
| Low | Quarterly review |

Patch fastest via:
- Bumping base image (renovate / dependabot)
- Pinning to security-patched versions
- Rebuilding regularly even if code didn't change

## Image Signing

### Cosign (Sigstore)
```bash
# Sign with keyless (OIDC identity)
COSIGN_EXPERIMENTAL=1 cosign sign --yes ghcr.io/me/app:v1

# Verify
cosign verify \
  --certificate-identity user@example.com \
  --certificate-oidc-issuer https://accounts.google.com \
  ghcr.io/me/app:v1

# Or with a key pair
cosign generate-key-pair
cosign sign --key cosign.key ghcr.io/me/app:v1
cosign verify --key cosign.pub ghcr.io/me/app:v1
```

### Notary v2 / Notation
- OCI spec for signatures
- Multi-vendor support

### K8s Admission Verification
Sigstore Policy Controller, Connaisseur, Kyverno — reject unsigned images.

```yaml
apiVersion: policy.sigstore.dev/v1beta1
kind: ClusterImagePolicy
spec:
  images:
    - glob: "ghcr.io/me/*"
  authorities:
    - keyless:
        identities:
          - issuer: https://token.actions.githubusercontent.com
            subjectRegExp: "^https://github.com/me/.*"
```

## Runtime Security

### Falco (CNCF)
Detects runtime anomalies via syscall monitoring.

Rules:
```yaml
- rule: Shell spawned in container
  desc: A shell was spawned in a container
  condition: container and proc.name in (shell_binaries)
  output: Shell in container (user=%user.name container=%container.name)
  priority: WARNING
```

Outputs: stdout, file, Slack, PagerDuty, webhook.

### Tetragon
eBPF-based; lower overhead; richer events; from Isovalent (Cilium).

### sysdig
Commercial superset; includes Falco.

## Common Container Vulnerabilities

- **Docker socket mounted** (`-v /var/run/docker.sock:...`) — escape to host
- **--privileged** flag — basically root on host
- **Capabilities CAP_SYS_ADMIN** — very dangerous
- **hostPath mounts of /, /etc, /proc** — read/write host state
- **Image with embedded secrets** — leaks on registry pull
- **Old base images** with unpatched CVEs

## Supply Chain (SLSA)

Stages to harden:
1. **Source**: signed commits (gitsign), branch protection, CODEOWNERS
2. **Build**: hosted CI (GitHub Actions OIDC), reproducible builds
3. **Provenance**: in-toto attestations, SLSA 3+
4. **Image**: SBOM, signed (Cosign), scanned (Trivy)
5. **Verify at deploy**: admission policy

## Interview Themes

- "Harden a Dockerfile"
- "What does rootless container give you?"
- "How does Cosign keyless signing work?"
- "Runtime detection — Falco rules"
- "What's SLSA?"
- "Supply chain — what can go wrong?"
