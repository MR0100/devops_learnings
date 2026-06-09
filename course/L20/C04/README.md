# L20/C04 — Container & Image Security

## Topics

- **T01 Image Scanning Pipelines** — Trivy, Snyk, Grype in CI
- **T02 Image Signing** — Cosign, Sigstore
- **T03 SBOM** — Bill of Materials
- **T04 Admission Controllers** — Block bad images at deploy

## Image Scanning Pipeline

```
PR  →  Build  →  Scan  →  Sign  →  Push  →  Admission  →  Deploy
                  │                          │
              vuln check           verify sig + policy
```

### CI Example
```yaml
- name: Build
  run: docker buildx build --sbom=true -t $IMAGE:$SHA .

- name: Scan
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: $IMAGE:$SHA
    severity: 'HIGH,CRITICAL'
    exit-code: '1'

- name: Sign
  run: COSIGN_EXPERIMENTAL=1 cosign sign --yes $IMAGE:$SHA

- name: Push
  run: docker push $IMAGE:$SHA
```

## Image Scanning Tools

| | Strengths | Trade-offs |
|---|---|---|
| **Trivy** | Free, fast, good defaults | Less commercial UI |
| **Grype** | Fast, OSS | Smaller team behind |
| **Snyk** | Best UX, reachability | Commercial cost |
| **AWS Inspector** | Native ECR integration | AWS-only |
| **Wiz / Lacework / Prisma** | CSPM + image | Heavy enterprise |

Most teams: Trivy in CI + Snyk or commercial for posture.

## Common Findings

- OS package CVEs (most numerous)
- Language deps CVEs
- Misconfig (running as root, no health check)
- Secrets accidentally baked in
- Out-of-date base images

## Patching Strategy

- **Bump base image regularly** — auto-PR via Renovate/Dependabot
- **Rebuild even without code changes** — pull latest base CVE fixes
- **Track via SBOM** — know what's where
- **Set freshness policy**: image > N days old without rebuild → flag

## SBOM

Generated at build:
```bash
docker buildx build --sbom=true -t myimage --push .
# or
syft myimage -o cyclonedx-json > sbom.json
```

Attached to image as OCI artifact. Used by:
- Vulnerability scanners (match SBOM to CVE DB)
- Audit / compliance evidence
- Incident response (log4shell-style)

## Image Signing (Cosign)

### Keyless via OIDC
```bash
COSIGN_EXPERIMENTAL=1 cosign sign --yes ghcr.io/me/app:v1
```

Signs with your identity (GitHub OIDC, Google, etc.). Sig stored alongside image. Public transparency log (Rekor).

Verify:
```bash
cosign verify \
  --certificate-identity user@example.com \
  --certificate-oidc-issuer https://accounts.google.com \
  ghcr.io/me/app:v1
```

### Keyless via GitHub Actions
```yaml
permissions:
  id-token: write       # for OIDC
  packages: write

- run: cosign sign --yes ghcr.io/me/app:${{ github.sha }}
```

Then verify with workflow identity:
```bash
cosign verify \
  --certificate-identity-regexp '^https://github.com/me/repo/.+@refs/heads/main$' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  ghcr.io/me/app:${{ github.sha }}
```

## Attestations

Beyond signing, attach metadata:
- SBOM (`--type spdx`)
- SLSA provenance (`--type slsaprovenance`)
- Vulnerability scan results
- Custom (test results, etc.)

```bash
cosign attest --predicate sbom.json --type spdx myimage:tag
cosign verify-attestation --type spdx myimage:tag
```

## Admission Controllers

Block bad images at deploy time.

### Sigstore Policy Controller
```yaml
apiVersion: policy.sigstore.dev/v1beta1
kind: ClusterImagePolicy
metadata:
  name: signed-images
spec:
  images:
    - glob: "ghcr.io/me/*"
  authorities:
    - keyless:
        url: https://fulcio.sigstore.dev
        identities:
          - issuer: https://token.actions.githubusercontent.com
            subjectRegExp: "^https://github.com/me/.+"
```

Pods using `ghcr.io/me/*` images must be signed by the GHA OIDC issuer.

### Kyverno
General-purpose K8s policy engine; can enforce signing + other policies:

```yaml
apiVersion: kyverno.io/v2beta1
kind: ClusterPolicy
metadata:
  name: verify-images
spec:
  validationFailureAction: Enforce
  rules:
    - name: check-image-signature
      match:
        any:
          - resources: { kinds: [Pod] }
      verifyImages:
        - imageReferences: ["ghcr.io/me/*"]
          attestors:
            - entries:
                - keyless:
                    subject: "^https://github.com/me/.+"
                    issuer: "https://token.actions.githubusercontent.com"
```

### OPA Gatekeeper
Same general capability; uses Rego.

## Runtime Container Security

### Pod Security Standards
- `privileged` (avoid)
- `baseline` (minimum for prod)
- `restricted` (strongest)

```yaml
metadata:
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### Falco
Runtime detection of anomalies:
- Shell spawned in container
- Sensitive file read
- Outbound to suspicious host
- Privilege escalation attempt

### Tetragon (eBPF, Isovalent)
Lower overhead; richer events; can block (not just detect).

## Image Hygiene Checklist

- [ ] Minimal base image (distroless, alpine, scratch)
- [ ] Non-root user
- [ ] Read-only root filesystem (set in pod spec)
- [ ] No SUID binaries
- [ ] No secrets baked in
- [ ] No unnecessary packages
- [ ] Pinned base image SHA
- [ ] SBOM attached
- [ ] Signed via Cosign
- [ ] Scanned, no HIGH/CRITICAL CVEs
- [ ] HEALTHCHECK defined (or K8s probes)
- [ ] STOPSIGNAL configured
- [ ] EXPOSE accurate

## Interview Themes

- "Image scanning pipeline — design"
- "Cosign keyless — how it works"
- "Sigstore Policy Controller — what does it do?"
- "Pod Security Standards — restricted profile"
- "Patch a deep CVE in a base image — strategy"
