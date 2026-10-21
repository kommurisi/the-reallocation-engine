---
owner: kommurisi
term: 2026fa
component: data-role-salary-floor
status: DRAFT
promoted_to: null
---

# data-role-salary-floor — prototype

## Executive summary

This folder holds a small tool that tells an early-career data or BI job seeker the lowest salary to accept for a posting in one US city. It uses the government's metro wage survey, and it refuses to give a number when it can't stand behind one: an unclear occupation, an inexact city name, a suppressed estimate, or a dead posting. It was run on three live Boston postings and three made-up test cases, and its tests catch four deliberately broken versions of it.

## Files

| File | What |
|---|---|
| `salary_floor.py` | the mode: gates G1–G4, floor, company H-1B context, log + report. Imports the maintained `scripts/bls/local-wage-adjustment.py` rather than copying it |
| `fetch_pay_ranges.py` | the only network code; contacts only `boards-api.greenhouse.io` |
| `build_local_wage_inputs.py` | rebuilds the maintained script's three inputs from the official BLS + BEA files (they are not in the repo) |
| `test_salary_floor.py` | 13 offline tests on `fixtures/test/` |
| `mutation_test.py` | break attempts: 4 one-line mutants, each must make a test fail |
| `fixtures/worked-run/` | `postings.json` (fictional persona; 3 real postings + 3 CONSTRUCTED) and `pay-ranges.json` (captured 2026-10-21) |
| `.data/` | rebuilt inputs, **git-ignored**; regenerate with the builder |

## Run it

The steps need Python 3.13 with the repo `.venv` (`pandas`, `openpyxl`). On Windows also run `source ../.rae-shim/env.sh`, or call `.venv/Scripts/python.exe` directly.

```bash
# 1. data, once. BLS answers scripted downloads with 403: save oesm24ma.zip from
#    https://www.bls.gov/oes/tables.htm ("May 2024 Metropolitan and Nonmetropolitan Area") in a browser.
curl -fL -o MARPP.zip https://apps.bea.gov/regional/zip/MARPP.zip
.venv/Scripts/python.exe scripts/contrib/2026fa/kommurisi-data-role-salary-floor/build_local_wage_inputs.py \
  --bls <unzipped>/MSA_M2024_dl.xlsx --bea <unzipped>/MARPP_MSA_2008_2024.csv
#    expect: {"metro_oews": 150176, ..., "crosswalk_exact_matches": 387}

# 2. capture postings (network; optional, the worked-run capture is committed)
python3 scripts/contrib/2026fa/kommurisi-data-role-salary-floor/fetch_pay_ranges.py

# 3. the mode (offline); with no flags it reruns the committed worked run
python3 scripts/contrib/2026fa/kommurisi-data-role-salary-floor/salary_floor.py
#    expect: 6 postings → Range clears floor 2 · Unresolved 2 · Range starts below floor 1 · Skip 1

# 4. tests and break attempts (offline, fixtures only)
.venv/Scripts/python.exe -m unittest scripts/contrib/2026fa/kommurisi-data-role-salary-floor/test_salary_floor.py -v
.venv/Scripts/python.exe scripts/contrib/2026fa/kommurisi-data-role-salary-floor/mutation_test.py
```

The checksums of the sources used for the worked run:
- `oesm24ma.zip`: `7bf915fc47e464983c5b8b8200d63a733ef90275c7af0576b78875e5b04d35d9`
  - `MSA_M2024_dl.xlsx`: `2a172aed29693f50afa398be03fd107ce6bfff8b04e5fd163b4c5ddcf941d6ec`
- `MARPP.zip`: `5dbf2e6ac2af222cc9abc205586c9b480344d89392752eb689c3ec823a34c83e`
  - `MARPP_MSA_2008_2024.csv`: `4ce7a7e2ea08ff721de83f50d8a70bb9c93956a49970462f462372aa58cee9f4`

`salary_floor.py` flags: `--input`, `--pay`, `--out-dir` (default `course/2026fa/submissions/kommurisi/data-role-salary-floor/runs/latest/`), `--oews`, `--rpp`, `--crosswalk`, `--national`, `--onet`, `--csv80`.

## Exit codes

`salary_floor.py`: `0` ran · `2` usage error, bad input or a missing data file. `mutation_test.py`: `0` all mutants killed · `1` a mutant survived · `2` setup error.

## The one maintained-file patch

`scripts/bls/local-wage-adjustment.py` could not run on Windows, for two reasons:
1. It looks for `.venv/bin/python`. Windows venvs use `Scripts\python.exe`.
2. `os.execv` does not quote arguments on Windows, so a repo path with a space broke the re-launch.

The patch picks the right interpreter path and re-launches with `subprocess` on Windows only. POSIX behaviour is unchanged. The before and after runs are in `course/2026fa/submissions/kommurisi/data-role-salary-floor/evidence/01–02`.
