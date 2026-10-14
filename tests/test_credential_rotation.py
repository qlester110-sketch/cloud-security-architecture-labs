import importlib.util
from pathlib import Path
import tempfile
import unittest

PROJECT = Path(__file__).parents[1] / 'projects/06-safe-credential-rotation'
SPEC = importlib.util.spec_from_file_location('rotation', PROJECT / 'tools/rotation.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RotationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'lab.sqlite'
        self.lab = MODULE.RotationLab(self.path)
        self.lab.register('orders', 0)

    def tearDown(self):
        self.lab.close()
        self.tmp.cleanup()

    def promote(self):
        self.lab.prepare()
        self.lab.validate()
        self.lab.promote(0, grace=30)

    def test_success_under_synthetic_load(self):
        result = MODULE.demo('success')
        self.assertEqual(result['successful_operations'], 300)
        self.assertEqual(result['authentication_failures'], 0)
        self.assertEqual(result['rotation_outcome'], 'retired')
        self.assertEqual(result['valid_credentials'], 1)

    def test_failed_validation_preserves_current_key(self):
        old = self.lab.token(1)
        new = self.lab.prepare()
        candidate = self.lab.token(new)
        self.assertFalse(self.lab.validate(False))
        self.assertTrue(self.lab.accepts(old))
        self.assertFalse(self.lab.accepts(candidate))
        self.assertEqual(self.lab.state()['current'], 1)

    def test_unvalidated_key_cannot_be_promoted(self):
        self.lab.prepare()
        with self.assertRaises(RuntimeError):
            self.lab.promote(0)

    def test_old_worker_keeps_operating_during_overlap(self):
        self.promote()
        self.assertTrue(self.lab.process('orders', 'example-order'))
        self.assertEqual(self.lab.retire(10), 'waiting')

    def test_revocation_requires_ack_and_old_key_is_rejected(self):
        old = self.lab.token(1)
        self.promote()
        self.lab.refresh('orders', 10)
        self.assertEqual(self.lab.retire(10), 'retired')
        self.assertFalse(self.lab.accepts(old))
        self.assertTrue(self.lab.process('orders', 'new-order'))

    def test_stale_heartbeat_does_not_allow_retirement(self):
        self.promote()
        self.lab.refresh('orders', 1)
        self.assertEqual(self.lab.retire(20), 'waiting')

    def test_deadline_rolls_back_and_new_key_is_rejected(self):
        self.promote()
        candidate = self.lab.token(2)
        self.assertEqual(self.lab.retire(30), 'rolled_back')
        self.assertEqual(self.lab.state()['current'], 1)
        self.assertFalse(self.lab.accepts(candidate))
        self.assertTrue(self.lab.process('orders', 'after-rollback'))

    def test_controller_restart_resumes_rotation(self):
        self.promote()
        self.lab.close()
        self.lab = MODULE.RotationLab(self.path)
        self.lab.refresh('orders', 10)
        self.assertEqual(self.lab.retire(10), 'retired')

    def test_competing_controller_cannot_start_second_rotation(self):
        self.lab.prepare()
        other = MODULE.RotationLab(self.path)
        try:
            with self.assertRaises(RuntimeError):
                other.prepare()
        finally:
            other.close()

    def test_retry_does_not_duplicate_side_effect(self):
        self.assertTrue(self.lab.process('orders', 'idempotent-order'))
        self.promote()
        self.lab.refresh('orders', 1)
        self.assertFalse(self.lab.process('orders', 'idempotent-order'))
        self.assertEqual(self.lab.report()['orders_processed'], 1)

    def test_no_secrets_in_audit_or_report(self):
        old = self.lab.token(1)
        self.promote()
        new = self.lab.token(2)
        report = str(self.lab.report())
        self.assertNotIn(old, report)
        self.assertNotIn(new, report)

    def test_local_store_permissions(self):
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)

    def test_failed_attempt_does_not_reuse_version(self):
        self.lab.prepare()
        self.lab.validate(False)
        self.assertEqual(self.lab.prepare(), 3)

    def test_enrollment_is_frozen_during_cutover(self):
        self.promote()
        with self.assertRaises(RuntimeError):
            self.lab.register('untracked', 10)

    def test_no_worker_cannot_retire_old_key(self):
        with self.lab.db:
            self.lab.db.execute('DELETE FROM workers')
        self.promote()
        self.assertEqual(self.lab.retire(5), 'waiting')

    def test_all_failure_scenarios_keep_operations_running(self):
        for scenario in ('failed-validation', 'stale-worker'):
            result = MODULE.demo(scenario)
            self.assertEqual(result['authentication_failures'], 0)
            self.assertEqual(result['successful_operations'], 300)
