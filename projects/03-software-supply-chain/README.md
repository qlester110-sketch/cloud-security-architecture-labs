# Software Supply Chain Security

**Status:** In progress — deterministic release gate, provenance checks, SBOM checks, signature requirement, vulnerability policy, and negative tests complete.

## Goal

Build a secure CI/CD reference pipeline that generates an SBOM, runs SAST and dependency analysis, signs artifacts, emits provenance, and enforces admission policy before deployment.

## Proof to produce

- GitHub Actions workflow with least-privilege permissions and OIDC.
- SAST, SCA, secret scanning, and infrastructure scanning.
- CycloneDX or SPDX SBOM generation.
- Cosign signing and provenance verification.
- A deliberately vulnerable change that the pipeline blocks.

## Resume signal

Adds concrete product-security and DevSecOps evidence for Chainguard, GitLab, GoodLeap, and 1Password-style roles.

## Release contract

A release passes only when it has:

- an immutable SHA-256 artifact digest;
- an SPDX 2.3 SBOM with versioned packages and checksums;
- source and builder provenance tied to a full commit SHA;
- an OIDC-backed build identity;
- a verified artifact signature;
- no critical or high-severity unresolved vulnerabilities.

Run the gate without external dependencies:

```bash
python projects/03-software-supply-chain/tools/release_gate.py \
  projects/03-software-supply-chain/examples/secure-release.json
python -m unittest tests.test_supply_chain -v
```

The insecure fixture intentionally fails several controls to prove that the gate fails closed.
