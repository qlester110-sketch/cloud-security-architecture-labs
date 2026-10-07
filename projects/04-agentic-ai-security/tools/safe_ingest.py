#!/usr/bin/env python3
"""Deterministic pre-model guardrail for untrusted AI ingestion content."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ALLOWED_SOURCE_TYPES = {"document", "webpage", "email", "ticket"}
MAX_CONTENT_BYTES = 100_000
INJECTION_PATTERNS = [
    re.compile(r"ignore (all |any )?(previous|prior) instructions", re.I),
    re.compile(r"system prompt", re.I),
    re.compile(r"developer message", re.I),
    re.compile(r"(?:reveal|exfiltrate|send).{0,40}(?:system prompt|developer message|credentials?|secrets?)", re.I),
    re.compile(r"do not tell (the )?user", re.I),
    re.compile(r"override (the )?(policy|rules|instructions)", re.I),
]
SENSITIVE_PATTERNS = {
    "email": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "phone": re.compile(r"(?<!\d)(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)"),
    "api_key": re.compile(r"\b(?:sk|api)[-_][A-Za-z0-9_-]{16,}\b", re.I),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
}

COMPACT_INJECTION_INDICATORS = {
    "ignorepreviousinstructions": "obfuscated ignore previous instructions",
    "ignorepriorinstructions": "obfuscated ignore prior instructions",
    "revealthe systemprompt": "obfuscated reveal system prompt",
    "revealsystemprompt": "obfuscated reveal system prompt",
    "donottelltheuser": "obfuscated do not tell the user",
}


def redact(text: str) -> tuple[str, list[str]]:
    detected: list[str] = []
    for label, pattern in SENSITIVE_PATTERNS.items():
        if pattern.search(text):
            detected.append(label)
            text = pattern.sub(f"[REDACTED_{label.upper()}]", text)
    return text, detected


def injection_indicators(text: str) -> list[str]:
    indicators = [pattern.pattern for pattern in INJECTION_PATTERNS if pattern.search(text)]
    compact = re.sub(r"[^a-z0-9]", "", text.lower())
    for phrase, label in COMPACT_INJECTION_INDICATORS.items():
        normalized_phrase = re.sub(r"[^a-z0-9]", "", phrase)
        if normalized_phrase in compact and label not in indicators:
            indicators.append(label)
    return indicators


def ingest(record: dict, now: str | None = None) -> dict:
    source_type = record.get("source_type", "")
    source_id = record.get("source_id", "")
    content = record.get("content", "")
    errors = []
    if source_type not in ALLOWED_SOURCE_TYPES:
        errors.append("SOURCE_TYPE_NOT_ALLOWED")
    if not source_id:
        errors.append("SOURCE_ID_REQUIRED")
    if not isinstance(content, str) or not content.strip():
        errors.append("CONTENT_REQUIRED")
        content = ""
    if len(content.encode("utf-8")) > MAX_CONTENT_BYTES:
        errors.append("CONTENT_TOO_LARGE")

    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    sanitized, sensitive = redact(content)
    indicators = injection_indicators(content)

    if errors:
        decision = "block"
    elif indicators:
        decision = "quarantine"
    elif sensitive:
        decision = "review"
    else:
        decision = "allow"

    return {
        "decision": decision,
        "sanitized_content": sanitized,
        "findings": {
            "validation_errors": errors,
            "sensitive_data_types": sensitive,
            "injection_indicators": indicators,
        },
        "provenance": {
            "source_type": source_type,
            "source_id": source_id,
            "content_sha256": digest,
            "ingested_at": now or datetime.now(timezone.utc).isoformat(),
            "trust_level": "untrusted",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    result = ingest(json.loads(args.record.read_text()))
    print(json.dumps(result, indent=2))
    return 0 if result["decision"] in {"allow", "review"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
