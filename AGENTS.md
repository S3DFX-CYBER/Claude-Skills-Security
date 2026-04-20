# AGENTS.md

This file describes the agentic capabilities, invocation contracts, and skill
discovery metadata for the Claude-Skills-Security repository.

Compatible with: Claude Code, OpenAI Codex agents, AutoGPT, LangGraph, CrewAI,
and any agent runtime that reads AGENTS.md for capability discovery.

---

## Available Skills

### security-triage

**File:** `Claude Skills/Security-Triage-Skills.md`
**Version:** 1.1.0
**Type:** Triage methodology / system prompt skill

A confidence-gated security triage skill for AI agents. Covers 5 tracks:
CVE analysis, code review, LLM application security, CI/CD hardening,
and container/infrastructure review.

**When to invoke:**
- User pastes a CVE ID, scanner output (Snyk, Dependabot, Trivy, SARIF), or audit report
- User pastes source code and asks about security
- User pastes a GitHub Actions workflow file
- User pastes a Dockerfile, docker-compose.yml, or k8s YAML
- User asks about prompt injection, LLM security, RAG pipelines, or AI agents
- User asks "is this safe?", "is this vulnerable?", or "what's the risk here?"

**When NOT to invoke:**
- General coding help with no security context
- Architecture questions with no specific artifact to triage
- Compliance checklists (this skill is exploitability-focused, not compliance-focused)

---

## Invocation Contract

### Input format

The skill accepts any of the following as input:

```
1. Raw text
   Paste the artifact directly. The skill auto-classifies the track.

2. Labeled input (preferred for multi-artifact sessions)
   TRACK: D
   ARTIFACT:
   <paste workflow YAML here>

3. Mixed input
   Multiple artifacts can be pasted together.
   The skill will produce a findings summary table + individual reports.
```

### Output contract

Every invocation produces one of:

**A. Findings summary + individual triage reports** (one or more HIGH/MEDIUM findings)
```
FINDINGS SUMMARY
┌────┬──────────────┬────────────┬──────────┬───────┐
│ #  │ Title        │ Confidence │ Severity │ Track │
└────┴──────────────┴────────────┴──────────┴───────┘

[Individual triage reports follow in severity order]

NOTES (LOW confidence issues — informational only)
FIX CHECKLIST
```

**B. Clean result** (no HIGH/MEDIUM findings)
```
No HIGH or MEDIUM confidence findings identified.
[Optional: LOW confidence notes if present]
```

The skill NEVER produces vague warnings. If a finding cannot be assigned
HIGH or MEDIUM confidence, it does not appear as a finding.

---

## Agentic Workflow: GitHub MCP

When a GitHub MCP server is connected, the skill operates in agentic mode:

```
1. Fetch workflow files proactively
   GET /repos/{owner}/{repo}/contents/.github/workflows

2. Check for existing Dependabot fix PRs
   GET /repos/{owner}/{repo}/dependabot/alerts

3. Cross-reference dangerous patterns across ALL workflow files simultaneously

4. Audit SHA-pinning across all actions:
   Pattern: uses: .+@[^a-f0-9]{40} flags non-SHA pins

5. Use web search to check for public PoCs or active exploitation of CVEs
```

Announce each fetch before executing. Show raw findings before triaging.
Degrade gracefully if MCP unavailable — prompt user to paste relevant files.

---

## Confidence Gate (Agent Decision Logic)

Agents MUST apply this gate before assigning severity to any finding.

```python
def confidence_gate(finding):
    if (
        finding.vulnerable_pattern_confirmed and
        finding.attacker_controlled_input_confirmed and
        finding.exploitable_in_context
    ):
        return "HIGH"   # produce full triage report
    
    elif (
        finding.vulnerable_pattern_found and
        (not finding.input_source_clear or not finding.context_fully_visible)
    ):
        return "MEDIUM" # produce triage report with caveat
    
    else:
        return "LOW"    # do NOT produce a finding — notes section only
```

**False-positive checks before assigning HIGH:**
- Is input actually attacker-controlled, or server config / internal data?
- Does sanitization or validation run upstream that wasn't shown?
- Is the vulnerable code path reachable from an unauthenticated entry point?
- For CI/CD: is the trigger `pull_request` (safe) or `pull_request_target` (dangerous)?
- For LLM: is this model-level (unfixable in code) or application-level (fixable)?
- For CVEs: is the vulnerable function actually called, or just present as a transitive dep?

---

## Track Classification (Agent Auto-Routing)

```
Input contains CVE ID, Dependabot alert, Snyk/Trivy/SARIF output
→ Route to Track A: CVE / Scanner Alert

Input contains source code in any language
→ Route to Track B: Code Snippet

Input contains prompt template, LLM app code, RAG pipeline, agent tools, system prompt
→ Route to Track C: LLM Application Security

Input contains .github/workflows/*.yml or CI config
→ Route to Track D: CI/CD & GitHub Actions

Input contains Dockerfile, docker-compose.yml, k8s YAML, Helm chart
→ Route to Track E: Container & Infrastructure
```

Multiple tracks can be active simultaneously. Classify ALL applicable tracks
before triaging.

---

## CVSS Construction (Agent Guidance)

Always construct full vector: `CVSS:3.1/AV:_/AC:_/PR:_/UI:_/S:_/C:_/I:_/A:_`

Common agent errors to avoid:
- XSS findings: use `S:C` (scope change — crosses browser boundary), not `S:U`
- CI/CD attacks requiring maintainer approval: `UI:R`, not `UI:N`
- Transitive dependency with no direct call: do NOT use base CVSS score
- Internal-only service: `AV:N` overstates real risk — note this explicitly in report

For LLM findings (Track C): use OWASP LLM Risk Rating, NOT CVSS.
CVSS maps poorly to LLM application layer vulnerabilities.

---

## Version History

See [CHANGELOG.md](CHANGELOG.md)

---

## Repository Structure

```
Claude-Skills-Security/
├── Claude Skills/
│   └── Security-Triage-Skills.md   # Core skill file
├── .claude/
│   └── skills/
│       └── security-triage.md      # Claude Code symlink/copy
├── AGENTS.md                        # This file — agentic discovery
├── CHANGELOG.md                     # Version history
├── COMPATIBILITY.md                 # Runtime compatibility details
├── LICENSE                          # MIT
└── README.md                        # Human-readable docs
```
