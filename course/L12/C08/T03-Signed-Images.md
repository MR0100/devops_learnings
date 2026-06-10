# L12/C08/T03 — Signed Images (Cosign, Notary v2)

## Learning Objectives

- Sign container images
- Verify signatures

## Why Sign

- Verify image provenance
- Detect tampering
- Supply chain trust
- Compliance (SLSA)

## Cosign (Sigstore)

```bash
brew install cosign
cosign sign myregistry/myapp:v1
cosign verify --key cosign.pub myregistry/myapp:v1
```

Sigstore-based; keyless option.

## Keyless Signing

```bash
COSIGN_EXPERIMENTAL=1 cosign sign myregistry/myapp:v1
```

Uses OIDC; no key management.

GitHub Actions:
```bash
cosign sign --yes myregistry/myapp:v1
# Uses GH OIDC; cert from Fulcio; logged to Rekor
```

## Verify Keyless

```bash
cosign verify \
  --certificate-identity-regexp 'https://github.com/myorg/.*' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
  myregistry/myapp:v1
```

For: pull-time verification.

## Notary v2

OCI signature format. Adopted by many registries.

```bash
notation sign myregistry/myapp:v1 --key mykey
notation verify myregistry/myapp:v1
```

## K8s Policy

Sigstore Policy Controller:
```yaml
apiVersion: policy.sigstore.dev/v1beta1
kind: ClusterImagePolicy
spec:
  images:
  - glob: "myregistry/**"
  authorities:
  - keyless:
      url: https://fulcio.sigstore.dev
      identities:
      - issuer: https://token.actions.githubusercontent.com
        subjectRegExp: .*github.com/myorg/.*
```

Unsigned → blocked.

## Kyverno
```yaml
- name: verify-images
  match: ...
  verifyImages:
  - imageReferences: ["myregistry/*"]
    attestors:
    - entries:
      - keyless:
          subject: 'https://github.com/myorg/.*'
          issuer: 'https://token.actions.githubusercontent.com'
```

## CI Sign

```yaml
- uses: sigstore/cosign-installer@v3
- run: |
    cosign sign --yes myregistry/myapp:${{ github.sha }}
    cosign attest --predicate sbom.json --type spdx myregistry/myapp:${{ github.sha }}
```

For: every image signed.

## Rekor Log

Public transparency log:
- Signatures recorded
- Verifiable
- Append-only

For: audit + forensics.

## Best Practices

- Sign every prod image
- Keyless (no key mgmt)
- Verify in K8s admission
- Block unsigned (gradual rollout)
- SBOM + provenance attestations

## Quick Refs

```bash
cosign sign IMAGE
cosign verify --key KEY IMAGE
cosign verify --certificate-identity-regexp REGEX --certificate-oidc-issuer URL IMAGE
notation sign IMAGE
```

## Interview Prep

**Mid**: "Image signing."

**Senior**: "Sigstore vs Notary."

**Staff**: "Signing in CI/CD."

## Next Topic

→ [T04 — Runtime Security (Falco, Tetragon)](T04-Runtime-Security.md)
