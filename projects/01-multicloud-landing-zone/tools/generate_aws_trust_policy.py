#!/usr/bin/env python3
"""Generate a least-privilege AWS IAM trust policy for GitHub Actions OIDC."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_policy(config: dict[str, str]) -> dict:
    required = {"github_org", "repository", "environment", "audience"}
    missing = sorted(required - config.keys())
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")

    subject = (
        f"repo:{config['github_org']}/{config['repository']}:"
        f"environment:{config['environment']}"
    )
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Federated": (
                        "arn:aws:iam::<ACCOUNT_ID>:oidc-provider/"
                        "token.actions.githubusercontent.com"
                    )
                },
                "Action": "sts:AssumeRoleWithWebIdentity",
                "Condition": {
                    "StringEquals": {
                        "token.actions.githubusercontent.com:aud": config["audience"],
                        "token.actions.githubusercontent.com:sub": subject,
                    }
                },
            }
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=Path)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    print(json.dumps(build_policy(config), indent=2))


if __name__ == "__main__":
    main()
