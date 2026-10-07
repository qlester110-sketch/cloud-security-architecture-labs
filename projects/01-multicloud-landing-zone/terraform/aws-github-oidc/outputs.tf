output "role_arn" {
  description = "Role ARN supplied to aws-actions/configure-aws-credentials."
  value       = aws_iam_role.github_actions.arn
}

output "trusted_subject" {
  description = "Exact GitHub OIDC subject allowed to assume the role."
  value       = local.github_subject
}

output "aws_account_id" {
  description = "AWS account in which the trust relationship was created."
  value       = data.aws_caller_identity.current.account_id
}
