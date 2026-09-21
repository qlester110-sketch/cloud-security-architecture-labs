# Cloud Security Architecture Labs

Public portfolio projects demonstrating practical cloud, infrastructure, identity, platform, and AI security engineering.

These labs are intentionally mapped to recurring requirements across Cloud Security Architect, Staff Infrastructure Security Engineer, Platform Security, IAM, SRE, and AI Security roles. Each project is designed to produce inspectable evidence: architecture decisions, threat models, infrastructure code, automated controls, tests, and measurable results.

## Project roadmap

| Priority | Project | Capability demonstrated | Status |
| --- | --- | --- | --- |
| 1 | [Secure multi-cloud landing zone](projects/01-multicloud-landing-zone/README.md) | Terraform, workload identity, policy as code, network controls | In progress |
| 2 | [Kubernetes security baseline](projects/02-kubernetes-security-baseline/README.md) | Kubernetes, admission policy, workload identity, runtime boundaries | Planned |
| 3 | [Software supply-chain security](projects/03-software-supply-chain/README.md) | SAST, SCA, SBOM, signing, provenance, CI/CD security | Planned |
| 4 | [Agentic AI security lab](projects/04-agentic-ai-security/README.md) | Prompt injection, tool abuse, guardrails, evals, findings | Planned |
| 5 | [Detection as code](projects/05-detection-as-code/README.md) | Cloud attack simulation, detections, runbooks, incident review | Planned |

## Evidence standard

Every completed lab must include:

- A concise problem statement and intended security outcome.
- An architecture diagram and documented trust boundaries.
- A threat model with assumptions and abuse cases.
- Reproducible infrastructure or configuration code.
- Automated validation in CI.
- A results section with measured coverage, findings, or failure behavior.
- Cleanup instructions and an explicit cost boundary.

## Safety and cost controls

- No production credentials, proprietary employer material, customer data, or internal network details.
- Examples use synthetic identifiers and isolated sandbox accounts or local tooling.
- Cloud resources default to least privilege and must include teardown instructions.
- Destructive or billable operations require an explicit opt-in variable.

## Target role alignment

The project sequence closes the most common gaps found across the target-role analysis:

1. Kubernetes and container security.
2. Policy as code and AWS-native guardrails.
3. Software-supply-chain and product-security depth.
4. Public proof of agentic AI security testing.
5. Detection engineering and incident-response automation.

## License

Apache License 2.0. See [LICENSE](LICENSE).
