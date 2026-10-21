# Worked run — data-role-salary-floor v0.1.0

## Executive summary

This is the record of actually running the salary-floor mode, on 21 October 2026, against real government wage data and three live Boston job postings, plus three made-up test postings.

**Getting there.** First, the repository's own wage tool had to be repaired: it could not start on Windows, and its data files were missing from the repository. Both are fixed or worked around, and the repair was checked against the tool's own published examples, which it now reproduces to the cent.

**What the mode found.**
- Two real postings (Klaviyo and Toast) start above the Boston floor for data work, $102,400.
- One real posting (CarGurus) cannot be judged until a person decides which occupation it is. The candidate floors differ by 42%.
- Toast's average pay for its visa-sponsored staff, $177,341, is flagged as a bad benchmark for an entry-level offer.
- The three test postings were handled as designed: one underpaying offer was caught, one dead job link was skipped, and one inexact city name was refused rather than guessed.

**How it was checked.** Every reported wage was re-read straight from the government spreadsheet. 13 tests pass, and four deliberately broken versions of the tool were each caught.

**What it cannot check.** The legal minimum wage for an H-1B version of the job; that is the main open item.

## Run record

- **Date:** 2026-10-21 · **Machine:** Windows 11, Git Bash, Python 3.13.2, pandas 3.0.6 · **Branch:** `contrib/2026fa-kommurisi-data-role-salary-floor`, from upstream `main` `015843d`.
- **Lifecycle claimed:** DRAFT (3 open TODOs). This was a full sample run, not a promotion.
- **Who did what:** Claude Code (Claude Opus 5.5) wrote the scripts and ran every command below in Siddi's session. Siddi chose the mode, approved the downloads and the maintained-file patch, and signs the attestation. See SOURCES.md.
- **Privacy:** fictional persona only. In pasted output, the home-folder part of file paths is shown as `~`.

## Inputs

**Persona** (fictional, modelled on the author's situation; no name, contacts or real dates): an F-1 MS Information Systems (STEM) student in Boston, graduating Dec 2026, targeting early-career BI / analytics roles that will need H-1B sponsorship.

**Floor rule** (your-input, *drafted by Claude, Siddi to confirm*):
- BLS metro **25th percentile** of the chosen occupation;
- an SOC spread limit of **15%**, above which the mode refuses to pick an occupation by itself.

| # | Posting | Real? | Source of range | SOC candidates | SOC choice (your-input, *drafted by Claude, Siddi to confirm*) |
|---|---|---|---|---|---|
| 1 | Klaviyo — Analytics Engineer (Boston) | real | Greenhouse API | 15-1243, 15-2051 (added) | 15-2051: BI/analytics modelling; the lower floor |
| 2 | CarGurus — Senior Product Data Analyst, Dealer (Boston) | real | Greenhouse API | 15-2051, 13-1161, 15-2041 (added) | none, to exercise the ambiguity gate |
| 3 | Toast — Senior Manager, CS Data & Analytics (Boston) | real | Greenhouse API | 15-2051, 11-3021 (added) | 15-2051: leads analytics work |
| 4 | Northwind Analytics — Data Analyst | **CONSTRUCTED** | typed: $65,000–$78,000 | O\*NET exact-title match | 15-2051 |
| 5 | Klaviyo — Data Analyst, job id 1000000001 | **CONSTRUCTED** (id doesn't exist) | Greenhouse API → 404 | O\*NET | 15-2051 |
| 6 | Klaviyo — Business Intelligence Analyst, metro "Boston, MA" | **CONSTRUCTED** (inexact metro) | typed | O\*NET | 15-2051 |

Data:
- BLS `oesm24ma.zip`: sha256 `7bf915fc…35d9`, saved from bls.gov in the app's browser, because BLS answers scripted downloads with 403.
- BEA `MARPP.zip`: sha256 `5dbf2e6a…c83e`.
- The 80 Days CSV and the O\*NET compact CSV, as shipped at `015843d`.

## 1. The maintained wage script on Windows: two failures, one patch

`scripts/bls/local-wage-adjustment.py` looked only for `.venv/bin/python`, which doesn't exist on Windows. So it reported a missing venv even though one existed:

`evidence/01-unpatched-windows-run.txt`:

```text
# 2026-10-21T21:19:36Z · Windows 11, Git Bash, Python 3.13.2 · branch contrib/2026fa-kommurisi-data-role-salary-floor @ 015843d (unpatched maintained script)
$ npm run bls:local-wage -- --metro "Boston-Cambridge-Newton, MA-NH" --soc 15-2051
missing .venv — create it with:
  python3.13 -m venv .venv
  .venv/bin/pip install -r data/bls/local-wage/requirements.txt
# exit 2
```

After the first fix (the interpreter path), a second Windows bug appeared: `os.execv` does not quote arguments, so the path split at the space in the user-folder name. With both fixes, the script starts and stops honestly, because its input files are not in the repository:

`evidence/02-patched-missing-inputs.txt`:

```text
# 2026-10-21T21:20:21Z · after BOTH Windows fixes (venv path; execv quoting); default inputs still absent from the repo
$ npm run bls:local-wage -- --metro "Boston-Cambridge-Newton, MA-NH" --soc 15-2051
missing data file: ~\Documents\GitHub\the-reallocation-engine\data\bls\local-wage\metro_oews.csv
# exit 2
$ git ls-files data/bls/local-wage data/BLS/local-wage | wc -l
0
# note (2026-10-21): the home-folder part of the path is shown as ~ for privacy; nothing else was changed.
```

## 2. Rebuilding the missing inputs from the official files

`evidence/10-build-inputs.txt`:

```text
# 2026-10-21T22:04:34Z · rebuild of the maintained script's inputs (re-run for this record; outputs compared with the first build by sha256)
$ .venv/Scripts/python.exe scripts/contrib/2026fa/kommurisi-data-role-salary-floor/build_local_wage_inputs.py --bls ~/Downloads/reallocation-data/oesm24ma/oesm24ma/MSA_M2024_dl.xlsx --bea ~/Downloads/reallocation-data/marpp/MARPP_MSA_2008_2024.csv
{"metro_oews": 150176, "metro_oews_areas": 393, "metro_oews_detailed": 141164, "bea_rpp_all_items": 389, "crosswalk_exact_matches": 387}
# exit 0
$ sha256sum .data/{metro_oews,bea_rpp,bls_bea_msa_crosswalk}.csv   # identical to the first build?
a549a37d43f815e0838737fcbb2286738774f04fea389f1647031a0a5ebb7021 *.data/metro_oews.csv
9690fbe43c4de6a2b701e970504a4b0879f7a0f15799c620d15a3a45b394a344 *.data/bea_rpp.csv
75731732f65fd6ebd1d8eeeccdeccc47a79f4f0527b0f43e36bacb4c017b723b *.data/bls_bea_msa_crosswalk.csv
identical to the first build: yes
```

The builder's manifest (`evidence/08-build-manifest.json`):

`evidence/08-build-manifest.json`:

```json
{
  "built_at": "2026-10-21T22:06:06+00:00",
  "sources": {
    "bls": {
      "file": "MSA_M2024_dl.xlsx",
      "sha256": "2a172aed29693f50afa398be03fd107ce6bfff8b04e5fd163b4c5ddcf941d6ec",
      "url": "https://www.bls.gov/oes/special-requests/oesm24ma.zip"
    },
    "bea": {
      "file": "MARPP_MSA_2008_2024.csv",
      "sha256": "4ce7a7e2ea08ff721de83f50d8a70bb9c93956a49970462f462372aa58cee9f4",
      "url": "https://apps.bea.gov/regional/zip/MARPP.zip"
    }
  },
  "rows": {
    "metro_oews": 150176,
    "metro_oews_areas": 393,
    "metro_oews_detailed": 141164,
    "bea_rpp_all_items": 389,
    "crosswalk_exact_matches": 387
  }
}
```

`crosswalk_exact_matches: 387` equals the "387 exact AREA=GeoFIPS matches" the maintained README documents. That is the first sign the rebuild is faithful.

## 3. The rebuilt inputs reproduce the maintained script's documented checks

`evidence/03-documented-checks.txt`:

```text
# 2026-10-21T21:21:48Z · maintained script (Windows-patched) on inputs rebuilt by build_local_wage_inputs.py; the three documented checks (scripts/bls/README.md + summer-2026 portfolio)

$ python3 scripts/bls/local-wage-adjustment.py --metro "Glens Falls, NY" --soc 15-1252 <rebuilt inputs> --json
coverage = 0/1 (ok=0 attempted=1 missing_reason={'suppressed-small-sample': 1})
{
  "coverage": {
    "ok": 0,
    "attempted": 1,
    "coverage": "0/1",
    "missing_reason": {
      "suppressed-small-sample": 1
    }
  }
}
metro_area,soc_code,status,missing_reason,nominal_wage_mean,nominal_wage_median,bea_rpp_value,adjusted_wage_band_low,adjusted_wage_band_high,adjusted_wage_median,plausibility_flag,national_median_wage,source_bls_file,source_bea_file,run_date
"Glens Falls, NY",15-1252,missing,suppressed-small-sample,,,,,,,,,scripts\contrib\2026fa\kommurisi-data-role-salary-floor\.data\metro_oews.csv,scripts\contrib\2026fa\kommurisi-data-role-salary-floor\.data\bea_rpp.csv,2026-10-21
# exit 0

$ python3 scripts/bls/local-wage-adjustment.py --metro "Glens Falls, NY" --soc 15-1243 <rebuilt inputs> --json
coverage = 0/1 (ok=0 attempted=1 missing_reason={'no-occupation-row': 1})
{
  "coverage": {
    "ok": 0,
    "attempted": 1,
    "coverage": "0/1",
    "missing_reason": {
      "no-occupation-row": 1
    }
  }
}
metro_area,soc_code,status,missing_reason,nominal_wage_mean,nominal_wage_median,bea_rpp_value,adjusted_wage_band_low,adjusted_wage_band_high,adjusted_wage_median,plausibility_flag,national_median_wage,source_bls_file,source_bea_file,run_date
"Glens Falls, NY",15-1243,missing,no-occupation-row,,,,,,,,,scripts\contrib\2026fa\kommurisi-data-role-salary-floor\.data\metro_oews.csv,scripts\contrib\2026fa\kommurisi-data-role-salary-floor\.data\bea_rpp.csv,2026-10-21
# exit 0

$ python3 scripts/bls/local-wage-adjustment.py --metro "New York-Newark-Jersey City, NY-NJ" --soc 15-1252 <rebuilt inputs> --json
coverage = 1/1 (ok=1 attempted=1 missing_reason={})
{
  "coverage": {
    "ok": 1,
    "attempted": 1,
    "coverage": "1/1",
    "missing_reason": {}
  }
}
metro_area,soc_code,status,missing_reason,nominal_wage_mean,nominal_wage_median,bea_rpp_value,adjusted_wage_band_low,adjusted_wage_band_high,adjusted_wage_median,plausibility_flag,national_median_wage,source_bls_file,source_bea_file,run_date
"New York-Newark-Jersey City, NY-NJ",15-1252,ok,,161090.00,161970.00,112.5630,112061.69,169078.65,143892.75,ok,133080.00,scripts\contrib\2026fa\kommurisi-data-role-salary-floor\.data\metro_oews.csv,scripts\contrib\2026fa\kommurisi-data-role-salary-floor\.data\bea_rpp.csv,2026-10-21
# exit 0
```

Expected, from `scripts/bls/README.md` and the summer-2026 portfolio:
- Glens Falls × 15-1252 → `suppressed-small-sample`.
- Glens Falls × 15-1243 → `no-occupation-row`.
- New York × 15-1252 → nominal median **161,970**, RPP **112.563**, adjusted median **143,892.75**.

All three match exactly.

## 4. Capturing the postings (the only network step)

`evidence/04-fetch-pay-ranges.txt`:

```text
# 2026-10-21T21:26:04Z · the mode's only network step
$ python3 scripts/contrib/2026fa/kommurisi-data-role-salary-floor/fetch_pay_ranges.py
200  klaviyo/7737707003  Analytics Engineer  $140,000�$210,000
200  cargurus/8096751  Senior Product Data Analyst, Dealer  $120,000�$151,000
200  toast/8243192  Senior Manager, CS Data & Analytics  $145,000�$232,000
404  klaviyo/1000000001    no range
# exit 0
# note (added 2026-10-21): each '?' / '�' above is an en dash mangled by the Windows console code page, not data. The saved file fixtures/worked-run/pay-ranges.json holds the exact values; fetch_pay_ranges.py now prints an ASCII '-'.
```

## 5. Running the mode

```text
$ python3 scripts/contrib/2026fa/kommurisi-data-role-salary-floor/salary_floor.py
6 postings → Range clears floor 2 · Unresolved 2 · Range starts below floor 1 · Skip 1
wrote course/2026fa/submissions/kommurisi/data-role-salary-floor/runs/latest/salary-floor.report.md and salary-floor.log.json
```

The report's summary table, pasted from `runs/latest/salary-floor.report.md`:

| Posting | SOC (gate) | Floor | Metro median | Posted range | Company H-1B median (all roles) | Decision |
|---|---|---|---|---|---|---|
| Klaviyo — Analytics Engineer | ok: 15-2051 | $102,400 | $131,830 | $140,000–$210,000 | $126,000 | **Range clears floor** |
| CarGurus — Senior Product Data Analyst | unresolved: ambiguous-soc (floors differ by 42%) | — | — | $120,000–$151,000 | — | **Unresolved** |
| Toast — Senior Manager, CS Data & Analytics | ok: 15-2051 | $102,400 | $131,830 | $145,000–$232,000 | $177,341 | **Range clears floor** |
| Northwind Analytics — Data Analyst (CONSTRUCTED) | ok: 15-2051 | $102,400 | $131,830 | $65,000–$78,000 | — | **Range starts below floor** |
| Klaviyo — Data Analyst (CONSTRUCTED) | ok: 15-2051 | $102,400 | $131,830 | — | $126,000 | **Skip** |
| Klaviyo — Business Intelligence Analyst (CONSTRUCTED) | — | — | — | $90,000–$110,000 | — | **Unresolved** |

## 6. Verified vs. inferred

| Value | Verified by data / script | Inferred or chosen |
|---|---|---|
| Boston 15-2051 p25 $102,400, median $131,830, p75 $166,710 | **record**: BLS `MSA_M2024_dl.xlsx`, `metro_oews.csv:16965`, re-read from the xlsx (§7) | — |
| Floors of the other candidate SOCs (15-1243 $132,660; 13-1161 $72,130; 15-2041 $81,950; 11-3021 $169,010) | **record**: same file | which candidates to list for titles O\*NET doesn't match is **your-input** |
| "Data Analyst" → 7 O\*NET occupations | **record**: O\*NET compact, exact alternate-title match (a sample list; a missing title proves nothing) | — |
| Metro "Boston, MA" has no BLS match | **script-output**: maintained `resolve_metro` | — |
| RPP-adjusted median, `crosscheck_p25 = true` | **script-output**: maintained `evaluate_pair` | — |
| Klaviyo $126,000 (154 approvals), Toast $177,341 (150) H-1B medians | **record**: 80 Days CSV lines 14495, 27011 (company-wide) | that they are *not* a benchmark is the mode's rule |
| CarGurus is not in the 80 Days CSV | **record**: exact-name search | — |
| Posted ranges $140k–$210k, $120k–$151k, $145k–$232k; job 1000000001 → 404 | **record**: Greenhouse API, captured 2026-10-21T21:26Z | — |
| SOC choice per posting | — | **your-input** (drafted by Claude, Siddi to confirm) |
| Floor = the 25th percentile; spread limit 15% | — | **your-input** (drafted by Claude, Siddi to confirm) |
| "Range clears / starts below floor" | **script-output**: arithmetic on the two records above | — |
| Anything from a language model | none: no model was called by the mode | — |

## 7. Verification

**Hand cross-check against the original spreadsheet.** This bypasses both the builder and the mode:

`evidence/07-hand-cross-check.txt`:

```text
# 2026-10-21T21:44:24Z · hand cross-check: values in the worked-run report re-read from the ORIGINAL sources (BLS xlsx via openpyxl, 80 Days CSV via grep), bypassing build_local_wage_inputs.py and salary_floor.py
MSA_M2024_dl.xlsx  AREA=14460 Boston-Cambridge-Newton, MA-NH  13-1161 Market Research Analysts and Marketing Specialists  A_PCT25=72130  A_MEDIAN=95930  A_PCT75=130200
MSA_M2024_dl.xlsx  AREA=14460 Boston-Cambridge-Newton, MA-NH  15-1243 Database Architects  A_PCT25=132660  A_MEDIAN=162310  A_PCT75=181720
MSA_M2024_dl.xlsx  AREA=14460 Boston-Cambridge-Newton, MA-NH  15-2041 Statisticians  A_PCT25=81950  A_MEDIAN=99230  A_PCT75=130980
MSA_M2024_dl.xlsx  AREA=14460 Boston-Cambridge-Newton, MA-NH  15-2051 Data Scientists  A_PCT25=102400  A_MEDIAN=131830  A_PCT75=166710
not found: none
$ grep -n '^KLAVIYO INC,\|^TOAST INC,' mapped_student_employment_targets_v3.csv | cut -f1,16,19 (company, Total Approvals, median_salary_offered)
14495 KLAVIYO INC 154.0 126000.0
27011 TOAST INC 150.0 177341.0
CARGURUS INC present: False
```

**An audit of the agent log, plus a determinism re-run:**

`evidence/09-audit-and-rerun.txt`:

```text
# 2026-10-21T22:09:29Z · audit: the agent log re-read against its sources, plus a determinism re-run
$ python3 scripts/contrib/2026fa/kommurisi-data-role-salary-floor/audit_log.py
A1 one entry per posting, each with decision + reason: held (6/6)
A2 klaviyo-analytics-engineer: floor 102,400 vs metro_oews.csv:16965 A_PCT25=102400 (Boston-Cambridge-Newton, MA-NH / 15-2051): held
A2 toast-senior-manager-cs-data-analytics: floor 102,400 vs metro_oews.csv:16965 A_PCT25=102400 (Boston-Cambridge-Newton, MA-NH / 15-2051): held
A2 northwind-data-analyst-CONSTRUCTED: floor 102,400 vs metro_oews.csv:16965 A_PCT25=102400 (Boston-Cambridge-Newton, MA-NH / 15-2051): held
A2 klaviyo-dead-job-CONSTRUCTED: floor 102,400 vs metro_oews.csv:16965 A_PCT25=102400 (Boston-Cambridge-Newton, MA-NH / 15-2051): held
A2 floors re-read from source: 4 checked
A3 cargurus-senior-product-data-analyst: Unresolved, comparison made: no
A3 klaviyo-dead-job-CONSTRUCTED: Skip, comparison made: no
A3 inexact-metro-CONSTRUCTED: Unresolved, comparison made: no
A4 klaviyo-analytics-engineer: KLAVIYO INC median_salary_offered=126000.0: held
A4 toast-senior-manager-cs-data-analytics: TOAST INC median_salary_offered=177341.0: held
A4 klaviyo-dead-job-CONSTRUCTED: KLAVIYO INC median_salary_offered=126000.0: held
A5 labels used: ['record', 'script-output', 'your-input']: held (model-judgment present: False)
all checks held
# exit 0

$ python3 scripts/contrib/2026fa/kommurisi-data-role-salary-floor/salary_floor.py   # second run, then compare results[] with the first
6 postings → Range clears floor 2 · Unresolved 2 · Range starts below floor 1 · Skip 1
wrote course/2026fa/submissions/kommurisi/data-role-salary-floor/runs/latest/salary-floor.report.md and salary-floor.log.json
results[] identical across runs: True
```

**Tests:**

`evidence/05-tests.txt`:

```text
# 2026-10-21T22:12:59Z · offline tests, fixtures only
$ python -m unittest scripts/contrib/2026fa/kommurisi-data-role-salary-floor/test_salary_floor.py -v
test_only_greenhouse_urls_are_built ... ok
test_ambiguous_soc_without_choice_refuses ... ok
test_bad_input_exits_2 ... ok
test_close_candidates_take_the_lowest_floor ... ok
test_company_h1b_median_is_context_never_the_floor ... ok
test_dead_posting_is_skipped_without_comparison ... ok
test_equal_to_floor_clears_and_below_floor_is_flagged ... ok
test_floor_is_the_bls_p25_of_the_chosen_soc ... ok
test_lca_wage_gate_is_never_claimed ... ok
test_missing_data_file_exits_2 ... ok
test_no_metro_match_never_falls_back_to_national ... ok
test_suppressed_median_refuses ... ok
test_top_coded_percentile_refuses ... ok

----------------------------------------------------------------------
Ran 13 tests in 22.976s

OK
# exit 0
```

**Deliberate break attempts: mutants.** Each mutant is a one-line sabotage that a hurried implementation might really contain:

`evidence/06-mutation-tests.txt`:

```text
# 2026-10-21T22:13:22Z · break attempts: 4 one-line mutants of salary_floor.py vs the test suite
$ python scripts/contrib/2026fa/kommurisi-data-role-salary-floor/mutation_test.py
BROKEN-floor-from-company-h1b-median: KILLED by 4 test(s): test_close_candidates_take_the_lowest_floor, test_company_h1b_median_is_context_never_the_floor, test_equal_to_floor_clears_and_below_floor_is_flagged, test_floor_is_the_bls_p25_of_the_chosen_soc
BROKEN-national-fallback-on-no-metro: KILLED by 1 test(s): test_no_metro_match_never_falls_back_to_national
BROKEN-no-ambiguity-gate-silently-take-lowest: KILLED by 1 test(s): test_ambiguous_soc_without_choice_refuses
BROKEN-liveness-ignored: KILLED by 1 test(s): test_dead_posting_is_skipped_without_comparison
4/4 mutants killed
# exit 0
```

## Attestation

- Recipe: data-role-salary-floor v0.1.0
- By: ______________________ (Siddi Kommuri, to sign after reading this page) · 2026-10-__
- Runs: every command below was executed by Claude Code in Siddi's session on 2026-10-21. The signature attests that Siddi reviewed these results, not that Siddi typed the commands.

### Tested

| Ran | Saw | Expected |
|---|---|---|
| `npm run bls:local-wage -- --metro "Boston-Cambridge-Newton, MA-NH" --soc 15-2051` (unpatched) | `missing .venv …`, exit 2, with `.venv` present | the maintained script runs (broke: Windows path) |
| same, patched, default inputs | `missing data file: …/data/bls/local-wage/metro_oews.csv`, exit 2 | an honest stop: the inputs aren't in the repo |
| `build_local_wage_inputs.py` on BLS + BEA files | 150,176 rows; crosswalk 387 | 387, per the maintained README |
| maintained script × 3 documented checks on the rebuilt inputs | suppressed · no-occupation-row · 161,970 / 112.563 / 143,892.75 | exactly those |
| `fetch_pay_ranges.py` | 200 ×3 with ranges; 404 for job 1000000001 | 404 for the constructed id |
| `salary_floor.py` | clears 2 · below 1 · Skip 1 · Unresolved 2 | the gates fire on postings 2, 5 and 6 |
| hand re-read of 4 Boston rows from `MSA_M2024_dl.xlsx` | 102400 / 132660 / 72130 / 81950 p25 | identical to the report |
| `audit_log.py` A1–A5, plus a second run | all held; `results[]` identical | held; deterministic |
| unittest (13 tests) | 13 OK | all pass |
| **break attempt:** 4 mutants (company-median floor, national fallback, no ambiguity gate, liveness ignored) | 4/4 killed | every mutant caught |
| **break attempt:** metro "Boston, MA" | Unresolved `no-metro-match`, no national number | refusal, no fallback |
| **break attempt:** `build_url("x@evil", 1)` and 5 more hostile board/job ids | `ValueError` each | only `boards-api.greenhouse.io` URLs |

### Did not test

- The H-1B prevailing-wage gate (G4): no data, so it is always `not-checked`.
- Any metro other than Boston and the documented New York / Glens Falls checks.
- Lever, Ashby or Workday postings (Greenhouse only).
- The maintained script's patch on macOS/Linux. The change is Windows-only by `os.name`, but it was not run on POSIX.
- `npm run bls:local-wage -- --sample` (the frozen 112-pair sample): its `sample.csv` is also missing from the repo.
- Whether the SOC choices match how Klaviyo or Toast would actually file. Unknowable from public data.
- Whether BLS's Feb 2026 re-issue of `MSA_M2024_dl.xlsx` differs from the file the summer contributor used; the three documented numbers matched.

### Broke during testing, fixed

- Two Windows bugs in `scripts/bls/local-wage-adjustment.py`. Fixed in one declared patch.
- The maintained inputs were missing. Rebuilt by `build_local_wage_inputs.py`, with source checksums.
- Console en dashes were mangled in evidence 04. Annotated in place; the JSON capture is exact.
- A fact in Claude's draft docs was wrong: "Data Analyst → seven codes with floors". In fact six have a Boston wage. Caught by checking the log; corrected before commit.

## Reflection

**What went well.**
- The mode is grounded in a maintained, already-tested script, which it imports rather than copies.
- That script's own documented outputs were reproduced before the rebuild was trusted.
- Every number in the report re-reads from a file line.
- The gates refuse instead of guessing: an ambiguous code, an inexact metro, a dead posting.

**What the mode got wrong or missed.**
- **The real postings are mostly senior.** Greenhouse showed few early-career Boston data roles with ranges in October 2026, so the worked run under-tests the persona's actual target.
- **The SOC choices are judgments**, made by Claude for this run, that decide the floor. The mode makes them visible, but it can't make them right.
- **The 25th-percentile rule is a policy, not a fact.**
- **The company H-1B median** is a weak signal even as context.

**Next steps.**
1. Close TODO-1 with the OFLC wage library, so G4 can say whether an offer would clear the legal Level I wage for the filed code.
2. Add Lever/Ashby ranges (TODO-2) and re-run on early-career postings.
3. Have Siddi re-decide the SOC choices from the actual job duties, and record the reasons.
4. Ask the maintainers whether to restore `data/bls/local-wage/` or adopt the builder (TODO-3).
