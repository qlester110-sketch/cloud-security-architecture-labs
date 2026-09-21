# Detection As Code

**Status:** In progress — five version-controlled AWS identity and infrastructure detections, synthetic telemetry, automated tests, and a triage runbook complete.

## Goal

Simulate cloud identity and infrastructure attacks in an isolated environment, generate auditable telemetry, detect the behavior with version-controlled rules, and execute documented response runbooks.

## Proof to produce

- Safe attack simulations for credential misuse, privilege escalation, and suspicious network changes.
- Detection rules with unit tests and expected telemetry.
- Alert triage and containment runbooks.
- A tabletop or game-day record.
- Post-incident review with detection coverage, false positives, and time-to-detect measurements.

## Resume signal

Adds detection-engineering, security incident command, and measurable response evidence.

## Implemented detections

- Root-account API activity.
- Console authentication without MFA.
- CloudTrail logging stopped or deleted.
- IAM privilege-policy changes.
- SSH exposed to the internet.

Run the synthetic event set:

```bash
python projects/05-detection-as-code/tools/detect.py \
  projects/05-detection-as-code/examples/events.jsonl
python -m unittest tests.test_detection_as_code -v
```

Each alert contains a stable rule ID, severity, event name, actor, account, region, and event time so the output can feed a case-management workflow.
