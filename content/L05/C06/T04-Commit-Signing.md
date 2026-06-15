# L05/C06/T04 — Commit Signing (GPG, Sigstore)

## Learning Objectives

- Sign commits with GPG, SSH, or Sigstore
- Verify commits as authentic

## Why Sign

Git commits show author name + email but ANYONE can claim any name. Without signatures, you can't verify a commit came from who it says.

```bash
git -c user.email='ceo@company.com' commit -m "Approved"
# Looks like CEO; not signed; could be anyone
```

Signed commits show "Verified" badge on GitHub/GitLab.

## GPG Signing

### Setup
```bash
# Generate key
gpg --full-generate-key
# Choose RSA 4096; long expiry

# Export public key
gpg --armor --export <KEY-ID>
# Add to GitHub: Settings → SSH and GPG keys → New GPG key

# Configure Git
git config --global user.signingkey <KEY-ID>
git config --global commit.gpgsign true
git config --global tag.gpgsign true
```

### Sign
```bash
git commit -m "Signed commit"
# GPG prompts for passphrase
```

### Verify
```bash
git log --show-signature
# commit abc123 (HEAD -> main)
# gpg: Good signature from "Alice <alice@example.com>"
```

## SSH Signing (Modern)

GPG is complex. SSH signing simpler.

### Setup
```bash
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
git config --global gpg.ssh.allowedSignersFile ~/.ssh/allowed_signers
```

### Allowed Signers File
```
# ~/.ssh/allowed_signers
alice@example.com ssh-ed25519 AAAAC3...
bob@example.com ssh-ed25519 AAAAC3...
```

### GitHub
Settings → SSH and GPG keys → New SSH key → choose "Signing Key" type.

### Sign + Verify
Same commands. Internally uses SSH key.

## Sigstore (Keyless)

Modern. No long-lived keys to manage.

### gitsign
```bash
# Install gitsign
brew install sigstore/tap/gitsign

# Configure
git config --global commit.gpgsign true
git config --global gpg.format x509
git config --global gpg.x509.program gitsign

# Commit — opens browser for OIDC
git commit -m "Keyless signed"
# Sign in via Google/GitHub/etc.
```

### How It Works
1. Sigstore CA (Fulcio) issues short-lived cert tied to OIDC identity
2. Sign commit with cert
3. Log to transparency ledger (Rekor)
4. Cert expires; signature still verifiable via Rekor

### Pros
- No long-lived keys
- Tied to your identity provider
- Auditable via transparency log

### Cons
- Requires online presence at signing
- Less universally supported (yet)

## Required Signed Commits

Branch protection → "Require signed commits" makes unsigned PRs fail.

```yaml
# GitHub
✓ Require signed commits
```

Increases security; ensures no anonymous commits.

## Verification on GitHub

GitHub verifies signatures:
- Green "Verified" badge: signature valid; key registered
- Yellow "Partially verified": signature valid but key not on file
- No badge: unsigned

## Cosign for Beyond Commits

Sigstore's `cosign` signs:
- Container images
- Other artifacts

For commits: `gitsign`. For images: `cosign`. Same trust model (Sigstore).

## Tag Signing

```bash
git tag -s v1.0 -m "Release 1.0"
# Annotated, signed tag
```

For releases especially:
- Verify cryptographically
- Track who released what

```bash
git tag --verify v1.0
```

## Operations

```bash
# Sign all commits in branch (rewrite history)
git rebase --exec 'git commit --amend --no-edit -S' HEAD~10

# Show signature
git show <sha> --show-signature

# Verify all
git log --show-signature
```

## Key Management

### GPG Keys Lifecycle
- Expiry: set ~2 years
- Renew before expiry: extend expiry
- Revoke if compromised
- Sign with master key; use subkeys for daily

### SSH Signing Keys
- Same key for SSH auth + signing usually
- Easier to manage

### Sigstore Keys
- No persistent keys to manage
- Just keep your OIDC accounts secure (MFA)

## Common Mistakes

- Setting up signing but not committing the public key to GitHub
- Lost signing key → can't sign; new key needed
- GPG passphrase forgotten
- Wrong email in Git config vs key

## Org Policy

```
✓ Require signed commits on main
✓ Maintain signers list (allowed_signers for SSH)
✓ Rotate keys yearly
✓ Document recovery process
```

## Supply Chain

Signed commits = first link in supply chain integrity:
- Signed commits → who wrote it
- Signed builds → what built it (SLSA provenance)
- Signed images → did it come from build
- Verify at deploy → only signed images run

## Best Practices

- Prefer SSH signing or Sigstore (keyless, OIDC) for new setups — they avoid GPG key-management pain while still producing verifiable signatures.
- Set `commit.gpgsign true` (and `tag.gpgSign true`) so signing is automatic; an unset default means most commits silently go unsigned.
- Ensure the email in `user.email` exactly matches an identity on the signing key/account, or the host will show "Unverified" despite a valid signature.
- Enforce signing at the boundary that matters: require signed commits via branch protection on `main`, and maintain the `allowed_signers` file for SSH verification.
- Plan key lifecycle up front: set expiry, rotate yearly, keep a documented recovery/revocation process, and store private keys in an agent or hardware token.
- Treat commit signing as the first link in supply-chain integrity (commit → build provenance → image signing → verify-at-deploy), not an isolated checkbox.

## Quick Refs

```bash
# --- SSH signing (modern, simplest) ---
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
# verify others: ~/.ssh/allowed_signers  "email ssh-ed25519 AAAA..."
git config --global gpg.ssh.allowedSignersFile ~/.ssh/allowed_signers

# --- GPG signing ---
git config --global user.signingkey <KEYID>
git config --global commit.gpgsign true
gpg --armor --export <KEYID>        # paste into GitHub → GPG keys

# --- Sigstore / gitsign (keyless, OIDC) ---
git config --global commit.gpgsign true
git config --global gpg.x509.program gitsign
git config --global gpg.format x509

# Sign / verify
git commit -S -m "msg"              # explicit sign (if not default)
git tag -s v1.0 -m "Release"        # signed annotated tag
git log --show-signature -1         # show signature status
git verify-commit <sha>             # verify a commit
git verify-tag v1.0                 # verify a tag
git rebase --exec 'git commit --amend --no-edit -S' <base>  # backfill signatures
```

| Method | Key mgmt | Best for |
|--------|----------|----------|
| SSH | reuse existing SSH key | most teams today |
| GPG | dedicated keypair, rotation | regulated / web-of-trust |
| Sigstore (gitsign) | keyless via OIDC | ephemeral CI, zero key storage |

## Interview Prep

**Junior**: "Why sign commits?"

**Mid**: "Compare GPG, SSH, Sigstore signing."

**Senior**: "Cert rotation for signing keys."

**Staff**: "Supply chain — where signing fits."

## Next Chapter

→ [C07 — Git Hooks & Automation](../C07/README.md)
