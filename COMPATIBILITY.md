# Compatibility

The Security Triage Skill is plain markdown. It works in any agent runtime
that accepts a system prompt or context file.

Primary format: `.claude/skills/` (Claude Code / Claude native)
Secondary: Any runtime — the methodology is model-agnostic.

---

## Claude (Primary)

### Claude.ai — Project Instructions

1. Open a Claude Project
2. Go to Project Instructions
3. Paste the full contents of `skills/security-triage/SKILL.md`
4. The skill is now active for all conversations in that project

### Claude Code — Agentic

```bash
# Clone and wire to your project
git clone https://github.com/S3DFX-CYBER/Claude-Skills-Security.git
mkdir -p /your/project/.claude/skills/security-triage/
cp "Claude-Skills-Security/skills/security-triage/SKILL.md" \
   /your/project/.claude/skills/security-triage/SKILL.md
```

Claude Code agents will discover the skill via `.claude/skills/` on startup.

### Claude API

```python
import anthropic

with open("skills/security-triage/SKILL.md") as f:
    skill = f.read()

client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    system=skill,
    messages=[
        {"role": "user", "content": "Triage this workflow file:\n\n<paste YAML>"}
    ]
)
```

---

## OpenAI Codex / Responses API

```python
from openai import OpenAI

with open("skills/security-triage/SKILL.md") as f:
    skill = f.read()

client = OpenAI()
response = client.responses.create(
    model="codex-mini-latest",
    instructions=skill,
    input="Triage this Dockerfile:\n\n<paste Dockerfile>"
)
print(response.output_text)
```

### Chat Completions API

```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": skill},
        {"role": "user", "content": "Triage this code:\n\n<paste code>"}
    ]
)
```

---

## Cursor

Create `.cursorrules` in your project root:

```
You are operating with the Security Triage Skill active.

Follow the triage methodology defined in:
https://github.com/S3DFX-CYBER/Claude-Skills-Security/blob/main/skills/security-triage/SKILL.md

Key rules:
- Apply the confidence gate (HIGH/MEDIUM/LOW) before every finding
- Never report LOW confidence issues as security findings
- Produce the structured triage report format for every HIGH/MEDIUM finding
- Re-evaluate CVSS base score against the actual deployment context
- Distinguish LLM model-level from application-level before triaging
```

Or paste the full skill content directly into `.cursorrules` for offline use.

---

## Windsurf

Add to your Windsurf rules file (`.windsurfrules` or via the Rules panel):

```
Security triage methodology: apply the confidence gate (HIGH/MEDIUM/LOW)
before assigning severity to any finding. Only HIGH and MEDIUM findings
get triage reports. LOW findings are noted briefly, never reported as findings.

Full methodology: [paste Security-Triage-Skills.md content here]
```

---

## GitHub Copilot

Create `.github/copilot-instructions.md`:

```markdown
## Security Triage

When reviewing code, workflow files, Dockerfiles, or dependencies for security issues,
apply the confidence-gated triage methodology from:
Claude-Skills-Security/skills/security-triage/SKILL.md

Confidence gate:
- HIGH: pattern confirmed + attacker input path confirmed + exploitable in context
- MEDIUM: pattern found, input or context unclear
- LOW: theoretical only — do NOT report as a finding

Output format: structured triage report (FINDING / AM I AFFECTED / IMPACT / THE FIX)
```

---

## Gemini CLI

```bash
# Single invocation
gemini -s "$(cat 'skills/security-triage/SKILL.md')" \
  "Triage this GitHub Actions workflow:\n\n$(cat .github/workflows/ci.yml)"

# As a shell function
triage() {
  local skill="$(cat '/path/to/skills/security-triage/SKILL.md')"
  gemini -s "$skill" "Triage this: $1"
}

# Usage
triage "$(cat Dockerfile)"
triage "CVE-2024-21536 — is this affecting my Express app?"
```

---

## LangChain / LangGraph

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage

with open("skills/security-triage/SKILL.md") as f:
    skill = f.read()

llm = ChatAnthropic(model="claude-sonnet-4-20250514")

def triage_node(state):
    messages = [
        SystemMessage(content=skill),
        HumanMessage(content=f"Triage this artifact:\n\n{state['artifact']}")
    ]
    response = llm.invoke(messages)
    return {"triage_report": response.content}
```

---

## CrewAI

```python
from crewai import Agent, Task
from langchain_anthropic import ChatAnthropic

with open("skills/security-triage/SKILL.md") as f:
    skill = f.read()

security_researcher = Agent(
    role="Senior Security Researcher",
    goal="Perform confidence-gated security triage on provided artifacts",
    backstory=skill,
    llm=ChatAnthropic(model="claude-sonnet-4-20250514"),
    verbose=True
)

triage_task = Task(
    description="Triage the following artifact: {artifact}",
    agent=security_researcher,
    expected_output="Structured triage report with confidence gate applied"
)
```

---

## Any OpenAI-compatible API

The skill works as a `system` message with any OpenAI-compatible endpoint
(Ollama, LM Studio, Groq, Together, Mistral, etc.):

```python
import openai

with open("skills/security-triage/SKILL.md") as f:
    skill = f.read()

client = openai.OpenAI(
    base_url="http://localhost:11434/v1",  # or any compatible endpoint
    api_key="placeholder"
)

response = client.chat.completions.create(
    model="your-model",
    messages=[
        {"role": "system", "content": skill},
        {"role": "user", "content": "Triage this: <paste artifact>"}
    ]
)
```

**Note on local models:** The confidence gate and structured output require
strong instruction-following capability. Models below ~13B parameters may
not reliably apply the gate or produce consistent report formatting.
Recommended: Claude Sonnet, GPT-4o, Gemini 1.5 Pro, or equivalent.

---

## Runtime Comparison

| Feature | Claude | Codex | Cursor | Gemini CLI | Local LLM |
|---------|--------|-------|--------|------------|-----------|
| Native skill format | ✅ `.claude/skills/` | ❌ | ❌ | ❌ | ❌ |
| System prompt injection | ✅ | ✅ | ✅ via rules | ✅ via `-s` | ✅ |
| GitHub MCP (agentic mode) | ✅ | ⚠️ custom | ❌ | ❌ | ❌ |
| CVSS construction accuracy | High | High | Medium | High | Variable |
| Confidence gate reliability | High | High | Medium | High | Variable |
| Recommended for prod triage | ✅ | ✅ | ⚠️ review output | ✅ | ⚠️ test first |

---

## Other Agents and Tools

Everything in this table uses the same artifact: the markdown body of
`skills/security-triage/SKILL.md`, frontmatter stripped. `./install.sh <target>` writes it
in the right place.

| Tool | Target | Mechanism |
|---|---|---|
| Cursor | `./install.sh cursor` | `.cursor/rules/*.mdc`, `alwaysApply: false` |
| Windsurf | `./install.sh windsurf` | `.windsurf/rules/` |
| Continue | `./install.sh continue` | `.continue/rules/` |
| GitHub Copilot | `./install.sh copilot` | `.github/copilot-instructions.md` |
| Codex / OpenAI agents | `./install.sh codex` | `AGENTS.md` |
| Gemini CLI | `./install.sh gemini` | `GEMINI.md` |
| Aider | `./install.sh aider` | `CONVENTIONS.md` via `--read` |
| Cline | `./install.sh cline` | `.clinerules` |
| Zed | `./install.sh zed` | `.rules` |
| Any other tool | `./install.sh print` | stdout — pipe into a system prompt |

```bash
# Anything that takes a system prompt or a prompt file
./install.sh print > /tmp/security-triage.md
your-agent --system-prompt /tmp/security-triage.md "triage this Dockerfile: $(cat Dockerfile)"

# Anything that takes a single concatenated prompt
your-agent "$(./install.sh print)"$'

'"$(cat .github/workflows/deploy.yml)"
```

### What actually travels

Two things matter across runtimes, and neither is the file format:

1. **The gate must survive.** A runtime that truncates context or summarises the system prompt
   will drop the LOW-suppression rule first, because it reads as a restriction. If you see
   findings reported without a confidence level, the gate was lost — shorten what you paste
   to the gate, the track definitions and the report format.
2. **Output format is per-runtime.** The box-drawing characters in the report template render
   inconsistently in some UIs. The structure is what matters, not the glyphs; tell the agent to
   keep the section order if your client mangles the borders.

### Local models

The gate and the structured output both depend on instruction-following. Below roughly 13B
parameters, expect the gate to be skipped and the report to be flattened. Test with
`evals/` before trusting a small model in a review path.
