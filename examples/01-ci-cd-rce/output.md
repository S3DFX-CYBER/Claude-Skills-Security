# Output - example 01

> Input: [`input.yml`](input.yml) - a `pull_request_target` workflow that checks out the
> pull request head and runs Django management commands against it.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 SECURITY TRIAGE REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FINDING
  Title      : Untrusted pull request code executes in a privileged CI runner
               with write-scoped GITHUB_TOKEN (pull_request_target + head checkout)
  Track      : D — CI/CD & GitHub Actions
  Confidence : HIGH — pull_request_target confirmed, PR head checked out, code executed,
               write-all permissions declared at workflow level
  Severity   : 🔴 Critical
  CVSS       : 8.8 — CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H
               AV:N  attacker reaches the workflow through a public fork PR
               AC:L  no special conditions; a normal PR triggers the path
               PR:N  no repository privileges needed — any contributor can open a PR
               UI:R  a maintainer must apply the `regenerate-migrations` label
               S:U   the runner is compromised, not a downstream component
               C/I/A:H full read of secrets, full write to the repo, runner is disposable

CLASSIFICATION
  OWASP      : A08:2021 Software and Data Integrity Failures
  CWE        : CWE-94 Improper Control of Generation of Code — the workflow executes
               code it did not write or review.
               CWE-829 Inclusion of Functionality from Untrusted Control Sphere — the
               PR head is an untrusted control sphere brought into the trusted runner.
  ASVS Level : L2 — V10.3 (malicious code), V14.2 (dependency/build integrity)

WHAT IS THIS?
  `pull_request_target` runs the workflow in the context of your base repository: the
  workflow file from `main`, your secrets, and a `GITHUB_TOKEN` that can write. That is
  the point of the trigger — it lets you label and comment on PRs from forks.
  The danger is the second half: this workflow also checks out the PR's own code and runs
  it. So the PR author's code now runs with the base repo's credentials.

AM I AFFECTED?
  Three conditions, all visible in this file:
    1. Trigger is `pull_request_target` — yes, line 3.
    2. PR head code is checked out — yes, `ref: github.event.pull_request.head.sha`.
    3. That code is executed — yes, `pip install -r requirements.txt` (installs from the
       PR's own requirements file) and `python manage.py makemigrations`.
  The attacker needs no privileges: opening a PR against a public repo is enough.
  The maintainer label is a real gate, but it is a gate on intent, not on content — the
  label says "run this", not "this is safe". Reviewers approve migration regeneration
  precisely because it is routine.
  On the CVSS score: base 8.8 with UI:R is correct here, and this is the exact reasoning
  behind CVE-2026-40316 (OWASP BLT) scoring 8.8 rather than 9.x. Do not upgrade to UI:N —
  the maintainer interaction is real. Do not downgrade below High either: one approved
  label converts an unauthenticated PR into full repository compromise.

IMPACT
  Any GitHub user can run arbitrary code inside your CI runner with:
    - `GITHUB_TOKEN` write access (declared `permissions: write-all`) — push commits,
      create releases, modify workflows, alter branch protection via API where permitted
    - every repository secret available to the workflow — deploy keys, registry tokens,
      cloud credentials
    - a build cache and artifact store that persist between runs
  Concretely: exfiltrate secrets, inject a commit into `main`, or publish a tampered
  release. Because `pip install -r requirements.txt` reads the attacker's requirements
  file, this also needs no malicious Python file at all — a dependency spec with a
  `--index-url` or a local path is enough.

BLIND SPOTS
  Not visible to me: whether the repository is public (a private repo with no external
  contributors changes the threat model but not the pattern), whether secrets are scoped
  to this environment, and whether branch protection blocks direct pushes by the token.
  Any of these changes blast radius, none of them removes the finding.

THE FIX
  Minimum viable fix — keep the label workflow, drop the privilege:

  -on:
  -  pull_request_target:
  -    types: [labeled]
  +on:
  +  pull_request:
  +    types: [labeled]
  -
  -permissions: write-all
  +permissions:
  +  contents: read
   jobs:
     regen:
       if: github.event.label.name == 'regenerate-migrations'
       runs-on: ubuntu-latest
       steps:
  -      - uses: actions/checkout@v4
  -        with:
  -          ref: ${{ github.event.pull_request.head.sha }}
  +      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
  +        with:
  +          ref: ${{ github.event.pull_request.head.sha }}
  +          persist-credentials: false

  With `pull_request`, fork PRs get a read-only token and no secrets. The job can still
  install and run the code; it simply has nothing worth stealing. `persist-credentials:
  false` stops the checkout from leaving the token in `.git/config`.
  Note the action is also pinned to a commit SHA — `@v4` is a mutable tag.

  If you genuinely need write access (posting a comment on the PR), split it:
  one read-only `pull_request` job that generates the migrations and uploads them as an
  artifact, and a separate `workflow_run` job that downloads the artifact and comments.
  Never give the job that executes PR code a write token.

VERIFY IT'S FIXED
  grep -rn "pull_request_target" .github/workflows/ && echo "FAIL: privileged trigger remains"
  grep -rn "permissions: write-all" .github/workflows/ && echo "FAIL: over-broad token"
  grep -rnE "uses: [^@]+@v[0-9]" .github/workflows/ && echo "WARN: mutable action tag"
  Then confirm on a test fork that a PR runs the job and the token cannot push.

REFERENCES
  - CWE-94: https://cwe.mitre.org/data/definitions/94.html
  - OWASP GitHub Actions Security Cheat Sheet:
    https://cheatsheetseries.owasp.org/cheatsheets/GitHub_Actions_Security_Cheat_Sheet.html
  - GitHub: security hardening for GitHub Actions
  - CVE-2026-40316 / GHSA-wxm3-64fx-cmx9 — the same shape in OWASP BLT, CVSS 8.8
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ACTION  🔴 Critical — fix before the next deploy. Until it ships, disable the workflow:
        `gh workflow disable regenerate-migrations.yml`, or remove the
        `regenerate-migrations` label from the repo so the job cannot be triggered.
```

## What to notice

- The verdict is one sentence a developer can act on, and the title names the *mechanism*,
  not the CVE.
- `AM I AFFECTED` cites line numbers from the input, so the reader can check the claim.
- The CVSS section argues with itself: why not 9.x, why not Medium. That is the difference
  between a score and a triage.
- `BLIND SPOTS` names three things that would change blast radius — and says the finding
  survives all three.
- `ACTION` gives an interim mitigation that works *today*, before the fix ships.
