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

```bash
./evals/run.sh --agent "claude -p"                 # results land in evals/results/<label>/
python3 evals/score.py --verbose                   # score them
```

`run.sh` walks every case, builds one prompt per case (the skill, then the artifact, with no
hint about what to look for), pipes it to your agent command, and saves the output. The only
requirement for the agent command is that it **reads the prompt on stdin and writes the
answer to stdout**.

```bash
./evals/run.sh --dry-run                           # preview: 12 prompts, nothing executed
./evals/run.sh --agent "claude -p" --case pos-05-sql-concat
./evals/run.sh --agent "ollama run qwen2.5-coder" --label qwen-coder
```

The case id is deliberately **not** put in the prompt. Ids like `neg-01-innerhtml-config`
telegraph the expected answer, and a model that reads them is being told the verdict.

## Command sheet

Flags move between releases. Check `--help` once; the contract above is what matters.

**Reads stdin, writes stdout — works as-is:**

| Tool | Command |
|---|---|
| Claude Code | `claude -p` |
| Gemini CLI | `gemini -p "$(cat)"` (see wrapper below) |
| Ollama | `ollama run qwen2.5-coder` |
| llm (simonw) | `llm -m gpt-4o` |
| Codex CLI | `codex exec -` (older builds take the prompt as an argument — use the wrapper) |
| Any OpenAI-compatible CLI | `your-cli -` |

**Wrapper, for anything that wants a file or an argument:**

```sh
#!/bin/sh
# /tmp/agent.sh — reads the prompt on stdin, prints the answer on stdout
tmp=$(mktemp); cat > "$tmp"
your-agent --prompt-file "$tmp" --no-interactive
rm -f "$tmp"
```

```bash
./evals/run.sh --agent /tmp/agent.sh --label my-agent
```

**Two runs you should always do:**

```bash
# 1. Your real agent
./evals/run.sh --agent "claude -p" --label claude
python3 evals/score.py --verbose

# 2. A second model, to see whether the gate is the skill or the model
./evals/run.sh --agent "ollama run qwen2.5-coder" --label qwen
python3 evals/score.py --verbose
```

If the gate holds on one model and collapses on the other, that is a finding about the
skill's robustness, not about the weaker model.

**Manual fallback** — the same thing by hand, from the repository root:

```bash
mkdir -p evals/results
for d in evals/cases/*/; do
  id=$(basename "$d")
  art=$(ls "$d"artifact.*)
  cat skills/security-triage/SKILL.md "$art" | your-agent > "evals/results/$id.md"
done
```

## What the scorer actually checks

`score.py` is mechanical and deliberately dumb. Per case it looks for the report structure
(`SECURITY TRIAGE REPORT` / `FINDINGS SUMMARY` / a `Confidence :` line), reads the `Track` and
`Severity` fields, and compares them with `expected.yaml`:

- **positives** must produce a finding, on the right track, within one severity band, and
  mention the key terms (`must_mention`)
- **negatives** must produce no finding, and must not contain a forbidden string
  (`must_not`) — checked after stripping the "No HIGH or MEDIUM findings" sentence, which
  would otherwise trip every negative on its own correct output

It cannot judge whether the reasoning was right. That is what `--verbose` and your eyes are
for. When a case fails, the first question is whether the case or the scorer is wrong — both
are code, and both have been wrong before.

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
