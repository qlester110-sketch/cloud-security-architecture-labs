#!/usr/bin/env python3
"""Evaluate a Kubernetes Deployment against the portfolio security baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def violations(workload: dict) -> list[str]:
    pod = workload.get("spec", {}).get("template", {}).get("spec", {})
    findings: list[str] = []

    if pod.get("automountServiceAccountToken", True):
        findings.append("K8S-001 service-account token automount must be disabled")

    pod_sc = pod.get("securityContext", {})
    if pod_sc.get("runAsNonRoot") is not True:
        findings.append("K8S-002 pod must require non-root execution")
    if pod_sc.get("seccompProfile", {}).get("type") != "RuntimeDefault":
        findings.append("K8S-003 pod must use RuntimeDefault seccomp")

    containers = pod.get("containers", [])
    if not containers:
        findings.append("K8S-004 workload must define at least one container")

    for container in containers:
        name = container.get("name", "<unnamed>")
        image = container.get("image", "")
        sc = container.get("securityContext", {})
        resources = container.get("resources", {})
        dropped = sc.get("capabilities", {}).get("drop", [])

        if not image or image.endswith(":latest") or ":" not in image:
            findings.append(f"K8S-005 {name} must use an explicit non-latest image tag")
        if sc.get("allowPrivilegeEscalation") is not False:
            findings.append(f"K8S-006 {name} must disable privilege escalation")
        if sc.get("readOnlyRootFilesystem") is not True:
            findings.append(f"K8S-007 {name} must use a read-only root filesystem")
        if "ALL" not in dropped:
            findings.append(f"K8S-008 {name} must drop all Linux capabilities")
        if not resources.get("requests") or not resources.get("limits"):
            findings.append(f"K8S-009 {name} must declare resource requests and limits")

    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    findings = violations(json.loads(args.manifest.read_text()))
    if findings:
        print("\n".join(findings))
        return 1
    print("PASS: workload satisfies the Kubernetes security baseline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
