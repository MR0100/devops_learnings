# L20/C04/T02 — Image Signing (Cosign / Sigstore)

## Learning Objectives

- Sign images
- Verify in deploy

## Why Sign

- Authenticity (who built it)
- Integrity (not tampered)
- Supply chain

For: prevent malicious images.

## Cosign

Sigstore tool:
- Sign + verify
- Keyless (OIDC)
- Or key-based

## Sign with Key

```bash
cosign generate-key-pair
# Outputs: cosign.key (private), cosign.pub (public)

cosign sign --key cosign.key registry/my-app:v1
```

Stores signature in registry (next to image).

## Sign Keyless

```bash
cosign sign --yes registry/my-app:v1
```

OIDC flow (browser):
- Sign in (GitHub, Google, Microsoft)
- Cosign gets short-lived cert
- Signs

For: no key management.

## Verify with Key

```bash
cosign verify --key cosign.pub registry/my-app:v1
```

Output: signature info.

## Verify Keyless

```bash
cosign verify \
  --certificate-identity 'https://github.com/myorg/myrepo/.github/workflows/build.yml@refs/heads/main' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
  registry/my-app:v1
```

For: GitHub Actions identity verified.

## In CI

```yaml
- uses: sigstore/cosign-installer@v3

- name: Build
  run: docker build -t REGISTRY/my-app:${{ github.sha }} .

- name: Push
  run: docker push REGISTRY/my-app:${{ github.sha }}

- name: Sign
  run: cosign sign --yes REGISTRY/my-app:${{ github.sha }}
  env:
    COSIGN_EXPERIMENTAL: 1
```

OIDC: keyless.

## Admission Controller

K8s verifies before deploy:
- Cosigned (signed by trusted)
- Connaisseur
- Kyverno
- OPA Gatekeeper

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: check-image-signature
spec:
  rules:
    - name: verify-signature
      match:
        any:
        - resources:
            kinds:
            - Pod
      verifyImages:
      - imageReferences:
        - "registry/*"
        attestors:
        - entries:
          - keyless:
              issuer: "https://token.actions.githubusercontent.com"
              subject: "https://github.com/myorg/myrepo/.github/workflows/build.yml@refs/heads/main"
```

For: only signed images allowed.

## Attestations

Beyond signing:
- SBOM
- Build provenance
- Scan results

Cosign attest:
```bash
cosign attest --predicate sbom.json --type cyclonedx registry/my-app:v1
```

## In-Toto

Format for attestations:
- Signed metadata
- Build provenance
- Verifiable

For: supply chain proof.

## SLSA Provenance

```bash
# GitHub-managed
- uses: actions/attest-build-provenance@v1
  with:
    subject-path: 'dist/*'
```

Auto-signed; published.

## Verify Provenance

```bash
gh attestation verify dist/artifact --owner myorg
```

For: integrity proof.

## Rekor

Sigstore transparency log:
- Every signature recorded
- Tamper-evident

For: proof of signing time.

## Fulcio

CA for keyless:
- Issues short-lived (10 min) certs
- Tied to OIDC identity

For: no long-term keys.

## Cosign Limitations

- Only supports certain registries (OCI)
- Verification policy adds complexity
- Key rotation if key-based

## Key Management

For key-based:
- Vault
- KMS (AWS / GCP / Azure)
- HSM

For prod: HSM.

## Compared to Notary v2

Notary v2:
- Docker's signing standard
- Different protocol

Cosign more common in K8s.

## Best Practices

- Sign all prod images
- Verify in admission controller
- Keyless (OIDC) preferred
- Attest SBOM + provenance
- Publish public key (key-based)

## Common Mistakes

- Sign only some images
- No verification (sign theater)
- Key in repo (defeated)
- Skip attestations

## Cost

- Cosign: free
- Sigstore: free
- HSM (if used): $$

## Quick Refs

```bash
# Sign
cosign sign --yes IMAGE
cosign sign --key KEY IMAGE

# Verify
cosign verify --certificate-identity ... IMAGE
cosign verify --key KEY.pub IMAGE

# Attest
cosign attest --predicate sbom.json IMAGE

# K8s admission
Kyverno / OPA / Connaisseur
```

## Interview Prep

**Mid**: "Image signing."

**Senior**: "Keyless signing."

**Staff**: "Supply chain via signing."

## Next Topic

→ [T03 — SBOM (CycloneDX, SPDX)](T03-SBOM.md)
