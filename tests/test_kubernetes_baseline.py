import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
PROJECT = ROOT / "projects/02-kubernetes-security-baseline"
SCRIPT = PROJECT / "tools/policy_check.py"
SPEC = importlib.util.spec_from_file_location("policy_check", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class KubernetesBaselineTests(unittest.TestCase):
    def load(self, name):
        return json.loads((PROJECT / "examples" / name).read_text())

    def test_secure_workload_passes(self):
        self.assertEqual(MODULE.violations(self.load("secure-deployment.json")), [])

    def test_insecure_workload_is_rejected(self):
        findings = MODULE.violations(self.load("insecure-deployment.json"))
        control_ids = {finding.split()[0] for finding in findings}
        self.assertEqual(
            control_ids,
            {"K8S-001", "K8S-002", "K8S-003", "K8S-005", "K8S-006", "K8S-007", "K8S-008", "K8S-009"},
        )

    def test_default_deny_covers_both_directions(self):
        text = (PROJECT / "manifests/default-deny-network-policy.yaml").read_text()
        self.assertIn("- Ingress", text)
        self.assertIn("- Egress", text)
        self.assertIn("podSelector: {}", text)


if __name__ == "__main__":
    unittest.main()
