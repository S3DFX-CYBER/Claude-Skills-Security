# Claude-Skills-Security

<div align="center">

**A production-grade security triage skill for AI agents.**
Confidence-gated. Context-aware. No false-positive noise.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Skills](https://img.shields.io/badge/Claude-Skills%20Compatible-orange)](https://claude.ai)
[![OWASP](https://img.shields.io/badge/OWASP-LLM%20Top%2010-blue)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
[![Agent Ready](https://img.shields.io/badge/Agent-Ready-brightgreen)](AGENTS.md)

</div>

---

## What this is

Security scanners find patterns. This skill answers what scanners cannot:

- **Is this actually exploitable** in this specific deployment context?
- **Does the CVSS base score reflect real-world risk** here — or is it overstated?
- **Is this an LLM model-level issue** (not fixable in code) **or application-level** (fixable)?
- **Is this CI/CD pattern a real attack vector** or a misconfigured false alarm?
- **What can an attacker concretely do**, and what is the minimum viable fix?

The difference between a scanner and a researcher is **judgment**. This skill encodes that judgment.

---

## The core mechanic: Confidence Gating

Every finding is blocked behind a confidence gate before severity is assigned.

```
HIGH    Vulnerable pattern confirmed + attacker-controlled input confirmed
        + exploitable in the described context.
        → Full triage report produced.

MEDIUM  Vulnerable pattern found, but input source unclear or exploitability
        depends on context not fully visible.
        → Triage report produced with explicit caveat.

LOW     Theoretical risk only. Multiple unlikely conditions required.
        → NOT reported as a finding. Listed in Notes only.
```

This is the single most important feature. It's why this skill doesn't produce noise.

---

## Coverage: 5 Triage Tracks

| Track | Scope |
|-------|-------|
| **A — CVE / Scanner Alert** | CVE IDs, Dependabot, Snyk, npm audit, pip-audit, Trivy, SARIF |
| **B — Code Snippet** | Any language — data flow tracing, sink reachability, upstream sanitization checks |
| **C — LLM Application Security** | Prompt injection, RAG pipelines, AI agents, OWASP LLM Top 10 2025 |
| **D — CI/CD & GitHub Actions** | Script injection (CWE-78), `pull_request_target` RCE, SHA pinning, permissions scoping |
| **E — Container & Infrastructure** | Dockerfile, docker-compose, k8s YAML, Helm — root user, floating tags, secret exposure |

Multiple tracks can apply simultaneously. The skill classifies before triaging.

---

## Output format

Every HIGH/MEDIUM finding produces a structured triage report:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 SECURITY TRIAGE REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FINDING
  Title      : [What is wrong — not just the CVE ID]
  Track      : [A–E with label]
  Confidence : [HIGH / MEDIUM — one-line reason why]
  Severity   : [🔴 Critical / 🟠 High / 🟡 Medium / 🔵 Low]
  CVSS       : [X.X — full CVSS:3.1 vector with component reasoning]

CLASSIFICATION
  OWASP / CWE / WSTG / ASVS Level

WHAT IS THIS?
  Plain English. No assumed knowledge.

AM I AFFECTED?
  Specific conditions. Concrete attacker requirements.
  CVSS context adjustment — does base score overstate or understate here?

IMPACT
  Concrete attacker capabilities. Specific, not generic.

THE FIX
  Copy-paste ready. Diff format. Minimum viable fix first.

VERIFY IT'S FIXED
  One runnable check — grep, command, or test assertion.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Real-world pedigree

The CI/CD detection logic in Track D is derived from original CVE research:

- **CVE-2026-40316** — `pull_request_target` + `git show` RCE in OWASP BLT (CVSS 8.8, CWE-94/95). Patched in BLT v2.1.1. The skill encodes the exact detection heuristic and CVSS reasoning used in this advisory.
- **GHSA-wxm3-64fx-cmx9** — Chained RCE via `pull_request_target` + Django model import. High severity.
This isn't a prompt template. It's field-tested triage methodology.

---

## Installation

### Claude (native)

Copy `Claude Skills/Security-Triage-Skills.md` into your Claude Project as a Project instruction, or reference it as a skill file.

For the `.claude/skills/` format (Claude Code / agentic workflows):

```bash
git clone https://github.com/S3DFX-CYBER/Claude-Skills-Security.git
cp "Claude Skills/Security-Triage-Skills.md" /your/project/.claude/skills/security-triage.md
```

### OpenAI Codex / Responses API

```python
with open("Claude Skills/Security-Triage-Skills.md") as f:
    skill = f.read()

response = client.responses.create(
    model="codex-mini-latest",
    instructions=skill,
    input="Triage this workflow file: ..."
)
```

### Cursor / Windsurf / Copilot (Rules)

Add to `.cursorrules` or `.github/copilot-instructions.md`:

```
Follow the triage methodology defined in:
Claude Skills/Security-Triage-Skills.md
Apply confidence gating before every finding.
```

### Gemini CLI

```bash
gemini -s "$(cat 'Claude Skills/Security-Triage-Skills.md')" \
  "Triage this Dockerfile: ..."
```

### Any agent runtime

The skill is plain markdown. If your agent accepts a system prompt or context file, it works. See [AGENTS.md](AGENTS.md) for invocation contracts and agentic discovery.

---

## Compatibility

| Runtime | Method | Status |
|---------|--------|--------|
| Claude (claude.ai / Claude Code) | Native `.claude/skills/` | ✅ Primary |
| OpenAI Codex | `instructions` parameter | ✅ Tested |
| Cursor | `.cursorrules` | ✅ Tested |
| Windsurf | Rules file | ✅ Tested |
| Gemini CLI | `-s` system prompt flag | ✅ Tested |
| Any OpenAI-compatible API | `system` message | ✅ Compatible |
| GitHub Copilot | `.github/copilot-instructions.md` | ✅ Tested |

---

## What this is NOT

- Not a vulnerability scanner. Run your scanners first, feed the output here.
- Not a compliance checklist. This is exploitability-focused triage.
- Not a generic "act as a security expert" prompt. The confidence gate and structured output format are the entire point.

---

## Contributing

Issues and PRs welcome. If you have a real-world finding that exposed a gap in the triage logic, open an issue with the finding details (redacted as needed). The methodology improves from field cases.

---

## Author

**S3DFX-CYBER** — Security researcher. CVE-2026-40316. OWASP LLM Top 10 v2 Co-Lead (LLM:08) 

---

<div align="center">
<sub>Designed for Claude Skills. Compatible with any agent runtime that reads markdown context.</sub>
</div>
