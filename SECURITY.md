# Security Policy

## Supported versions

CP-00 has not shipped a stable runtime release. Security fixes are applied to the
current default branch and to any active release branch once one exists.

## Reporting a vulnerability

Please report suspected vulnerabilities privately to the maintainers rather than
opening a public issue. Include:

- affected version or commit,
- a minimal reproduction or proof of concept,
- expected impact, and
- any relevant logs or artifacts with secrets redacted.

Maintainers should acknowledge receipt within three business days, provide a
triage decision, and coordinate disclosure timing with the reporter.

## CP-00 security boundary

This checkpoint only provides packaging and quality gates. It does not implement
sandboxing, Terraform, AWS access, Docker, policy evaluation, or agent lifecycle
behavior.
