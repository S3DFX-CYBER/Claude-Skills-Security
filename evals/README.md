# Evals

Twelve labelled cases. Six are real vulnerabilities; six are patterns a scanner flags that
are not vulnerabilities.

The negatives are the point. Any model can produce the six positives. A triage skill earns
its keep on the six it declines to report.

## Why this exists

"Confidence-gated" is a claim until it is measured. This corpus turns the gate into three
numbers you can publish, compare across models, and regression-test when you edit the
skill.

| Metric | Definition | Target |
|---|---|---|
| **Recall** | positives with a HIGH/MEDIUM report | 6 / 6 |
| **False positives** | negatives that produced a HIGH/MEDIUM finding | 0 / 6 |
| **Track accuracy** | cases routed to the right track | 12 / 12 |
| **Severity agreement** | findings within one band of `expected.yaml` | 6 / 6 |

A skill that scores 6/6 recall and 4/6 false positives is worse than useless — it is a
scanner with extra steps. Report both numbers or neither.

## Running it

The protocol is deliberately manual: it must work on any runtime, not just one vendor's
harness.

1. Install the skill for your runtime (see the main README).
2. For each case directory, feed `artifact.*` to the agent as the user message, with no
   hint about what to look for. Do not name the track. Do not say "is this vulnerable".
3. Save the full output to `results/<runtime>/<case-id>.md`.
4. Score against `expected.yaml`.

```
for d in cases/*/; do
  id=$(basename "$d")
  art=$(ls "$d"artifact.*)
  cat skills/security-triage/SKILL.md "$art" | your-agent > "results/$id.md"
done
```

Feeding the skill and the artifact in one prompt is the honest test: it is how a user with
the skill installed will experience it.

## Scoring

For each case, record:

```
case                          finding  track  severity  verdict
pos-01-pr-target-git-show     yes      D      crit      pass
neg-01-innerhtml-config       NO       B      —         pass
neg-03-transitive-cve-unused  NO       A      —         pass
```

Rules:
- A negative case fails if *any* HIGH or MEDIUM finding is produced, even a correct-looking
  one about a different line. The contract is "no noise", not "mostly no noise".
- A positive case fails if the finding is buried in NOTES. Suppressed findings are
  false negatives, and they are worse than false positives because nobody sees them.
- `must_not` strings are checked mechanically — `UI:N` on a CI/CD finding, `Critical` on a
  best-practice note. These catch reasoning errors that the headline verdict hides.

## Publishing results

Once you have run it, put the table in the main README. Include the model and date:

```
Evals (gpt-x, 2026-11-25): recall 6/6 · false positives 0/6 · track 12/12
```

Do not publish a number you have not measured, and re-run when you change the gate. A
stale score is a false claim.

## A note on the credentials in this corpus

Every key here is a non-functional placeholder, and deliberately so: GitHub push protection
rejects commits containing real-looking credentials. That block is correct, and it is the
same mechanism Track F tells you to enable.

It also means the fixtures are weaker than reality — a placeholder key cannot be verified
as live. Score `pos-03` and `pos-06` on whether the skill identifies *where the credential
reaches* and states that liveness is unverified, not on whether it names a provider.

## Adding a case

A new case needs an artifact, a `README.md` line saying what it tests, and an entry in
`expected.yaml`. The best source of new cases is a false positive you actually received —
that is how the negatives here were chosen.

Highest-value additions: a Rust `unsafe` block with a bounds check, a Java
`ObjectInputStream` behind an allowlist, a k8s manifest with `privileged: true`, a
`postMessage` handler that validates origin, and a Terraform S3 bucket with public ACLs.
