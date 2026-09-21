# AWS High-Severity Alert Triage

## First 15 minutes

1. Preserve the original event and record the rule ID, account, region, actor, source address, and event time.
2. Confirm whether the action was expected through a change record or approved automation identity.
3. If unauthorized activity is plausible, disable or isolate the affected identity without deleting evidence.
4. Protect logging. Re-enable the trail or compensating telemetry through a known-good administrative path.
5. Search the actor, session, source address, and affected resource across the surrounding event window.

## Containment by alert

- **Root activity:** contact the account owner, invalidate active sessions, rotate root credentials, confirm MFA, and review every action in the session.
- **Login without MFA:** disable the identity, revoke sessions, reset credentials, require MFA, and inspect subsequent API activity.
- **Logging changed:** restore the approved trail configuration and compare configuration history for other disabled controls.
- **IAM privilege change:** detach the unauthorized policy or restore the prior version after preserving evidence; enumerate credentials created by the actor.
- **Internet-exposed SSH:** revoke the rule, identify exposed instances, review connection telemetry, and rotate affected credentials if access occurred.

## Closure evidence

Document timeline, scope, containment action, root cause, affected resources, detection gaps, false-positive assessment, and a named owner and due date for every corrective action.
