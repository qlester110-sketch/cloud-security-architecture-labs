import copy
import importlib.util
import json
from pathlib import Path
import unittest

PROJECT = Path(__file__).parents[1] / 'projects/06-safe-credential-rotation'
SPEC = importlib.util.spec_from_file_location('expiry', PROJECT / 'tools/expiry.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ExpiryTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((PROJECT / 'examples/credential-inventory.json').read_text())[0]

    def evaluate(self, **updates):
        record = copy.deepcopy(self.record)
        record.update(updates)
        return MODULE.plan([record], '2026-10-14T00:00:00Z')[0]

    def test_policy_deadline_does_not_claim_provider_expiration(self):
        result = self.evaluate()
        self.assertEqual(result['deadline_type'], 'rotate_by')
        self.assertEqual(result['status'], 'upcoming')

    def test_earliest_deadline_wins(self):
        result = self.evaluate(provider_expires_at='2026-10-15T00:00:00Z')
        self.assertEqual(result['deadline_type'], 'provider_expires_at')
        self.assertEqual(result['status'], 'urgent')

    def test_unknown_dates_are_not_healthy(self):
        self.assertEqual(self.evaluate(rotate_by=None)['status'], 'unknown')

    def test_overdue_and_warning_boundaries(self):
        for day,status in [('14','overdue'), ('15','urgent'), ('21','soon')]:
            self.assertEqual(self.evaluate(rotate_by='2026-10-'+day+'T00:00:00Z')['status'], status)

    def test_timezone_is_required_and_offsets_are_normalized(self):
        with self.assertRaises(ValueError):
            self.evaluate(rotate_by='2026-10-15')
        self.assertEqual(self.evaluate(rotate_by='2026-10-15T02:00:00+02:00')['days_remaining'], 1)

    def test_raw_secret_fields_and_values_are_rejected(self):
        record = dict(self.record, api_key='synthetic-secret')
        with self.assertRaises(ValueError):
            MODULE.plan([record], '2026-10-14T00:00:00Z')
        with self.assertRaises(ValueError):
            self.evaluate(secret_ref='synthetic-secret')

    def test_unknown_provider_contract_never_implies_automatic_rotation(self):
        self.assertEqual(self.evaluate()['next_action'], 'verify-provider-contract')
        self.assertEqual(self.evaluate(overlap_supported=False, renewal='api')['next_action'], 'manual-renewal-required')

    def test_duplicate_integration_and_string_boolean_are_rejected(self):
        with self.assertRaises(ValueError):
            MODULE.plan([self.record,self.record], '2026-10-14T00:00:00Z')
        with self.assertRaises(ValueError):
            self.evaluate(overlap_supported='true')
