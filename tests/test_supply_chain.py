import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
PROJECT = ROOT / "projects/03-software-supply-chain"
SPEC = importlib.util.spec_from_file_location("release_gate", PROJECT / "tools/release_gate.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class SupplyChainTests(unittest.TestCase):
    def load(self, name):
        return json.loads((PROJECT / "examples" / name).read_text())

    def test_secure_release_passes(self):
        self.assertEqual(MODULE.findings(self.load("secure-release.json")), [])

    def test_insecure_release_fails_all_major_boundaries(self):
        controls = {item.split()[0] for item in MODULE.findings(self.load("insecure-release.json"))}
        self.assertEqual(controls, {f"SC-{i:03d}" for i in range(1, 12) if i != 4})

    def test_high_vulnerability_blocks_otherwise_secure_release(self):
        release = self.load("secure-release.json")
        release["vulnerabilities"]["high"] = 1
        self.assertIn("SC-011 high vulnerabilities block release", MODULE.findings(release))

    def test_missing_vulnerability_evidence_fails_closed(self):
        release = self.load("secure-release.json")
        del release["vulnerabilities"]
        controls = {item.split()[0] for item in MODULE.findings(release)}
        self.assertEqual(controls, {"SC-010", "SC-011"})

    def test_malformed_vulnerability_counts_fail_closed(self):
        release = self.load("secure-release.json")
        release["vulnerabilities"] = {"critical": "0", "high": "1"}
        controls = {item.split()[0] for item in MODULE.findings(release)}
        self.assertEqual(controls, {"SC-010", "SC-011"})

    def test_unapproved_github_repository_is_rejected(self):
        release = self.load("secure-release.json")
        release["provenance"]["source_uri"] = "https://github.com/example/untrusted"
        self.assertIn("SC-008 provenance requires an approved source URI", MODULE.findings(release))


if __name__ == "__main__":
    unittest.main()
