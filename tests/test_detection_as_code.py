import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
PROJECT = ROOT / "projects/05-detection-as-code"
SPEC = importlib.util.spec_from_file_location("detect", PROJECT / "tools/detect.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class DetectionTests(unittest.TestCase):
    def event(self, name, **extra):
        base = {"eventName": name, "eventTime": "2026-01-01T00:00:00Z", "awsRegion": "us-east-1", "recipientAccountId": "111122223333", "userIdentity": {"type": "AssumedRole", "arn": "synthetic-role"}}
        base.update(extra)
        return base

    def test_benign_read_has_no_alert(self):
        self.assertEqual(MODULE.detect(self.event("ListBuckets")), [])

    def test_root_api_activity_is_critical(self):
        alerts = MODULE.detect(self.event("DeleteBucket", userIdentity={"type": "Root", "principalId": "root"}))
        self.assertEqual(alerts[0]["rule_id"], "AWS-IAM-001")
        self.assertEqual(alerts[0]["severity"], "critical")

    def test_console_login_without_mfa(self):
        alerts = MODULE.detect(self.event("ConsoleLogin", additionalEventData={"MFAUsed": "No"}))
        self.assertEqual({a["rule_id"] for a in alerts}, {"AWS-IAM-002"})

    def test_logging_change_is_critical(self):
        self.assertEqual(MODULE.detect(self.event("StopLogging"))[0]["rule_id"], "AWS-LOG-001")

    def test_iam_change_is_detected(self):
        self.assertEqual(MODULE.detect(self.event("AttachRolePolicy"))[0]["rule_id"], "AWS-IAM-003")

    def test_public_ssh_is_detected(self):
        alerts = MODULE.detect(self.event("AuthorizeSecurityGroupIngress", requestParameters={"cidrIp": "0.0.0.0/0", "fromPort": 22}))
        self.assertEqual(alerts[0]["rule_id"], "AWS-NET-001")


if __name__ == "__main__":
    unittest.main()
