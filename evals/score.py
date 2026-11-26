#!/usr/bin/env python3
"""Score eval results against evals/expected.yaml.

Mechanical, deliberately dumb: it looks for an actual finding block, reads the
Track and Severity fields from it, and compares the verdict. It cannot judge
whether the reasoning was right — that is your job, on the cases it flags.

Usage:
    python3 evals/score.py                       # score evals/results/<one label>/
    python3 evals/score.py --results evals/results/claude
    python3 evals/score.py --verbose             # show every failed check
    python3 evals/score.py --md                  # markdown table, for a README

Exit codes: 0 all cases pass, 1 one or more cases failed or are missing,
2 no results found at all.
"""

import argparse
import pathlib
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("needs PyYAML: pip install pyyaml")

BANDS = {"critical": 4, "high": 3, "medium": 2, "low": 1}

# A finding is a FINDING section containing a Confidence field. The report banner
# ("SECURITY TRIAGE REPORT") is emitted for clean results too, so it proves nothing —
# see examples/02-false-positive/output.md, which is a correct clean result wrapped in
# the same header.
RE_FINDING_HEAD = re.compile(r"^\s*#*\s*\**\s*FINDING\b[^\n]*$", re.M)
RE_CONFIDENCE = re.compile(r"^\s*\**\s*Confidence\s*\**\s*:", re.M)
RE_CLEAN = re.compile(r"no\s+(?:high|medium)[^\n]{0,80}finding", re.I)
RE_SEVERITY = re.compile(r"Severity\s*:\s*([^\n]+)", re.I)
RE_TRACK = re.compile(r"Track\s*:\s*([A-F])\b")

# Summary tables only appear when there is at least one finding.
RE_SUMMARY = re.compile(r"FINDINGS SUMMARY", re.I)
RE_SUMMARY_ROW = re.compile(r"[│|]\s*\d+\s*[│|]")

# NOTES is where suppressed, non-findings go. A finding confined to NOTES is a false
# negative by the protocol, so it must not be counted as a report.
RE_NOTES = re.compile(r"^\s*(?:#{1,4}\s*)?\**\s*NOTES\b", re.I)
RE_NOTES_END = re.compile(
    r"^\s*(?:#{1,4}\s*)?\**\s*(?:FIX CHECKLIST|ACTION\b|REFERENCES\b|BLIND SPOTS|━)", re.I
)

BLOCK_CHARS = 900


def strip_notes(text):
    """Remove NOTES blocks, which legitimately contain severity words and Confidence lines."""
    keep, skipping = [], False
    for line in text.splitlines():
        if RE_NOTES.match(line):
            skipping = True
            keep.append("")
            continue
        if skipping and RE_NOTES_END.match(line):
            skipping = False
        if not skipping:
            keep.append(line)
    return "\n".join(keep)


def detect(text):
    """Return (reported, severity, track) from an agent's output."""
    body = strip_notes(text)

    blocks = [body[m.end(): m.end() + BLOCK_CHARS] for m in RE_FINDING_HEAD.finditer(body)]
    confident = [b for b in blocks if RE_CONFIDENCE.search(b)]
    has_clean = bool(RE_CLEAN.search(body))
    summary = bool(RE_SUMMARY.search(body) and RE_SUMMARY_ROW.search(body))

    if summary or confident:
        reported = True
    elif blocks and not has_clean:
        # A FINDING heading with no Confidence line and no clean notice: still a report.
        reported = True
    else:
        reported = False

    scope = confident[0] if confident else (blocks[0] if blocks else body)

    severity = None
    m = RE_SEVERITY.search(scope) or RE_SEVERITY.search(body)
    if m:
        blob = m.group(1).lower()
        for band in ("critical", "high", "medium", "low"):
            if band in blob:
                severity = band
                break
    track = None
    m = RE_TRACK.search(scope) or RE_TRACK.search(body)
    if m:
        track = m.group(1).upper()
    return reported, severity, track


def resolve_results(results_dir):
    """Pick exactly one run. Returns (path, error)."""
    root = pathlib.Path(results_dir)
    if not root.is_dir():
        return None, f"results directory not found: {results_dir}"

    loose = sorted(root.glob("*.md"))
    runs = [d for d in sorted(root.iterdir()) if d.is_dir() and any(d.glob("*.md"))]

    if runs and not loose:
        if len(runs) > 1:
            names = ", ".join(d.name for d in runs)
            return None, (
                f"multiple runs under {results_dir}: {names}\n"
                f"Score one at a time: --results {results_dir}/<label>"
            )
        return runs[0], None
    if loose and not runs:
        return root, None
    if loose and runs:
        return None, (
            f"{results_dir} mixes run directories and loose result files; "
            "pass an explicit --results <label directory>"
        )
    return root, None


def score_case(case, results_dir, verbose):
    cid = case["id"]
    expect_finding = bool(case.get("finding"))
    problems, advisories = [], []

    path = pathlib.Path(results_dir) / f"{cid}.md"
    if not path.is_file():
        return {"id": cid, "status": "MISSING", "problems": ["no result file"], "path": None}

    text = path.read_text(errors="replace")
    reported, severity, track = detect(text)

    if expect_finding and not reported:
        problems.append("expected a finding, got none (false negative — check NOTES)")
    if not expect_finding and reported:
        problems.append("expected no finding, got one (false positive)")

    if expect_finding:
        want_track = case.get("track")
        if want_track and track != want_track:
            problems.append(f"track {track or '?'} != {want_track}")
        want_sev = case.get("severity")
        if want_sev and severity:
            if abs(BANDS.get(severity, 0) - BANDS.get(want_sev, 0)) > 1:
                problems.append(f"severity {severity} more than one band from {want_sev}")
        elif want_sev and not severity:
            problems.append("no severity line found")

    # must_not is checked against the text with the clean notice removed: that sentence
    # legitimately contains "HIGH" and "MEDIUM".
    scrubbed = RE_CLEAN.sub(" ", text)
    lowered = scrubbed.lower()
    for needle in case.get("must_mention") or []:
        if needle.lower() not in lowered:
            (problems if expect_finding else advisories).append(f"missing mention: {needle!r}")
    for needle in case.get("must_not") or []:
        if needle.lower() in lowered:
            problems.append(f"contains forbidden: {needle!r}")

    return {
        "id": cid,
        "status": "pass" if not problems else "FAIL",
        "problems": problems,
        "advisories": advisories,
        "path": str(path),
        "reported": reported,
        "severity": severity,
        "track": track,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="evals/results")
    ap.add_argument("--expected", default="evals/expected.yaml")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--md", action="store_true")
    args = ap.parse_args()

    results_dir, err = resolve_results(args.results)
    if err:
        print(err, file=sys.stderr)
        return 2

    cases = yaml.safe_load(pathlib.Path(args.expected).read_text())["cases"]
    rows = [score_case(c, results_dir, args.verbose) for c in cases]

    pos = [r for r, c in zip(rows, cases) if c.get("finding")]
    neg = [r for r, c in zip(rows, cases) if not c.get("finding")]
    recall = sum(1 for r in pos if r["status"] == "pass")
    fp = sum(1 for r in neg if r.get("reported"))
    missing = [r for r in rows if r["status"] == "MISSING"]
    track_ok = sum(
        1 for r, c in zip(rows, cases)
        if c.get("finding") and r.get("track") == c.get("track")
    )

    if args.md:
        print("| Case | Expect | Got | Status |")
        print("|---|---|---|---|")
        for r, c in zip(rows, cases):
            want = "finding" if c.get("finding") else "clean"
            got = "—" if r["status"] == "MISSING" else ("finding" if r.get("reported") else "clean")
            print(f"| `{r['id']}` | {want} | {got} | {r['status']} |")
    else:
        print(f"results  {results_dir}")
        print()
        print(f"{'case':38} {'expect':8} {'got':8} status")
        print("-" * 70)
        for r, c in zip(rows, cases):
            want = "finding" if c.get("finding") else "clean"
            got = "—" if r["status"] == "MISSING" else ("finding" if r.get("reported") else "clean")
            print(f"{r['id']:38} {want:8} {got:8} {r['status']}")
            if args.verbose:
                for p in r["problems"]:
                    print(f"    x {p}")
                for a in r.get("advisories", []):
                    print(f"    - {a}")

    total = len(rows)
    print()
    print(f"cases              {total}")
    print(f"missing results    {len(missing)}")
    print(f"recall             {recall}/{len(pos)}")
    print(f"false positives    {fp}/{len(neg)}")
    print(f"track accuracy     {track_ok}/{len(pos)}")
    print()

    if len(missing) == total:
        print("No results found. Run evals/run.sh first.")
        return 2

    failed = [r for r in rows if r["status"] == "FAIL"]
    if failed or missing:
        if missing:
            print(f"{len(missing)} case(s) have no result. An incomplete corpus is not a")
            print("score — re-run the full corpus before quoting a number.")
        if failed:
            print(f"{len(failed)} case(s) failed. Re-read the output before assuming the")
            print("skill is wrong — the case or this scorer may be. Both are code.")
        return 1

    print("All cases passed. Publish the numbers — with the model and date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
