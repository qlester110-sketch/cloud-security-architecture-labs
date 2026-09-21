import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "projects/01-multicloud-landing-zone/tools/generate_aws_trust_policy.py"
SPEC = importlib.util.spec_from_file_location("trust_policy", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class TrustPolicyTests(unittest.TestCase):
    def setUp(self):
        path = ROOT / "projects/01-multicloud-landing-zone/config/oidc-trust.json"
        self.config = json.loads(path.read_text())
        self.policy = MODULE.build_policy(self.config)
        self.statement = self.policy["Statement"][0]

    def test_uses_web_identity_only(self):
        self.assertEqual(self.statement["Action"], "sts:AssumeRoleWithWebIdentity")

    def test_audience_is_exact(self):
        conditions = self.statement["Condition"]["StringEquals"]
        self.assertEqual(
            conditions["token.actions.githubusercontent.com:aud"],
            "sts.amazonaws.com",
        )

    def test_subject_is_repository_and_environment_scoped(self):
        conditions = self.statement["Condition"]["StringEquals"]
        self.assertEqual(
            conditions["token.actions.githubusercontent.com:sub"],
            "repo:qlester110-sketch/cloud-security-architecture-labs:environment:production",
        )

    def test_wildcards_are_rejected_by_contract(self):
        rendered = json.dumps(self.policy)
        self.assertNotIn("StringLike", rendered)
        self.assertNotIn("*", rendered)

    def test_missing_scope_fails_closed(self):
        incomplete = dict(self.config)
        incomplete.pop("environment")
        with self.assertRaisesRegex(ValueError, "environment"):
            MODULE.build_policy(incomplete)


if __name__ == "__main__":
    unittest.main()
