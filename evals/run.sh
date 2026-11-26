#!/bin/sh
# Run the eval corpus against any agent CLI.
#
# The only requirement for the agent command: it reads the prompt on stdin and
# writes the answer to stdout. Everything else is your tool's business.
#
#   ./evals/run.sh --agent "claude -p"
#   ./evals/run.sh --agent "codex exec --full-auto -" --label codex
#   ./evals/run.sh --agent "ollama run qwen2.5-coder" --label ollama-qwen
#   ./evals/run.sh --dry-run            # show what would run, run nothing
#
# Results land in evals/results/<label>/<case-id>.md
# Score them with: python3 evals/score.py --verbose

set -eu

AGENT=""
LABEL=""
DRY=0
ONLY=""

while [ $# -gt 0 ]; do
  case "$1" in
    --agent)  AGENT="${2:-}"; shift 2 ;;
    --label)  LABEL="${2:-}"; shift 2 ;;
    --case)   ONLY="${2:-}"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    -h|--help)
      sed -n '2,18p' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) echo "error: unknown argument '$1'" >&2; exit 1 ;;
  esac
done

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
SKILL="$ROOT/skills/security-triage/SKILL.md"
CASES="$ROOT/evals/cases"

if [ -z "$AGENT" ] && [ "$DRY" -eq 0 ]; then
  echo "error: --agent is required (or --dry-run to preview)" >&2
  echo >&2
  sed -n '2,18p' "$0" | sed 's/^# \{0,1\}//' >&2
  exit 1
fi

[ -f "$SKILL" ] || { echo "error: $SKILL not found" >&2; exit 1; }

# A readable label for the results directory.
if [ -z "$LABEL" ]; then
  LABEL=$(printf '%s' "$AGENT" | tr -cs 'A-Za-z0-9._-' '-' | sed 's/^-//;s/-$//' | cut -c1-40)
fi
OUT="$ROOT/evals/results/$LABEL"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

echo "agent    $AGENT"
echo "label    $LABEL"
echo "skill    ${SKILL#$ROOT/}"
echo "results  ${OUT#$ROOT/}"
echo

n=0
ok=0
fail=0

for dir in "$CASES"/*/; do
  id=$(basename "$dir")
  [ -n "$ONLY" ] && [ "$id" != "$ONLY" ] && continue

  artifact=$(ls "$dir"artifact.* 2>/dev/null | head -1 || true)
  if [ -z "$artifact" ]; then
    echo "  skip   $id (no artifact)"
    continue
  fi

  prompt="$TMP/$id.prompt"
  # Skill first, then the artifact, with no hint about what to look for.
  {
    cat "$SKILL"
    printf '\n\n---\n\nINPUT ARTIFACT\n\n'
    cat "$artifact"
    printf '\n'
  } > "$prompt"

  n=$((n + 1))

  if [ "$DRY" -eq 1 ]; then
    echo "  would  $id  ($(wc -l < "$prompt") line prompt)"
    continue
  fi

  mkdir -p "$OUT"
  printf '  run    %-38s ' "$id"
  if sh -c "$AGENT" < "$prompt" > "$OUT/$id.md" 2> "$OUT/$id.err"; then
    lines=$(wc -l < "$OUT/$id.md")
    echo "ok (${lines} lines)"
    ok=$((ok + 1))
  else
    echo "FAILED (see $id.err)"
    fail=$((fail + 1))
  fi
done

echo
if [ "$DRY" -eq 1 ]; then
  echo "$n case(s) ready. Re-run without --dry-run to execute."
  exit 0
fi

echo "$ok succeeded, $fail failed, $n total"
echo
echo "score:  python3 evals/score.py --verbose"
[ "$fail" -eq 0 ] || exit 1
