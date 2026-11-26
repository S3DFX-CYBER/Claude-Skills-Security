#!/usr/bin/env python3
"""Score eval results against evals/expected.yaml.

Mechanical, deliberately dumb: it looks for the report structure the skill is
supposed to emit and compares the verdict. It cannot judge whether the reasoning
was right — that is your job, on the cases it flags.

Usage:
    python3 evals/score.py                       # score evals/results/**
    python3 evals/score.py --results DIR
    python3 evals/score.py --verbose             # show every failed check
    python3 evals/score.py --md                  # markdown table, for a README

Exit code is 0 when every case passes, 1 otherwise, so it works in CI.
"""

import argparse
import os
import pathlib
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("needs PyYAML: pip install pyyaml")

BANDS = {"critical": 4, "high": 3, "medium": 2, "low": 1}

# What a produced finding looks like.
RE_REPORT = re.compile(r"SECURITY TRIAGE REPORT|FINDINGS SUMMARY", re.I)
RE_CONFIDENCE = re.compile(r"^\s*Confidence\s*:", re.M)
RE_CLEAN = re.compile(r"no\s+(?:high|medium)[^\n]{0,80}finding", re.I)
RE_SEVERITY = re.compile(r"Severity\s*:\s*([^\n]+)", re.I)
RE_TRACK = re.compile(r"Track\s*:\s*([A-F])\b")
RE_FINDING_TITLE = re.compile(r"^\s*Title\s*:\s*(.+)$", re.M)


def detect(text):
    """Return (reported, severity, track) from an agent's output."""
    report = bool(RE_REPORT.search(text))
    confidence = bool(RE_CONFIDENCE.search(text))
    clean = bool(RE_CLEAN.search(text))

    if report:
        reported = True
    elif confidence and not clean:
        reported = True
    else:
        reported = False

    severity = None
    m = RE_SEVERITY.search(text)
    if m:
        blob = m.group(1).lower()
        for band in ("critical", "high", "medium", "low"):
            if band in blob:
                severity = band
                break
    track = None
    m = RE_TRACK.search(text)
    if m:
        track = m.group(1).upper()
    return reported, severity, track


def find_result(results_dir, case_id):
    hits = sorted(pathlib.Path(results_dir).rglob(f"{case_id}.md"))
    return hits[0] if hits else None


def score_case(case, results_dir, verbose):
    cid = case["id"]
    expect_finding = bool(case.get("finding"))
    problems, advisories = [], []

    path = find_result(results_dir, cid)
    if path is None:
        return {"id": cid, "status": "MISSING", "problems": ["no result file"], "path": None}

    text = path.read_text(errors="replace")
    reported, severity, track = detect(text)

    if expect_finding and not reported:
        problems.append("expected a finding, got none (false negative)")
    if not expect_finding and reported:
        problems.append("expected no finding, got one (false positive)")

    if expect_finding:
        want_track = case.get("track")
        if want_track and track != want_track:
            problems.append(f"track {track or '?'} != {want_track}")
        want_sev = case.get("severity")
        if want_sev and severity:
            delta = abs(BANDS.get(severity, 0) - BANDS.get(want_sev, 0))
            if delta > 1:
                problems.append(f"severity {severity} more than one band from {want_sev}")
        elif want_sev and not severity:
            problems.append("no severity line found")

    # The clean notice legitimately contains "HIGH" and "MEDIUM". Strip it before
    # checking must_not, or every negative case fails on its own correct output.
    scrubbed = RE_CLEAN.sub(" ", text)
    scrubbed = re.sub(r"no\s+(high|medium)\s+confidence[^\n]*", " ", scrubbed, flags=re.I)
    lowered = scrubbed.lower()
    for needle in case.get("must_mention") or []:
        ok = needle.lower() in lowered
        if not ok:
            # Advisory on clean results: a bare "no findings" is acceptable output,
            # it just makes the note weaker.
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

    cases = yaml.safe_load(pathlib.Path(args.expected).read_text())["cases"]
    rows = [score_case(c, args.results, args.verbose) for c in cases]

    pos = [r for r, c in zip(rows, cases) if c.get("finding")]
    neg = [r for r, c in zip(rows, cases) if not c.get("finding")]
    recall = sum(1 for r in pos if r["status"] == "pass")
    fp = sum(1 for r in neg if r.get("reported"))
    missing = sum(1 for r in rows if r["status"] == "MISSING")
    track_ok = sum(
        1 for r, c in zip(rows, cases)
        if c.get("finding") and r.get("track") == c.get("track")
    )

    if args.md:
        print("| Case | Expect | Got | Status |")
        print("|---|---|---|---|")
        for r, c in zip(rows, cases):
            got = "finding" if r.get("reported") else "clean"
            if r["status"] == "MISSING":
                got = "—"
            want = "finding" if c.get("finding") else "clean"
            print(f"| `{r['id']}` | {want} | {got} | {r['status']} |")
        print()
    else:
        print(f"{'case':38} {'expect':8} {'got':8} {'status'}")
        print("-" * 70)
        for r, c in zip(rows, cases):
            want = "finding" if c.get("finding") else "clean"
            got = "—" if r["status"] == "MISSING" else ("finding" if r.get("reported") else "clean")
            print(f"{r['id']:38} {want:8} {got:8} {r['status']}")
            if args.verbose:
                for p in r["problems"]:
                    print(f"    ✗ {p}")
                for a in r.get("advisories", []):
                    print(f"    · {a}")

    total = len(rows)
    print()
    print(f"cases              {total}")
    print(f"missing results    {missing}")
    print(f"recall             {recall}/{len(pos)}")
    print(f"false positives    {fp}/{len(neg)}")
    print(f"track accuracy     {track_ok}/{len(pos)}")
    print()

    if missing == total:
        print("No results found. Run evals/run.sh first.")
        return 2

    failures = [r for r in rows if r["status"] == "FAIL"]
    if failures:
        print(f"{len(failures)} case(s) failed. Re-read the output before assuming the")
        print("skill is wrong — the case or this scorer may be. Both are code.")
        return 1
    print("All cases passed. Publish the numbers — with the model and date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
