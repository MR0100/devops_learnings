# L30/C01/T05 — Security Gates

## Learning Objectives

- Add security
- Demonstrate DevSecOps

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

## Quick Refs

```
SAST: Semgrep / CodeQL
SCA:  Trivy / Snyk
Container: Trivy + Cosign
IaC:  Checkov
Secret: Gitleaks
Policy: OPA / Kyverno
SBOM:  Syft / Trivy
```

## Next Topic

→ Move to [L30/C02 — Project 2: Multi-Region Kubernetes Platform](../C02/README.md)
