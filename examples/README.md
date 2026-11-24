# Examples

Three input/output pairs, showing what the skill actually produces. Not descriptions of
the format - the real output, on real artifacts.

| # | Input | What it demonstrates |
|---|---|---|
| [01 - CI/CD RCE](01-ci-cd-rce/) | A `pull_request_target` workflow that checks out PR code | The flag case. Mirrors the shape of CVE-2026-40316. |
| [02 - False positives](02-false-positive/) | Four dangerous-looking sinks, all safe | **The gate declining to report.** The most important example here. |
| [03 - LLM / RAG](03-llm-rag/) | An ingestion pipeline, a system prompt, an output handler | Track C, three findings, one summary table. |

Start with **02**. Anyone can flag a sink. A triager's value is the finding they refuse to
raise, with the reason attached.

## Reproducing

```bash
# Claude Code, with the skill installed
claude "Triage this workflow file: $(cat examples/01-ci-cd-rce/input.yml)"

# Any runtime
cat skills/security-triage/SKILL.md examples/01-ci-cd-rce/input.yml
```

Output varies with the model. The verdicts (confidence, severity, track) should not - that
is what `evals/` measures.
