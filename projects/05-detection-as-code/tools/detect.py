#!/usr/bin/env python3
"""Evaluate synthetic AWS CloudTrail events with version-controlled detections."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

IAM_CHANGES = {"AttachUserPolicy", "AttachRolePolicy", "PutUserPolicy", "PutRolePolicy", "CreatePolicyVersion", "SetDefaultPolicyVersion"}


def detect(event: dict) -> list[dict]:
    alerts = []
    name = event.get("eventName", "unknown")
    identity = event.get("userIdentity", {})
    actor = identity.get("arn") or identity.get("principalId") or "unknown"

    def add(rule_id, severity, title):
        alerts.append({"rule_id": rule_id, "severity": severity, "title": title, "event_name": name, "actor": actor, "account": event.get("recipientAccountId", "unknown"), "region": event.get("awsRegion", "unknown"), "event_time": event.get("eventTime", "unknown")})

    if identity.get("type") == "Root":
        add("AWS-IAM-001", "critical", "Root account activity detected")
    login_result = event.get("responseElements", {}).get("ConsoleLogin")
    login_failed = login_result == "Failure" or bool(event.get("errorMessage"))
    if name == "ConsoleLogin" and not login_failed and event.get("additionalEventData", {}).get("MFAUsed") != "Yes":
        add("AWS-IAM-002", "high", "Console login completed without MFA")
    if name in {"StopLogging", "DeleteTrail", "UpdateTrail"}:
        add("AWS-LOG-001", "critical", "CloudTrail logging configuration changed")
    if name in IAM_CHANGES:
        add("AWS-IAM-003", "high", "IAM privilege policy changed")
    params = event.get("requestParameters", {})
    permissions = params.get("ipPermissions", {}).get("items", [])
    if not permissions:
        permissions = [params]
    ssh_exposed = False
    for permission in permissions:
        start = permission.get("fromPort")
        end = permission.get("toPort", start)
        includes_ssh = isinstance(start, int) and isinstance(end, int) and start <= 22 <= end
        ipv4_ranges = {permission.get("cidrIp")}
        ipv4_ranges.update(item.get("cidrIp") for item in permission.get("ipRanges", {}).get("items", []))
        ipv6_ranges = {permission.get("cidrIpv6")}
        ipv6_ranges.update(item.get("cidrIpv6") for item in permission.get("ipv6Ranges", {}).get("items", []))
        if includes_ssh and ("0.0.0.0/0" in ipv4_ranges or "::/0" in ipv6_ranges):
            ssh_exposed = True
            break
    if name == "AuthorizeSecurityGroupIngress" and ssh_exposed:
        add("AWS-NET-001", "high", "SSH exposed to the internet")
    return alerts


def load_events(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("events", type=Path)
    args = parser.parse_args()
    alerts = [alert for event in load_events(args.events) for alert in detect(event)]
    print(json.dumps(alerts, indent=2))
    return 1 if alerts else 0


if __name__ == "__main__":
    raise SystemExit(main())
