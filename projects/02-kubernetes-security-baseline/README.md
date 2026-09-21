# Kubernetes Security Baseline

**Status:** In progress — admission controls, secure reference workload, default-deny networking, and automated negative tests complete.

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

## Implemented controls

- Non-root execution and `runAsNonRoot` enforcement.
- Read-only root filesystem.
- Privilege escalation disabled and all Linux capabilities dropped.
- Seccomp `RuntimeDefault` profile.
- CPU and memory requests and limits.
- Immutable image references; `latest` tags are rejected.
- Service-account token automount disabled by default.
- Namespace-level default-deny ingress and egress.

## Run locally

The tests use only Python's standard library, so they run without a cluster:

```bash
python -m unittest tests.test_kubernetes_baseline -v
python projects/02-kubernetes-security-baseline/tools/policy_check.py \
  projects/02-kubernetes-security-baseline/examples/secure-deployment.json
```

The policy logic is intentionally independent of a particular admission controller. The next increment will package the same rules as native Kubernetes `ValidatingAdmissionPolicy` resources and add kind-based integration tests.
