#!/usr/bin/env python3
"""Break attempts: make four deliberately wrong copies of salary_floor.py and check the tests catch each one.

Each BROKEN mutant changes exactly one line, the kind of shortcut that produces a confident, wrong floor.
A mutant is "killed" if at least one test fails against it. A surviving mutant means the tests are blind there.
The mutant file is generated beside salary_floor.py (so its imports resolve), and is removed after its run.

    .venv/Scripts/python.exe scripts/contrib/2026fa/kommurisi-data-role-salary-floor/mutation_test.py
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = (HERE / "salary_floor.py").read_text(encoding="utf-8")

MUTANTS = [
    ("BROKEN-floor-from-company-h1b-median",
     '    floor = money(d["floor_raw"])\n',
     '    floor = money(d["floor_raw"])\n'
     '    _c, _ = company_row(paths["csv80"], posting.get("csv_name", ""))\n'
     '    floor = money(_c["median_salary_offered"]) if _c and _c.get("median_salary_offered") else floor\n'),
    ("BROKEN-national-fallback-on-no-metro",
     '        out["decision"] = "Unresolved"\n        out["reason"] = "no-metro-match (no national fallback)"\n        return out\n',
     '        v["floor"] = rec(1.0, "national fallback")\n        v["national_median"] = rec(1.0, "national")\n'
     '        out["decision"] = "Unresolved"\n        out["reason"] = "no-metro-match (no national fallback)"\n        return out\n'),
    ("BROKEN-no-ambiguity-gate-silently-take-lowest",
     '        elif spread > float(profile.get("soc_spread_limit", 0.15)):\n',
     '        elif False:\n'),
    ("BROKEN-liveness-ignored",
     '    if live == "not-live":\n',
     '    if False:\n'),
]


def main() -> int:
    survived = 0
    for name, find, repl in MUTANTS:
        if SRC.count(find) != 1:
            print(f"{name}: SETUP ERROR, the target line is not unique in salary_floor.py")
            return 2
        mutant = HERE / "_mutant_salary_floor.py"
        mutant.write_text(SRC.replace(find, repl), encoding="utf-8")
        env = dict(os.environ, SALARY_FLOOR_SCRIPT=str(mutant), PYTHONIOENCODING="utf-8")
        p = subprocess.run([sys.executable, "-m", "unittest", str(HERE / "test_salary_floor.py")],
                           capture_output=True, text=True, env=env)
        mutant.unlink()
        failed = sorted(set(re.findall(r"^(?:FAIL|ERROR): (test_\w+)", p.stderr, re.M)))
        status = "KILLED" if p.returncode != 0 else "SURVIVED"
        survived += status == "SURVIVED"
        print(f"{name}: {status} by {len(failed)} test(s): {', '.join(failed) or '-'}")
    print(f"{len(MUTANTS) - survived}/{len(MUTANTS)} mutants killed")
    return 1 if survived else 0


if __name__ == "__main__":
    raise SystemExit(main())
