#!/usr/bin/env python3
"""Audit a salary-floor.log.json against its sources. Reports what it found; it does not fix anything.

Checks:
  A1 every posting in postings.json appears exactly once in the log, with a decision and a reason
  A2 every floor value re-reads from the cited metro_oews.csv line, in the cited column
  A3 no posting that failed G1/G2/G3 carries a floor that the decision then used (Unresolved / Skip have no comparison)
  A4 every company H-1B median re-reads from the cited 80 Days CSV line
  A5 every value carries one of the allowed labels, and no label is model-judgment

    python3 audit_log.py [--log <salary-floor.log.json>] [--input <postings.json>]
Exit: 0 all checks held · 1 a check failed · 2 usage
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
LABELS = {"record", "script-output", "your-input"}


def line_of(path: Path, n: int) -> dict:
    with open(path, encoding="utf-8", newline="") as f:
        r = csv.reader(f)
        header = next(r)
        for i, row in enumerate(r, start=2):
            if i == n:
                return dict(zip(header, row))
    raise KeyError(f"{path}:{n} not found")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", type=Path, default=REPO / "course/2026fa/submissions/kommurisi/data-role-salary-floor/runs/latest/salary-floor.log.json")
    ap.add_argument("--input", type=Path, default=HERE / "fixtures/worked-run/postings.json")
    a = ap.parse_args()
    log = json.loads(a.log.read_text(encoding="utf-8"))
    ids = [p["id"] for p in json.loads(a.input.read_text(encoding="utf-8"))["postings"]]
    res = log["results"]
    fails = []

    got = [r["id"] for r in res]
    a1 = sorted(got) == sorted(ids) and len(set(got)) == len(got) and all(r.get("decision") and r.get("reason") for r in res)
    print(f"A1 one entry per posting, each with decision + reason: {'held' if a1 else 'FAILED'} ({len(got)}/{len(ids)})")
    fails += [] if a1 else ["A1"]

    checked = 0
    for r in res:
        f = r["values"].get("floor")
        if not f:
            continue
        m = re.match(r"(.+\.csv):(\d+) (A_\w+)", f["source"])
        row = line_of(REPO / m.group(1), int(m.group(2)))
        ok = float(row[m.group(3)]) == f["value"]
        checked += 1
        print(f"A2 {r['id']}: floor {f['value']:,.0f} vs {m.group(1).split('/')[-1]}:{m.group(2)} {m.group(3)}={row[m.group(3)]} "
              f"({row['AREA_TITLE']} / {row['OCC_CODE']}): {'held' if ok else 'FAILED'}")
        fails += [] if ok else [f"A2 {r['id']}"]
    print(f"A2 floors re-read from source: {checked} checked")

    for r in res:
        if r["decision"] in ("Unresolved", "Skip"):
            used = any(k in r["reason"] for k in ("under the floor", "≥ floor"))
            print(f"A3 {r['id']}: {r['decision']}, comparison made: {'YES (FAILED)' if used else 'no'}")
            fails += [f"A3 {r['id']}"] if used else []

    for r in res:
        c = r["values"].get("company_h1b_median_all_roles")
        if c and c["value"] is not None:
            m = re.match(r"(.+\.csv):(\d+) median_salary_offered", c["source"])
            row = line_of(REPO / m.group(1), int(m.group(2)))
            ok = float(row["median_salary_offered"]) == c["value"]
            print(f"A4 {r['id']}: {row['company_name']} median_salary_offered={row['median_salary_offered']}: {'held' if ok else 'FAILED'}")
            fails += [] if ok else [f"A4 {r['id']}"]

    labels = {v["label"] for r in res for v in r["values"].values()}
    a5 = labels <= LABELS
    print(f"A5 labels used: {sorted(labels)}: {'held' if a5 else 'FAILED'} (model-judgment present: {'model-judgment' in labels})")
    fails += [] if a5 else ["A5"]

    print("all checks held" if not fails else f"FAILED: {', '.join(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
