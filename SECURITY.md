# Security policy

## Supported versions

Only the latest released version of the `tenet` plugin and the installer receives fixes.

## Reporting a vulnerability

Do not open a public issue for vulnerabilities, such as:

- a guard bypass;
- the installer writing outside its ownership manifest;
- a secret leaking through messages or logs.

Use GitHub's private vulnerability reporting ("Report a vulnerability" under the Security tab) once the repository is public. Include:

- what you ran (redact secrets);
- what you expected and what happened;
- OS, shell, Python and Claude Code versions.

## Scope and limits

The guard hook reduces accidental damage. It is not a sandbox and can be bypassed by deliberate obfuscation. See [docs/security.md](docs/security.md) for the threat model, what is technically enforced, and the known limits.

This project never asks for, stores or transmits credentials. If you find a secret committed to this repository, report it privately so it can be rotated and purged.
