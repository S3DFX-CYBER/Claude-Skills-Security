# Changelog

All notable changes to Claude-Skills-Security are documented here.

Format: [Semantic Versioning](https://semver.org/)
Methodology: Exploitability-first triage. Every change is grounded in field findings.

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
