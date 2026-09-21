# Threat Model

## Assets

Cloud organization hierarchy, deployment identities, Terraform state, audit logs, network boundaries, and workload data.

## Trust boundaries

1. Contributor workstation to GitHub.
2. GitHub workflow to cloud identity provider.
3. Management plane to workload environments.
4. Workload networks to shared services and the internet.
5. Cloud services to centralized security logging.

## Priority abuse cases

| Abuse case | Preventive control | Detection/evidence |
| --- | --- | --- |
| Forked repository requests a cloud token | Exact OIDC subject and repository claim matching | Denied federation event |
| Pull request attempts production deployment | Protected environment and separate role | Workflow audit log |
| Storage becomes publicly readable | Public-access blocks plus plan policy | CI policy failure |
| Attacker disables logging | Separate logging administration and deny guardrail | Missing-log alert and configuration event |
| Compromised workload moves laterally | Segmentation, least privilege, default deny | Flow and identity logs |
| Broad exception becomes permanent | Required owner and expiration | Scheduled exception test |

## Validation targets

- Unauthorized OIDC claims fail closed.
- Public storage and unrestricted ingress fail CI.
- Missing required metadata fails CI.
- Log-retention settings below the baseline fail CI.
- Teardown removes billable workload resources without deleting retained security evidence.
