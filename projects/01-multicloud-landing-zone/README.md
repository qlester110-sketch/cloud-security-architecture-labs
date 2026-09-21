# Secure Multi Cloud Landing Zone

## Goal

Build a vendor-neutral reference implementation for secure account and project vending across AWS, Azure, and GCP using Terraform, short-lived workload identity, network segmentation, centralized logging, and policy checks.

## Proof to produce

- Architecture diagram with management, identity, logging, networking, and workload boundaries.
- GitHub Actions OIDC federation with no static cloud credentials.
- Reusable Terraform modules and environment promotion gates.
- Policy tests for public exposure, encryption, logging, and least privilege.
- Automated teardown and a documented cost ceiling.

## Resume signal

Demonstrates that enterprise landing-zone and identity patterns can be communicated publicly without exposing proprietary implementation details.
