# Security Policy

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability involving credentials, live cloud resources, or sensitive data. Use GitHub private vulnerability reporting after the repository is published.

## Repository rules

- Never commit secrets, tokens, private keys, account identifiers, or proprietary configuration.
- Use synthetic data and example domains.
- Pin third-party GitHub Actions by commit SHA before a project is marked complete.
- Run secret scanning, static analysis, dependency review, and infrastructure validation in CI.
- Document known limitations and accepted risks in each project.
