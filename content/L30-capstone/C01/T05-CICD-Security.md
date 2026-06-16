# L30/C01/T05 — Security Gates

## Learning Objectives

- Add security
- Demonstrate DevSecOps

## Why Layered Gates (Defense in Depth)

No single scanner catches everything, and a gate you can bypass isn't a control.
The strategy is **defense in depth across the supply chain**: catch source bugs
(SAST), vulnerable dependencies (SCA), bad images (container scan), risky infra
(IaC scan), and leaked secrets — then *prove provenance* by signing every image
and *enforce* it at the cluster with admission control. CI gates give fast
developer feedback; admission control is the gate that still holds even if
someone pushes around CI.

The shift-left/enforce-right split is the key insight for an interview: scanning
in CI is necessary but **not sufficient**, because CI is a control the producer
owns. Signature verification at K8s admission is what protects the cluster from
*any* image that didn't come through your pipeline.

## Gates

### SAST
Code analysis:
- Semgrep
- CodeQL

```yaml
- uses: returntocorp/semgrep-action@v1
```

### SCA
Dependencies:
- Trivy
- Snyk

```yaml
- run: trivy fs --severity HIGH,CRITICAL --exit-code 1 .
```

### Container Scan
- Trivy image
- Cosign sign

```yaml
- run: trivy image --severity HIGH,CRITICAL --exit-code 1 IMAGE
- run: cosign sign --yes IMAGE
```

### IaC Scan
- Checkov

```yaml
- uses: bridgecrewio/checkov-action@v12
  with:
    directory: terraform/
```

### Secret Scan
- Gitleaks

```yaml
- uses: gitleaks/gitleaks-action@v2
```

### Policy
- OPA / Kyverno
- Admission control

```yaml
- run: conftest test --policy policy/ k8s/
```

### Pen Test
Annually (not in CI).

## Workflow

```yaml
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Secrets
        uses: gitleaks/gitleaks-action@v2
      
      - name: SAST
        uses: returntocorp/semgrep-action@v1
      
      - name: SCA
        run: trivy fs .
      
      - name: Build
        run: docker build -t IMAGE .
      
      - name: Container scan
        run: trivy image IMAGE
      
      - name: IaC
        uses: bridgecrewio/checkov-action@v12
      
      - name: Policy
        run: conftest test --policy policy/ k8s/
      
      - name: Sign
        uses: sigstore/cosign-installer@v3
      - run: cosign sign --yes IMAGE
      
      - name: SBOM
        uses: anchore/sbom-action@v0
        with:
          image: IMAGE
```

## Severity Block

```
CRITICAL: block merge
HIGH: block merge
MEDIUM: warn
LOW: info
```

## Allowlist

```yaml
# Trivy
.trivyignore:
CVE-2023-12345  # not exploitable
```

Document why.

## Kubernetes Policy

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
spec:
  rules:
    - name: require-signed
      verifyImages:
      - imageReferences: ["registry/*"]
        attestors:
        - entries:
          - keyless:
              subject: "https://github.com/org/*"
```

## Best Practices

- Multi-layer (SAST + SCA + image + IaC + policy)
- Block critical
- Allowlist with reason
- SBOM published
- Sign images

## Common Mistakes

- One scanner
- No image signing
- No K8s admission
- Critical not blocked

## Acceptance Criteria

- CI fails the build on a planted HIGH/CRITICAL CVE and on a planted secret
- Every image is signed (Cosign, keyless via OIDC) and has an SBOM attached
- Admission control **rejects** an unsigned image and **admits** a signed one
  (demo both — proving the gate, not just configuring it)
- The `.trivyignore` (if any) has a documented reason per CVE

## Quick Refs

```
SAST: Semgrep / CodeQL          SCA:  Trivy / Snyk
Container: Trivy + Cosign       IaC:  Checkov
Secret: Gitleaks                Policy: OPA / Kyverno
SBOM:  Syft / Trivy
Shift-left (CI scan) + enforce-right (admission verify signatures)
```

## Interview Prep

**Junior**: "What kinds of security scanning go in a pipeline?" — SAST scans
your source code, SCA scans your dependencies for known CVEs, container scanning
checks the built image, IaC scanning checks Terraform for misconfigurations, and
secret scanning catches leaked credentials. Critical/High findings block the
merge.

**Mid**: "What does signing images get you that scanning doesn't?" — Scanning
tells you an image *was* clean when CI ran. Signing (Cosign) gives provenance —
a cryptographic statement that *this* image came from *your* pipeline. Paired
with admission control that verifies signatures, the cluster will only run
images you produced, so an attacker can't deploy a malicious image even if they
get registry access.

**Senior**: "Why isn't blocking CVEs in CI enough?" — Because CI is a control the
image producer owns and can be bypassed — someone with cluster access can deploy
an image that never went through your pipeline, or a base image can sprout a new
CVE after the scan. So you enforce at two places: CI for fast feedback during
development, and Kubernetes admission (Kyverno/Sigstore policy controller) to
verify signatures and Pod Security at deploy time. Defense in depth means a gap
in one layer doesn't become a breach. I also keep an `.trivyignore` with a
documented justification per CVE so suppressions are auditable, not silent.

**Staff**: "How do you roll supply-chain security across many teams without
becoming the bottleneck?" — Centralize the *policy*, distribute the *mechanism*.
The scan-sign-SBOM steps live in a reusable workflow / shared action so every
team inherits them by reference, not by copy-paste — fix it once, everyone gets
it. Enforcement (signature verification, PSS) moves to admission so it's
guaranteed regardless of each team's pipeline. Then map it to a framework like
SLSA so "what level are we at" is a concrete conversation with leadership rather
than vibes. The platform team owns the paved road and the admission policy;
teams own their findings. That's how you get fleet-wide guarantees without
reviewing every PR.

## Next Topic

→ Move to [L30/C02 — Project 2: Multi-Region Kubernetes Platform](../C02/README.md)
