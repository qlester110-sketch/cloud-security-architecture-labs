# Detection As Code

**Status:** In progress. Five AWS CloudTrail detections, a synthetic event file, six tests, and a triage runbook are working. Attack simulation in a real account and time-to-detect measurement are not built yet.

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

Run the synthetic event set from the repository root, with Python 3.9 or newer and no dependencies:

```bash
python3 -m unittest tests.test_detection_as_code -v
python3 projects/05-detection-as-code/tools/detect.py \
  projects/05-detection-as-code/examples/events.jsonl
```

Each alert contains a stable rule ID, severity, event name, actor, account, region, and event time so the output can feed a case-management workflow. The CLI exits with code 1 when any alert fires, so it can fail a pipeline.

## Sample output

Captured from a clean clone on 5 Oct 2026. The four synthetic events produce three alerts. The benign `ListBuckets` event produces none. Account `111122223333` is the example account used in AWS documentation. First alert shown:

```json
{
  "rule_id": "AWS-LOG-001",
  "severity": "critical",
  "title": "CloudTrail logging configuration changed",
  "event_name": "StopLogging",
  "actor": "arn:aws:iam::111122223333:user/synthetic-attacker",
  "account": "111122223333",
  "region": "us-east-1",
  "event_time": "2026-09-21T12:01:00Z"
}
```

The other two are `AWS-IAM-002` (console login without MFA) and `AWS-NET-001` (SSH opened to the internet).

## Known limitations

- Rules match single events. There is no correlation across events or time windows.
- A root-account console login does not alert. The root rule excludes `ConsoleLogin`, and the MFA rule only fires when MFA was not used.
- AWS-IAM-002 does not check whether the login succeeded, so a failed login without MFA is labelled "succeeded".
- AWS-NET-001 only matches `fromPort` exactly 22 on `0.0.0.0/0`. A port range that includes 22, such as 0 to 65535, and IPv6 `::/0` are missed.
- The events are hand-written synthetic samples, not exported from a live trail.
