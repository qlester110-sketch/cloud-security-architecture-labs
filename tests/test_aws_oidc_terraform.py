import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
PROJECT = ROOT / "projects/01-multicloud-landing-zone"
MODULE = PROJECT / "terraform/aws-github-oidc"
WORKFLOW = PROJECT / "examples/github-actions-aws-oidc.yml"


class AwsOidcTerraformTests(unittest.TestCase):
    def setUp(self):
        self.main = (MODULE / "main.tf").read_text()
        self.variables = (MODULE / "variables.tf").read_text()
        self.workflow = WORKFLOW.read_text()

    def test_trust_is_scoped_to_repository_and_environment(self):
        self.assertIn(
            'repo:${var.github_organization}/${var.github_repository}:environment:${var.github_environment}',
            self.main,
        )
        self.assertIn('"token.actions.githubusercontent.com:sub" = local.github_subject', self.main)

    def test_audience_and_action_are_exact(self):
        self.assertIn('"token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"', self.main)
        self.assertIn('Action = "sts:AssumeRoleWithWebIdentity"', self.main)
        self.assertNotIn("StringLike", self.main)

    def test_inputs_reject_wildcards(self):
        self.assertEqual(self.variables.count('!strcontains(var.'), 3)

    def test_session_is_capped_at_one_hour(self):
        self.assertIn("var.max_session_duration <= 3600", self.variables)

    def test_reference_workflow_requests_only_required_permissions(self):
        self.assertIn("contents: read", self.workflow)
        self.assertIn("id-token: write", self.workflow)
        self.assertNotIn("contents: write", self.workflow)

    def test_reference_workflow_uses_protected_environment(self):
        self.assertIn("environment: production", self.workflow)
        self.assertIn("aws-actions/configure-aws-credentials@v4", self.workflow)
        self.assertNotIn("AWS_ACCESS_KEY_ID", self.workflow)
        self.assertNotIn("AWS_SECRET_ACCESS_KEY", self.workflow)

    def test_reference_workflow_cannot_run_from_examples_directory(self):
        self.assertNotIn("/.github/workflows/", str(WORKFLOW))


if __name__ == "__main__":
    unittest.main()
