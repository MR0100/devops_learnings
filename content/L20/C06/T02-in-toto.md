# L20/C06/T02 — in-toto Attestations

## Learning Objectives

- Use in-toto
- Build chain of trust

## in-toto

Framework for supply chain integrity:
- Layouts (allowed steps)
- Link (signed step output)
- Verify end-to-end

For: cryptographic supply chain.

## Concept

```
Source → Build → Test → Package → Sign → Deploy
   Each step: signed by responsible party
   Layout: defines allowed flow
   Verify: at any point
```

## Layout

```yaml
# Defines:
- steps: which operations
- inspections: post-checks
- public keys: who's allowed
- expiration
```

Signed by project owner.

## Link Metadata

```json
{
  "subject": [...],
  "predicate": {
    "type": "https://in-toto.io/attestation/link/v1",
    "step": "build",
    "products": {...},
    "materials": {...}
  }
}
```

Signed by step performer.

## Compose

Multiple link → end-to-end chain.

Verifier:
- Confirms each step signed
- Confirms allowed flow
- Confirms materials match

## SLSA Provenance = in-toto

SLSA provenance attestation:
- in-toto format
- predicate type: slsaprovenance/v1

For: standard.

## Cosign + in-toto

```bash
cosign attest \
  --predicate provenance.json \
  --type slsaprovenance \
  IMAGE
```

Signs predicate; attaches to image.

## Verify

```bash
cosign verify-attestation \
  --type slsaprovenance \
  --certificate-identity ... \
  IMAGE > attestation.json

jq '.payload' attestation.json | base64 -d | jq '.predicate'
```

Inspect.

## Tools

- in-toto CLI
- Sigstore (Cosign)
- Tekton Chains
- GitHub attestations

## Tekton Chains

Auto-attest TaskRuns:
```yaml
apiVersion: tekton.dev/v1
kind: Task
metadata:
  name: build
  annotations:
    chains.tekton.dev/transparency-upload: "true"
```

Each task: signed attestation.

## Threat: Build Compromise

Attacker compromises builder.

in-toto with hermetic builds + layout:
- Builder must use approved inputs
- Output recorded
- Layout enforces flow

For: detect compromised.

## Pipeline End-to-End

```
Commit (signed by dev)
   ↓ link
Build (signed by builder)
   ↓ link
Test (signed by tester)
   ↓ link
Deploy

Verifier: all signatures valid; flow allowed.
```

## Limitations

- Setup complexity
- Per-step adoption
- Layout management

For: high-security only.

## Layouts in Practice

Project has:
- layout.yaml
- Signed by owner
- Updated rarely

Steps reference layout.

## Adoption

Slowly growing:
- SLSA provenance most common (in-toto under)
- Tekton Chains
- Major OSS projects (sometimes)

## Real Examples

- Datadog uses for builds
- Some federal projects
- Open Source Security Foundation (OpenSSF) work

## Best Practices

- Start with SLSA provenance
- Cosign attestations
- Layout sparingly
- Verify in policy

## Common Mistakes

- in-toto without verification
- Layout never updated
- Skip steps (broken chain)

## Quick Refs

```
in-toto:
  Layout: allowed flow
  Link: signed step
  Verify: chain integrity

SLSA provenance: in-toto with specific predicate
Tools: Cosign, Tekton Chains, in-toto CLI
```

## Interview Prep

**Junior**: "What is in-toto?" — A framework that cryptographically verifies the integrity of a software supply chain by having each step (build, test, package) produce signed attestations about what it consumed and produced.

**Mid**: "What is a layout in in-toto?" — A signed policy that defines the expected steps in the supply chain, who is authorized to perform each, and how the materials/products of one step must match the next, so verification can detect a skipped, reordered, or tampered step.

**Senior**: "How does in-toto relate to SLSA?" — in-toto provides the attestation format and end-to-end link-verification model; SLSA builds on it (the SLSA provenance is an in-toto attestation), with SLSA defining what assurance level the build meets and in-toto defining how the chain is recorded and checked.

**Staff**: "How would you roll out supply-chain attestation across an org?" — Standardize on the in-toto attestation format, have CI emit signed attestations (provenance, SBOM, test results) bound to artifact digests, store them in a transparency log (Rekor), and enforce a verification policy at admission so an artifact missing required attestations from authorized steps cannot deploy.

## Next Topic

→ [T03 — Dependency Pinning & Reproducible Builds](T03-Dependency-Reproducible.md)
