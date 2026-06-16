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
# Modern cosign: keyless is the default; the experimental flag is no longer needed
cosign sign myregistry/myapp:v1
```

Uses OIDC; no long-lived key to manage, rotate, or leak.

GitHub Actions:
```bash
cosign sign --yes myregistry/myapp:v1
# Uses GH OIDC; cert from Fulcio; entry logged to Rekor
```

## Keyless Trust Model (Fulcio + Rekor)

The whole point of keyless is to replace *"trust this public key"* with *"trust this **identity**, attested by an OIDC provider, and proven by a public transparency log."* There is no private key sitting on disk to steal. Here is what actually happens:

1. **Identity via OIDC.** The signer (a human via `cosign login`, or more often a CI job) obtains a short-lived **OIDC token** from an issuer — e.g. GitHub Actions (`https://token.actions.githubusercontent.com`), GitLab, Google, or Microsoft. The token's `subject`/claims encode *who* is signing (a workflow path, a user email, a service account).

2. **Ephemeral key + Fulcio certificate.** Cosign generates a throwaway key pair **in memory**, valid for seconds. It sends the public key plus the OIDC token to **Fulcio**, Sigstore's certificate authority. Fulcio validates the token and issues a **short-lived (~10-minute) X.509 code-signing certificate** that **binds the ephemeral public key to the verified OIDC identity** (the identity goes in the cert's SAN). The private key is used to sign and then discarded — nothing persistent to protect.

3. **Transparency log via Rekor.** The signature, the certificate, and a timestamp are recorded as an entry in **Rekor**, an append-only, tamper-evident (Merkle-tree) public transparency log. This is what makes a *short-lived* certificate usable long after it expires: a verifier doesn't need the cert to still be valid *now*, only proof that the signature existed **while the cert was valid** — Rekor's signed timestamp provides exactly that. It also gives auditors a global, queryable record of every signing event ("did anyone ever sign an image as our release workflow?").

4. **Verification.** At pull/admission time the verifier checks the chain end-to-end: signature → Fulcio cert → Fulcio root (trusted via the Sigstore **TUF** root of trust) **and** that a matching, inclusion-proven entry exists in Rekor **and** that the cert's identity matches the **expected `--certificate-identity[-regexp]` and `--certificate-oidc-issuer`**. All four must hold.

The critical security insight: **a signature alone proves nothing — you must pin the expected identity and issuer.** Without those flags, cosign will happily verify *any* validly-signed image, including one an attacker signed with their *own* legitimate OIDC identity. Identity + issuer is the actual trust anchor; Fulcio and Rekor just make it verifiable without key custody.

## Verify Keyless

```bash
cosign verify \
  --certificate-identity-regexp 'https://github.com/myorg/.*' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
  myregistry/myapp:v1
```

For: pull-time verification. The two `--certificate-*` flags are **mandatory in spirit** — omitting them defeats the entire model (see Common Mistakes).

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

## Verification Failure & Admission Block (Walkthrough)

Signing is only as good as the *enforcement* on the other side. Here is the end-to-end path of a bad deploy getting stopped.

**Scenario:** an attacker (or an honest mistake) pushes `myregistry/myapp:bad` that was never signed by the release workflow, and someone applies a Deployment referencing it.

1. **`kubectl apply`** sends the Pod spec to the API server.
2. The API server fans the request out to **validating admission webhooks**. The Sigstore Policy Controller (or Kyverno) is registered as one and matches `myregistry/**`.
3. The controller resolves each image **to its digest** (tags are mutable — it pins `image@sha256:...` so a TOCTOU tag-swap can't bypass policy) and runs the equivalent of `cosign verify` against the configured authorities: Fulcio cert chain, Rekor inclusion, and the **expected identity + issuer**.
4. For `:bad` there is **no signature / no Rekor entry / identity mismatch**, so verification fails.
5. The webhook returns **`allowed: false`**, and the API server **rejects the whole request** before anything is scheduled.

What the user sees:

```text
$ kubectl apply -f deploy.yaml
Error from server: admission webhook "policy.sigstore.dev" denied the request:
  validation failed: failed to verify signature of myregistry/myapp@sha256:...:
  no matching signatures: none of the expected identities matched what was in the certificate
```

Hands-on with cosign, the same failure modes look like:

```bash
# Never signed
$ cosign verify --certificate-identity-regexp '...' --certificate-oidc-issuer '...' myregistry/myapp:bad
Error: no signatures found for image

# Signed, but by the WRONG identity (attacker's own valid OIDC cert)
$ cosign verify --certificate-identity-regexp 'https://github.com/myorg/.*' \
    --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' myregistry/evil:v1
Error: none of the expected identities matched what was in the certificate
       (got: https://github.com/attacker/repo/.github/workflows/x.yml@refs/heads/main)

# Tampered image (digest changed after signing)
$ cosign verify ... myregistry/myapp:tampered
Error: no matching signatures: invalid signature when validating ASN.1 encoded signature
```

**Rollout safety — fail-open vs fail-closed.** Enforce in stages so a broken policy or an unreachable Fulcio/Rekor doesn't take down every deploy:

- Start the webhook in **`warn`/audit mode** (`failurePolicy: Ignore`) — log violations, admit anyway. Find the unsigned images already in your manifests.
- Scope `ClusterImagePolicy` to a namespace, prove it, then widen.
- Flip to **enforce** (`failurePolicy: Fail`) only once the fleet is clean. Now `failurePolicy: Fail` is the desired behavior: if verification can't be performed, the deploy is **blocked**, not silently admitted.
- Always exempt the controller's own namespace and break-glass paths, or you can wedge the cluster (the policy controller can't start because its own image fails policy).

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
- **Pin identity + issuer on every verify** — never `cosign verify` without `--certificate-identity[-regexp]` and `--certificate-oidc-issuer`
- Verify by **digest**, not tag, at admission time

## Common Mistakes

- **Verifying without pinning identity/issuer.** A bare `cosign verify` (or a policy with no `subjectRegExp`/`issuer`) accepts *any* validly-signed image — an attacker signs with their own legitimate OIDC identity and sails through. This is the #1 keyless footgun.
- **Signing the tag, trusting the tag.** Tags are mutable; sign and verify by `@sha256:` digest or an attacker swaps the tag after verification (TOCTOU).
- **Confusing "signed" with "trustworthy."** A signature proves *who built it*, not that the contents are CVE-free or non-malicious. Pair signing with scanning (T02) and SBOM/provenance attestations.
- **Enforcing fail-closed on day one** with no audit phase, then blocking every legitimate deploy (including the policy controller's own image) and being forced to disable the webhook — losing all enforcement.
- **Leaving Rekor out of verification** (or running fully air-gapped without a private Rekor/TUF mirror), so you lose the transparency-log guarantee that anchors short-lived certs.
- **Mixing up `cosign attest` and `cosign sign`** — an SBOM/provenance *attestation* is signed metadata about the image; it does not by itself satisfy a signature-required policy.
- **Hardcoding a `--key` keypair "for simplicity"** and then having no rotation/revocation story when it leaks — the exact problem keyless was designed to remove.

## Quick Refs

```bash
cosign sign IMAGE                                  # keyless by default
cosign verify --key KEY IMAGE                      # key-based
cosign verify \
  --certificate-identity-regexp REGEX \
  --certificate-oidc-issuer URL IMAGE              # keyless (always pin both)
cosign attest --predicate sbom.json --type spdx IMAGE
cosign verify-attestation --type spdx \
  --certificate-identity-regexp REGEX \
  --certificate-oidc-issuer URL IMAGE
notation sign IMAGE --key mykey                    # Notation / Notary v2
notation verify IMAGE
```

## Interview Prep

**Mid**: "How do you sign and verify a container image, and why bother?"
Sign with `cosign sign` so consumers can prove *provenance* (it came from your pipeline) and *integrity* (it wasn't tampered with). Verify at pull time and, more importantly, at **K8s admission** so unsigned/unknown images can't run. Signing complements — doesn't replace — vulnerability scanning; one proves *who*, the other proves *what*.

**Senior**: "Sigstore (Cosign) vs Notary v2 (Notation) — when would you pick each?"
Both produce OCI-stored signatures, so registry support overlaps. The real difference is the **trust model**:
- **Sigstore/Cosign** centers on **keyless** signing: ephemeral keys, **Fulcio** binds a short-lived cert to an **OIDC identity**, and every signing event lands in the **Rekor** transparency log. You trust *identities and a public log*, not a key you have to guard. It also natively carries **attestations** (SBOM, SLSA provenance) and dominates the cloud-native / CNCF ecosystem. Cost: you depend on Fulcio/Rekor (public Sigstore or self-hosted), and air-gapped setups need a private deployment + TUF mirror.
- **Notary v2 / Notation** is a **PKI/key-and-cert** model — you sign with X.509 keys, typically rooted in **your own CA**, with trust policies you control end-to-end. No external transparency log, no OIDC dependency. That suits **regulated/enterprise/air-gapped** shops that want self-contained PKI and registry-vendor backing (it's the path AWS Signer, Azure, Docker pushed via the OCI Notary v2 effort).
- **Pick Sigstore** for CI-driven, identity-based, low-key-management signing with attestations (the common modern default). **Pick Notation** when you must own the CA, can't take an external-log/OIDC dependency, or are standardizing on a registry vendor's signing story. They're not mutually exclusive — you can store both signature types on the same image.

**Staff**: "Design image signing + enforcement for an org's CI/CD."
Sign **keyless in CI** off the workflow's OIDC identity, attach **SBOM and SLSA provenance attestations**, and pin everything to **digests**. Enforce with an admission controller (**Sigstore Policy Controller** or **Kyverno** `verifyImages`) that pins **expected identity + issuer**, verifies the **Fulcio chain and Rekor inclusion**, and requires the attestations — not just a signature. Roll out **audit → namespace-scoped enforce → fleet-wide fail-closed**, with break-glass exemptions and the policy controller self-exempted. For air-gapped or regulated estates, run **self-hosted Fulcio/Rekor + a TUF mirror**, or use **Notation with an internal CA**. Tie it back to **SLSA** levels: signed provenance from a hardened, isolated builder is what moves you up the chain.

## Next Topic

→ [T04 — Runtime Security (Falco, Tetragon)](T04-Runtime-Security.md)
