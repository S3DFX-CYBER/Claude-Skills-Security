# Security Policy

## Scope

This repository is a prompt and a methodology, not an executable. The realistic issues are:

- **Dangerous guidance.** A fix that is wrong, incomplete, or would break the security
  property it claims to restore.
- **A missing check.** A class of vulnerability the skill should catch and does not, or a
  false-positive trap it falls into.
- **Unsafe default behaviour.** Anything that leads an agent to write exploit code, run
  untrusted artifacts, or exfiltrate what it is given.
- **Supply chain.** Tampering with this repository or its published artifacts.

The skill deliberately produces *reachability analysis*, not weaponised exploits. If you
find a path where it generates working attack payloads, that is in scope and I want to
know.

## Reporting

Open a [private security advisory](https://github.com/S3DFX-CYBER/Claude-Skills-Security/security/advisories/new),
or email the address on the GitHub profile. Do not open a public issue for a security
report.

Include: the artifact you fed it, the output you got, and what the correct output is.

## Response

- Acknowledged within 72 hours.
- Assessment within 7 days.
- Fix or a documented decision within 30 days.
- Credit in the CHANGELOG and the release notes, unless you ask otherwise.

## Not in scope

- A finding that requires the user to paste their own secrets into the prompt.
- "The model can be persuaded to be wrong" without a reproducible input that produces
  dangerous *advice* — models are probabilistic, and the fix has to be in the methodology.
- Vulnerabilities in the software being triaged. Report those to that project's maintainers.
