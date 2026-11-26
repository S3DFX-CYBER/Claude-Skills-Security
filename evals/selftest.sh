#!/bin/sh
# Proves the eval harness scores correctly, using a stub that already knows the answers.
#
# This is NOT a score of the skill. It tests run.sh and score.py: prompt building,
# finding detection, track and severity parsing, must_mention and must_not handling.
# A correct stub must score 12/12; a stub that reports everything must score 6/6
# false positives. If either is wrong, the harness is broken and any published score
# is worthless.

set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"; rm -rf "$ROOT/evals/results/_selftest"' EXIT

# A stub that produces the expected verdict for each case.
cat > "$TMP/good.sh" <<'STUB'
#!/bin/sh
body=$(awk '/^INPUT ARTIFACT$/{f=1;next} f' | head -40)
emit() { printf 'SECURITY TRIAGE REPORT\n\nFINDING\n  Title      : stub\n  Track      : %s\n  Confidence : HIGH\n  Severity   : %s\n\n%s\n' "$1" "$2" "$3"; }
case "$body" in
  *"git show"*)           emit D Critical "pull_request_target GITHUB_TOKEN git show UI:R" ;;
  *"subprocess.run(code"*) emit C Critical "LLM10 shell=True" ;;
  *STRIPE_SECRET_KEY*)    emit F High     "rotate layer" ;;
  *"pull_request.title"*) emit D High     "CWE-78 pull_request.title" ;;
  *"request.args.get"*)   emit B Critical "CWE-89 parameterised" ;;
  *ghp_*)                 emit F Critical "rotate ghp_" ;;
  *) printf 'No HIGH or MEDIUM confidence findings identified.\n\nNOTES\nconstant literal config transitive not imported pinned checked out USER digest\n' ;;
esac
STUB

# A stub that reports a finding for everything — the failure path.
cat > "$TMP/bad.sh" <<'STUB'
#!/bin/sh
cat > /dev/null
printf 'SECURITY TRIAGE REPORT\n\nFINDING\n  Track      : D\n  Confidence : HIGH\n  Severity   : Critical\n'
STUB

chmod +x "$TMP/good.sh" "$TMP/bad.sh"
mkdir -p evals/results

echo "selftest: correct stub should score 12/12"
./evals/run.sh --agent "$TMP/good.sh" --label _selftest >/dev/null
if python3 evals/score.py --results evals/results/_selftest >/dev/null; then
  echo "  pass"
else
  echo "  FAIL — the harness mis-scores a correct agent"; exit 1
fi

echo "selftest: over-reporting stub should be caught as 6/6 false positives"
rm -rf evals/results/_selftest
./evals/run.sh --agent "$TMP/bad.sh" --label _selftest >/dev/null
if python3 evals/score.py --results evals/results/_selftest >/dev/null; then
  echo "  FAIL — the harness accepted an agent that flags everything"; exit 1
else
  echo "  pass"
fi

echo "harness ok"
