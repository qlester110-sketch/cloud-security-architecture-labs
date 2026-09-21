#!/usr/bin/env python3
"""Fail-closed policy gate for software release evidence."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SHA256 = re.compile(r"^[a-f0-9]{64}$")
COMMIT_SHA = re.compile(r"^[a-f0-9]{40}$")


def findings(release: dict) -> list[str]:
    issues: list[str] = []
    artifact = release.get("artifact", {})
    sbom = release.get("sbom", {})
    provenance = release.get("provenance", {})
    vulnerabilities = release.get("vulnerabilities", {})

    if not SHA256.fullmatch(artifact.get("sha256", "")):
        issues.append("SC-001 artifact requires an immutable SHA-256 digest")
    if release.get("signature", {}).get("verified") is not True:
        issues.append("SC-002 artifact signature must be verified")
    if sbom.get("format") != "SPDX-2.3":
        issues.append("SC-003 release requires an SPDX 2.3 SBOM")
    packages = sbom.get("packages", [])
    if not packages:
        issues.append("SC-004 SBOM must contain packages")
    for package in packages:
        if not package.get("name") or not package.get("version"):
            issues.append("SC-005 every package requires name and version")
        if not SHA256.fullmatch(package.get("sha256", "")):
            issues.append("SC-006 every package requires a SHA-256 checksum")
    if not COMMIT_SHA.fullmatch(provenance.get("commit_sha", "")):
        issues.append("SC-007 provenance requires a full source commit SHA")
    if not provenance.get("source_uri", "").startswith("https://github.com/"):
        issues.append("SC-008 provenance requires an approved source URI")
    if provenance.get("identity_type") != "oidc":
        issues.append("SC-009 build identity must use OIDC")
    if vulnerabilities.get("critical", 0) > 0:
        issues.append("SC-010 critical vulnerabilities block release")
    if vulnerabilities.get("high", 0) > 0:
        issues.append("SC-011 high vulnerabilities block release")
    return sorted(set(issues))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("release", type=Path)
    args = parser.parse_args()
    issues = findings(json.loads(args.release.read_text()))
    if issues:
        print("FAIL\n" + "\n".join(issues))
        return 1
    print("PASS: release evidence satisfies the supply-chain policy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
