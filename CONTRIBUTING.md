# Contributing

The most valuable contribution is a **case where the skill was wrong**.

A real finding that exposed a gap is worth more than a rewrite, because the methodology
improves from field cases and nothing else.

## What to send

**A false positive** — the skill reported something that was not exploitable. Use the
[false-positive template](.github/ISSUE_TEMPLATE/false-positive.yml). Include the artifact
and the reasoning that made it a false positive. These become `neg-*` eval cases.

**A false negative** — something real it missed, or buried in NOTES. Use the
[bug template](.github/ISSUE_TEMPLATE/bug_report.yml). Include what it should have said.
These become `pos-*` eval cases.

**A new track or sink table** — use the [new track template](.github/ISSUE_TEMPLATE/new-track.yml).
Bring the detection heuristic, not just the topic name.

## Changing the skill

1. Edit `skills/security-triage/SKILL.md`. **This is the only file you edit.** Never edit
   `.claude/skills/...` by hand — it is generated.
2. `make sync` to regenerate the mirror.
3. `make check` to verify drift, frontmatter and the eval corpus.
4. If your change alters a verdict, update `evals/expected.yaml` and say why in the PR.

CI fails on drift between the two copies. That is intentional: the last release shipped two
copies of the skill that had quietly diverged.

## Style

- Rules, not descriptions. "A dangerous sink fed by a constant is not a finding" beats a
  paragraph about input validation.
- Every rule should be falsifiable against an artifact. If you cannot write an eval case for
  it, it is probably too vague to change behaviour.
- Plain English before jargon, and explain the jargon inline the first time.
- No emoji in the skill body. It renders inconsistently across runtimes.

## What will be declined

- New tracks that duplicate an existing one with different words.
- Rules that only fire on a specific vendor's product.
- Anything that turns the output into a checklist of best practices. The gate exists to
  keep that out.

## Test fixtures

Never commit a real credential, and never commit one that looks real — GitHub push
protection will reject the push, which is the mechanism Track F asks you to enable.
Use `sk_live_DOCS_EXAMPLE_NOT_A_REAL_KEY`, `AKIAIOSFODNN7EXAMPLE` or
`ghp_REPLACE_WITH_REAL_TOKEN` style placeholders. If a case needs to test liveness
assessment, describe the provider response in the case README instead.

## Commits

Conventional commits are welcome but not enforced. One logical change per PR. Update
`CHANGELOG.md` under `## [Unreleased]`.
