# Changelog

All notable changes to Claude-Skills-Security are documented here.

Format: [Semantic Versioning](https://semver.org/)
Methodology: Exploitability-first triage. Every change is grounded in field findings.

---

## [1.2.2] — 2026-11-26

### Fixed
- **Track C now follows the OWASP Top 10 for LLM Applications 2026** (published
  2026-08-04), not the 2025 list. The numbering moved, so every heuristic was renumbered:
  Improper Output Handling is **LLM10** (was LLM05), Excessive Agency is **LLM03** (was
  LLM06), Supply Chain is **LLM04** (was LLM03), Data and Model Poisoning is **LLM05** (was
  LLM04), Unbounded Consumption is **LLM06** (was LLM10), Misinformation is **LLM07** (was
  LLM09), Vector and Embedding Weaknesses is **LLM09** (was LLM08).
- **Added LLM08:2026 Hidden Context Exposure**, which absorbs and broadens 2025's LLM07
  System Prompt Leakage: system prompt, developer instructions, retrieved policy text, tool
  and function schemas, permission and role directives, output formatting rules — with the
  four-band severity ladder the 2026 text specifies.
- **LLM10:2026 Improper Output Handling** gains the two sink classes the 2026 text adds:
  ANSI escape sequences reaching terminal, log-viewer and IDE sinks, and chat UIs that
  auto-fetch Markdown images or link previews from model output.
- **Agentic references corrected to the official ASI01–ASI10 IDs.** The previous labels
  were descriptive inventions; the published list is ASI01 Agent Goal Hijack through ASI10
  Rogue Agents. Example 03 cited three of them incorrectly and is fixed.

### Added
- **2025 → 2026 numbering map** in Track C, so a report written against the old list can be
  translated before severity is reasoned about.
- **Hard rule:** never cite an LLM category without its year.
- Taxonomy source links in Track C; README badge and Track C description updated.

---

## [1.2.1] — 2026-11-26

### Added
- **`install.sh`** — universal installer. One script, no dependencies, no network, no sudo:
  `claude`, `claude-global`, `cursor`, `windsurf`, `continue`, `copilot`, `codex`, `gemini`,
  `aider`, `cline`, `zed`, `print`. Idempotent for the append targets.
- **`llms.txt`** — machine-readable index of the skill, examples and evals, for agents that
  fetch a repository summary before reading it.
- **`img/banner.svg`, `img/gate.svg`** — original diagrams. The gate diagram is documentation:
  it shows the three outcomes and where `BLIND SPOTS` sits.
- **COMPATIBILITY.md** — "Other agents and tools" section covering nine more runtimes, plus
  what actually travels across them (the gate survives truncation; the glyphs do not).

### Fixed
- **Track B, Go: `text/template` no longer implies XSS.** Unescaped output is only XSS when it
  reaches an HTML context. Logs, email bodies, CSVs and CLIs are assessed against the sink that
  actually consumes them; user-controlled template *source* is template injection (CWE-1336)
  in either package. Reported in review.
- **`evals/README.md` run loop** — paths were relative to no single working directory, so the
  documented command could not run. Now anchored at the repo root, writing to the git-ignored
  `evals/results/`. Reported in review.
- **CI stale-path check** failed on the old path recorded in this changelog's history. Both
  greps now exclude `CHANGELOG.md`. Reported in review.

### Changed
- README leads with the banner, carries the gate diagram next to the gate table, and documents
  the installer as the primary path for non-Claude tools.

---

## [1.2.0] — 2026-11-25

### Added
- **Track F — Secrets & Credential Exposure.** Live-vs-placeholder triage, reachability
  (bundle > repo > log > CI variable), blast radius over C/I/A, and a rotate-first fix order.
- **Track B per-language sink tables** — JS/TS, Python, Java, Go, PHP, Ruby, Rust, SQL.
  Includes the constant-feed rule: a dangerous sink fed by a literal is not a finding.
- **BLIND SPOTS section** — mandatory on every report, including clean results. Silence on
  a real bug is the failure mode the gate creates; this closes it.
- **Step 5 — Action Mapping and Disclosure.** Severity → action line, interim mitigation,
  and the third-party reporting path (advisory, CNA, 90-day window).
- **Repo-Scale Mode** — diff-first auditing, one track at a time, and a mandatory scope
  manifest stating how many files were actually read.
- **`examples/`** — three input/output pairs, including a false-positive case showing six
  scanner flags correctly suppressed with reasoning.
- **`evals/`** — 12-case labelled corpus (6 positive, 6 negative) with `expected.yaml`,
  a manual protocol that works on any runtime, and published metrics.
- **`CONTRIBUTING.md`, `SECURITY.md`, issue templates** (bug, false positive, new track).
- **CI** — fails on drift between the canonical skill and the generated copy.

### Changed
- **Skill moved to `skills/security-triage/SKILL.md`** with `.claude/skills/` as a
  generated mirror. Previously shipped as a flat `.claude/skills/security-triage.md`,
  which Claude Code does not discover — one directory per skill, containing `SKILL.md`.
- **Frontmatter rewritten** to fields Claude Code reads (`name`, `description`,
  `when_to_use`, `license`); custom keys moved under `metadata:`. `tracks:` and `author:`
  were silently ignored before.
- **`Claude Skills/` renamed to `skills/`** — the space broke URLs, `curl` and shell
  one-liners.
- README restructured around the gate, the examples, and the evals.

### Fixed
- **`GHSA-wxm3-64fx-cmx9` was listed as a second pedigree finding.** It is the advisory
  that carries CVE-2026-40316 — one vulnerability, not two. Merged, with NVD linked.
- Two copies of the skill had already drifted (385 vs 403 lines, frontmatter on one only).
  Single source of truth plus a CI drift check.

---

## [1.1.0] — 2026-04-20

### Added
- **AGENTS.md** — Agentic discovery metadata, invocation contracts, and GitHub MCP
  workflow for autonomous triage across full repositories
- **Multi-agent compatibility** — Explicit installation and invocation guidance for
  OpenAI Codex, Cursor, Windsurf, Gemini CLI, and GitHub Copilot
- **COMPATIBILITY.md** — Runtime-specific configuration details
- **`.claude/skills/` structure** — Native Claude Code agentic skill path
- **Agentic Mode section** in skill file — GitHub MCP proactive fetch logic,
  SHA-pin auditing grep pattern, graceful degradation when MCP unavailable
- **CVSS agent guidance** — Common agent CVSS errors documented (XSS S:C, CI/CD UI:R,
  transitive dep downgrade, AV:N context adjustment)

### Changed
- Track D (CI/CD) — Expanded `pull_request_target` detection heuristics with
  real-world PoC reference (CVE-2026-40316, GHSA-wxm3-64fx-cmx9)
- Track C (LLM) — LLM01–LLM10 detection heuristics updated to OWASP LLM Top 10 2025
- Confidence gate — False-positive checklist expanded with LLM model-level vs
  application-level distinction as mandatory pre-classification step
- CVSS construction — Component-by-component reasoning now required in all reports;
  base score context adjustment added as mandatory field in AM I AFFECTED section

### Fixed
- LOW confidence issues were appearing in findings summaries in edge cases —
  gate logic now explicitly suppresses them to Notes section only

---

## [1.0.0] — 2026-04-17

### Initial release

- **Confidence-gated triage methodology** — HIGH / MEDIUM / LOW gate applied
  before severity assignment. LOW findings suppressed from reports.
- **5 Triage Tracks:**
  - Track A: CVE / Scanner Alert (Dependabot, Snyk, Trivy, SARIF, npm audit, pip-audit)
  - Track B: Code Snippet (data flow tracing, sink reachability, upstream sanitization)
  - Track C: LLM Application Security (OWASP LLM Top 10, model vs application layer
    distinction, prompt injection, RAG, excessive agency, output handling)
  - Track D: CI/CD & GitHub Actions (script injection CWE-78, pull_request_target
    RCE pattern, SHA pinning, permissions scoping CWE-732)
  - Track E: Container & Infrastructure (Dockerfile, docker-compose, k8s, Helm)
- **Structured triage report format** — FINDING / CLASSIFICATION / WHAT IS THIS /
  AM I AFFECTED / IMPACT / THE FIX / VERIFY IT'S FIXED / REFERENCES
- **CVSS 3.1 construction guidance** — Full vector with component reasoning
- **Multiple findings protocol** — Summary table + individual reports in severity order
  + LOW notes section + combined fix checklist
- **False-positive checklist** — Mandatory pre-HIGH-assignment checks
- **LLM risk rating** — OWASP LLM Risk Rating used for Track C instead of CVSS

### Pedigree
Track D logic derived from original CVE research:
- CVE-2026-40316 (OWASP BLT) — `pull_request_target` + `git show` RCE, CVSS 8.8
- GHSA-wxm3-64fx-cmx9 — Chained RCE via Django model import from untrusted PR
