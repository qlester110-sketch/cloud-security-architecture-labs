# Kubernetes Security Baseline

## Goal

Create a reproducible Kubernetes security baseline covering workload identity, RBAC, network policies, pod-security controls, secrets handling, admission policy, audit logging, and observability.

## Proof to produce

- Local kind or k3d deployment plus an optional managed-cluster path.
- Kyverno or OPA Gatekeeper policies with positive and negative tests.
- Default-deny network policy and controlled egress.
- Signed images and admission verification.
- Prometheus/Grafana SLOs and a controlled failure exercise.

## Resume signal

Closes the most common gap across platform-security, infrastructure-security, and SRE roles.
