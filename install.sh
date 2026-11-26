#!/bin/sh
# security-triage — universal installer.
# No dependencies, no network, no sudo. Writes the skill where your tool looks for it.
#
#   ./install.sh              list targets
#   ./install.sh claude       install for Claude Code, this project
#   ./install.sh print        print the skill to stdout

set -eu

REPO_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SKILL="$REPO_DIR/skills/security-triage/SKILL.md"
NAME="security-triage"
MARKER="<!-- security-triage skill (installed by install.sh) -->"
DESC="Confidence-gated security triage: CVE alerts, code, LLM apps, CI/CD, containers, secrets. Suppress false positives behind a HIGH/MEDIUM/LOW gate before assigning severity."

if [ ! -f "$SKILL" ]; then
  echo "error: $SKILL not found — run this from a clone of the repository" >&2
  exit 1
fi

# Skill body without the YAML frontmatter, for tools that want plain markdown.
body() {
  awk 'NR==1 && $0=="---" {fm=1; next} fm && $0=="---" {fm=0; next} !fm' "$SKILL"
}

write_skill() {   # $1 = directory that will hold SKILL.md
  mkdir -p "$1"
  cp "$SKILL" "$1/SKILL.md"
  echo "  wrote      $1/SKILL.md"
}

write_flat() {    # $1 = file, plain markdown
  mkdir -p "$(dirname "$1")"
  { printf -- '---\nname: %s\ndescription: %s\n---\n\n' "$NAME" "$DESC"; body; } > "$1"
  echo "  wrote      $1"
}

append_block() {  # $1 = file, for tools that read one shared instruction file
  if [ -f "$1" ] && grep -qF "$MARKER" "$1"; then
    echo "  present    $1 (already installed)"
    return 0
  fi
  mkdir -p "$(dirname "$1")" 2>/dev/null || true
  { printf '\n%s\n\n' "$MARKER"; body; printf '\n'; } >> "$1"
  echo "  appended   $1"
}

usage() {
  cat <<EOF
security-triage installer

  ./install.sh claude          .claude/skills/$NAME/SKILL.md   (project)
  ./install.sh claude-global   ~/.claude/skills/$NAME/SKILL.md (every project)
  ./install.sh cursor          .cursor/rules/$NAME.mdc
  ./install.sh windsurf        .windsurf/rules/$NAME.md
  ./install.sh continue        .continue/rules/$NAME.md
  ./install.sh copilot         appends to .github/copilot-instructions.md
  ./install.sh codex           appends to AGENTS.md
  ./install.sh gemini          appends to GEMINI.md
  ./install.sh aider           appends to CONVENTIONS.md
  ./install.sh cline           appends to .clinerules
  ./install.sh zed             appends to .rules
  ./install.sh print           stdout, for any other tool

Anything that accepts a system prompt or a rules file works: pipe 'print' into it.

  ./install.sh print | your-agent --system-prompt -
EOF
}

TARGET="${1:-}"

case "$TARGET" in
  claude|claude-code)
    write_skill ".claude/skills/$NAME"
    echo "  next       /$NAME, or paste an artifact and ask"
    ;;
  claude-global)
    write_skill "$HOME/.claude/skills/$NAME"
    echo "  next       /$NAME in any project"
    ;;
  cursor)
    mkdir -p .cursor/rules
    { printf -- '---\ndescription: %s\nalwaysApply: false\n---\n\n' "$DESC"; body; } \
      > ".cursor/rules/$NAME.mdc"
    echo "  wrote      .cursor/rules/$NAME.mdc"
    ;;
  windsurf)
    write_flat ".windsurf/rules/$NAME.md"
    ;;
  continue)
    write_flat ".continue/rules/$NAME.md"
    ;;
  copilot)
    append_block ".github/copilot-instructions.md"
    ;;
  codex)
    append_block "AGENTS.md"
    ;;
  gemini)
    append_block "GEMINI.md"
    ;;
  aider)
    append_block "CONVENTIONS.md"
    echo "  note       run aider with --read CONVENTIONS.md"
    ;;
  cline)
    append_block ".clinerules"
    ;;
  zed)
    append_block ".rules"
    ;;
  print)
    body
    ;;
  ""|-h|--help|help|list)
    usage
    ;;
  *)
    echo "error: unknown target '$TARGET'" >&2
    echo >&2
    usage >&2
    exit 1
    ;;
esac
