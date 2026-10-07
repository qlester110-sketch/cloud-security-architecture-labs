# Cloud Security Architecture Labs

Public portfolio projects demonstrating practical cloud, infrastructure, identity, platform, and AI security engineering.

Each lab turns a security control into something you can run and test. A policy is written as code, fed a secure example and an insecure example, and the insecure one has to fail. Everything runs locally with the Python standard library. No cloud account, credentials, or third-party packages are needed.

**Live demo:** [Kubernetes workload checker in the browser](https://qlester110-sketch.github.io/cloud-security-architecture-labs/)

## Start here

If you only have five minutes, look at these two:

1. [Kubernetes security baseline](projects/02-kubernetes-security-baseline/README.md). Paste a Deployment into the live demo and see which hardening controls it fails.
2. [AI ingestion guardrail](projects/04-agentic-ai-security/README.md). A pre-model gate that treats retrieved content as untrusted, records provenance, redacts sensitive values, and quarantines prompt-injection attempts.

## Quick start

Requires Python 3.9 or newer. There is nothing to install.

```bash
git clone https://github.com/qlester110-sketch/cloud-security-architecture-labs.git
cd cloud-security-architecture-labs
python3 -m unittest discover -s tests -v
```

Expected result: `Ran 41 tests` followed by `OK`. The same command runs in GitHub Actions on every push and pull request.

Each project README has its own run commands, sample output, and known limitations.

## Projects

| # | Project | What runs today | Planned next | Tests |
| --- | --- | --- | --- | --- |
| 1 | [Secure multi-cloud landing zone](projects/01-multicloud-landing-zone/README.md) | AWS trust-policy generator for GitHub Actions OIDC, ADR, threat model, control contract | Terraform modules for AWS, Azure, GCP | 5 |
| 2 | [Kubernetes security baseline](projects/02-kubernetes-security-baseline/README.md) | Offline workload checker (13 controls), default-deny NetworkPolicy, browser demo | Native admission policy and kind cluster tests | 6 |
| 3 | [Software supply-chain security](projects/03-software-supply-chain/README.md) | Release gate that evaluates an evidence document against 11 controls | Real SBOM generation, Cosign signing and verification in CI | 6 |
| 4 | [AI ingestion and agentic security lab](projects/04-agentic-ai-security/README.md) | Deterministic ingestion guardrail with provenance, redaction, injection detection | Tool-using agent eval harness | 8 |
| 5 | [Detection as code](projects/05-detection-as-code/README.md) | Five CloudTrail detections over synthetic events, triage runbook | Attack simulation in an isolated account | 9 |

All five are **in progress**. None is yet complete by the evidence standard below. Each project README separates what is implemented from what is planned.

## How the repository is organized

```text
projects/<nn-name>/
  README.md     problem, design, run steps, sample output, limitations
  tools/        the control, written as a small Python CLI
  examples/     synthetic secure and insecure inputs
  docs/         ADRs, threat models, runbooks (where present)
tests/          one unittest module per project, run in CI
docs/           the GitHub Pages site and browser demo
```

The checkers share one convention: exit code `0` means the input passed, and exit code `1` means a finding or a block, so each can be used as a CI gate. The trust-policy generator in project 1 is a generator, not a checker, and exits `0` on success.

## Evidence standard

A lab is complete only when it includes:

- A concise problem statement and intended security outcome.
- An architecture diagram and documented trust boundaries.
- A threat model with assumptions and abuse cases.
- Reproducible infrastructure or configuration code.
- Automated validation in CI.
- A results section with measured coverage, findings, or failure behavior.
- Cleanup instructions and an explicit cost boundary.

## Safety and cost controls

- No production credentials, proprietary employer material, customer data, or internal network details.
- Examples use synthetic identifiers. AWS account `111122223333` is the example account used in AWS documentation.
- Nothing in the current labs creates cloud resources or costs money.
- Future cloud resources default to least privilege, include teardown instructions, and require an explicit opt-in variable for anything billable or destructive.

## Public portfolio boundary

This repository demonstrates reusable engineering patterns, not private business advantage. Public examples use synthetic data and generic workflows. Product research, suppliers, margins, advertising performance, customer information, internal prompts, credentials, and daily operating procedures remain outside this repository.

## Target role alignment

The project sequence closes the most common gaps found across the target-role analysis:

1. Kubernetes and container security.
2. Policy as code and AWS-native guardrails.
3. Software-supply-chain and product-security depth.
4. Public proof of agentic AI security testing.
5. Detection engineering and incident-response automation.

## License

Apache License 2.0. See [LICENSE](LICENSE).
