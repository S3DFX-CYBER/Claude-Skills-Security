#!/bin/sh
# Proves the eval harness scores correctly, using stubs that already know the answers.
#
# This is NOT a score of the skill. It tests run.sh and score.py: prompt building,
# finding detection, track and severity parsing, must_mention and must_not handling,
# and the failure paths. If any check here is wrong, the harness is broken and every
# number it produces is worthless.
#
# Three stubs, three properties:
#   1. correct output  -> 12/12, including clean results wrapped in the report banner
#   2. flags everything -> caught as false positives
#   3. finding in NOTES -> caught as a false negative, not scored as a pass

set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"; rm -rf "$ROOT/evals/results/_selftest"' EXIT

# --- 1. A stub that produces the expected verdict, in the skill's real output shape.
cat > "$TMP/good.sh" <<'STUB'
#!/bin/sh
body=$(awk '/^INPUT ARTIFACT$/{f=1;next} f' | head -40)
emit() { printf 'SECURITY TRIAGE REPORT\n\nFINDING\n  Title      : stub\n  Track      : %s\n  Confidence : HIGH\n  Severity   : %s\n\n%s\n' "$1" "$2" "$3"; }
clean() {
  # The real clean format: the report banner is still emitted. A scorer that treats the
  # banner as a finding will mark this a false positive.
  printf 'SECURITY TRIAGE REPORT\n\nNo HIGH or MEDIUM confidence findings identified.\n\nNOTES (informational only)\n%s\n' "$1"
}
case "$body" in
  *"git show"*)           emit D Critical "pull_request_target GITHUB_TOKEN git show UI:R" ;;
  *"subprocess.run(code"*) emit C Critical "LLM10 shell=True" ;;
  *STRIPE_SECRET_KEY*)    emit F High     "rotate layer" ;;
  *"pull_request.title"*) emit D High     "CWE-78 pull_request.title" ;;
  *"request.args.get"*)   emit B Critical "CWE-89 parameterised" ;;
  *ghp_*)                 emit F Critical "rotate ghp_" ;;
  *) clean "constant literal config transitive not imported pinned checked out USER digest" ;;
esac
STUB

# --- 2. Reports a finding for everything.
cat > "$TMP/bad.sh" <<'STUB'
#!/bin/sh
cat > /dev/null
printf 'SECURITY TRIAGE REPORT\n\nFINDING\n  Track      : D\n  Confidence : HIGH\n  Severity   : Critical\n'
STUB

# --- 3. Buries the finding in NOTES, which the protocol counts as a false negative.
cat > "$TMP/notes.sh" <<'STUB'
#!/bin/sh
cat > /dev/null
printf 'SECURITY TRIAGE REPORT\n\nNo HIGH or MEDIUM confidence findings identified.\n\nNOTES\n\nConfidence : HIGH\nTrack      : B\nSeverity   : Critical\nCWE-89 parameterised\n'
STUB

chmod +x "$TMP/good.sh" "$TMP/bad.sh" "$TMP/notes.sh"
mkdir -p evals/results

pass() { printf '  pass\n'; }
fail() { printf '  FAIL — %s\n' "$1"; exit 1; }

echo "selftest: correct output scores 12/12"
./evals/run.sh --agent "$TMP/good.sh" --label _selftest >/dev/null
out=$(python3 evals/score.py --results evals/results/_selftest 2>&1) \
  || fail "a correct agent does not score 12/12"
for metric in "recall             6/6" "false positives    0/6" "severity agreement 6/6"; do
  case "$out" in
    *"$metric"*) : ;;
    *) fail "expected '$metric' in the summary" ;;
  esac
done
pass

echo "selftest: clean result inside the report banner is not a finding"
./evals/run.sh --agent "$TMP/good.sh" --label _selftest --case neg-01-innerhtml-config >/dev/null
python3 evals/score.py --results evals/results/_selftest >/dev/null 2>&1 || true
out=$(python3 evals/score.py --results evals/results/_selftest 2>&1 || true)
case "$out" in
  *"neg-01-innerhtml-config"*"FAIL"*) fail "the report banner was read as a finding" ;;
  *) pass ;;
esac

echo "selftest: an agent that flags everything is caught as 6/6 false positives"
rm -rf evals/results/_selftest
./evals/run.sh --agent "$TMP/bad.sh" --label _selftest >/dev/null
out=$(python3 evals/score.py --results evals/results/_selftest 2>&1 || true)
case "$out" in
  *"false positives    6/6"*) pass ;;
  *"false positives"*)        fail "wrong false-positive count — negatives are no longer detected" ;;
  *)                          fail "scorer crashed or printed nothing useful" ;;
esac

echo "selftest: a finding buried in NOTES is caught"
rm -rf evals/results/_selftest
./evals/run.sh --agent "$TMP/notes.sh" --label _selftest --case pos-05-sql-concat >/dev/null
python3 evals/score.py --results evals/results/_selftest >/dev/null \
  && fail "a finding buried in NOTES was scored as a pass" || pass

echo "selftest: missing results fail instead of passing"
rm -rf evals/results/_selftest
./evals/run.sh --agent "$TMP/good.sh" --label _selftest --case pos-01-pr-target-git-show >/dev/null
python3 evals/score.py --results evals/results/_selftest >/dev/null \
  && fail "an incomplete corpus scored as a pass" || pass

echo "selftest: two runs present is an error, not a coin flip"
rm -rf evals/results/_selftest
mkdir -p evals/results/_selftest/a evals/results/_selftest/b
printf 'x\n' > evals/results/_selftest/a/pos-01-pr-target-git-show.md
printf 'x\n' > evals/results/_selftest/b/pos-01-pr-target-git-show.md
python3 evals/score.py --results evals/results/_selftest >/dev/null 2>&1 \
  && fail "two runs were scored without an explicit label" || pass

echo "harness ok"
