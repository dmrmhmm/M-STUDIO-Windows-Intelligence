# Security Policy

## Supported versions
Security fixes target the latest code on the `main` branch.

## Reporting
Please do not publish exploitable details in a public issue. Contact the repository owner privately through GitHub's security reporting feature.

## Current security posture
- The application is read-only.
- It does not request administrator privileges.
- It does not accept arbitrary shell commands.
- It does not transmit diagnostics.
- PowerShell use is limited to a fixed read-only CIM query with a timeout.

This is an early project. Do not use it as a security scanner or remediation tool.
