# ADR-001: Federated CI Identity and Administrative Boundaries

## Status

Accepted

## Decision

GitHub Actions will authenticate to each cloud through OpenID Connect and assume a narrowly scoped deployment identity. Long-lived cloud credentials are prohibited. Separate deployment identities and state boundaries will be used for development, staging, and production.

## Why

Static credentials create rotation, leakage, and attribution risks. Repository, workflow, branch, environment, audience, and subject claims allow each cloud trust policy to constrain who may request a token and what that token may do.

## Guardrails

- Production jobs require protected GitHub environments.
- Pull-request workflows receive read-only validation permissions.
- Trust policies reject unapproved repositories, refs, and audiences.
- Deployment roles cannot modify their own trust policy.
- Break-glass access is human-operated, time-bound, logged, and excluded from CI.

## Consequences

Initial setup requires one trusted administrator in each cloud. After bootstrap, normal deployments avoid stored secrets and produce attributable audit events.
