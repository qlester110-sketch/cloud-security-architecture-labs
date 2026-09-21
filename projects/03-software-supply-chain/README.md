# Software Supply Chain Security

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
