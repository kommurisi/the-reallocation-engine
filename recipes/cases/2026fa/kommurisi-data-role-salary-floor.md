---
status: DRAFT
todos_open: 3
last_gate: "sample-run executed 2026-10-21 (logs/runs/2026fa-kommurisi-2.md) — not a lifecycle promotion: 3 open TODOs block DRAFT → SPECIFIED"
attestation: null
recipe_version: 0.1.0
---

# data-role-salary-floor — What is the lowest pay I should accept for this data role, here?

## Executive summary

**Who it is for:** an F-1 master's student in a STEM-designated MS Information Systems / analytics program, graduating within a semester, who is about to answer "what are your salary expectations?" or weigh an offer for an **early-career data, analytics or business-intelligence role in one US metro** (the worked run uses Boston) that will need H-1B sponsorship later.

**What it does:** for each posting it reads the government's own wage survey for that metro and occupation. A posting is a company, a title, a metro and, if published, a pay range. The mode returns a **floor**: the pay that the lowest-paid quarter of people already doing that occupation in that metro earn. It then says whether the posting's range starts above or below that floor. It shows the company's average pay for its visa-sponsored staff as context, and never uses it as the floor.

**What it decides:** the number you should not go below when you name a salary, and which postings are underpaying before you spend hours on them.

**Why the engine does not already do this:** the engine knows a national median wage per occupation, and a maintained recipe can adjust a metro wage for local prices. Nothing turns those into a per-posting floor. Nothing handles the step that decides the answer: **which occupation code the job is.** O\*NET lists "Data Analyst" under seven occupations. Six of them have a Boston wage, and their 25th-percentile floors run from $46,190 to $132,660.

**Two customers:** this file is for the agent; `recipes/cases/2026fa/kommurisi-data-role-salary-floor.card.md` is for the person.

**Handoff condition (done when):**
- `salary_floor.py` exits 0;
- both `salary-floor.log.json` and `salary-floor.report.md` exist in the out-dir;
- every posting appears in the log exactly once, with a decision or a named Unresolved reason;
- every floor value's source is a `metro_oews.csv:<line>` row whose `A_PCT25` equals the value, and `crosscheck_p25` is `true`;
- a human has read the report's "What this run cannot verify" section.

## Lifecycle note (why DRAFT)

A full sample run completed on real BLS, BEA, 80 Days and Greenhouse data, and conformance passes. That is the evidence SNICKERDOODLE asks for at SPECIFIED → RUNNABLE-SAMPLE. But the DRAFT → SPECIFIED gate is *zero open TODOs*, and this recipe carries three (see Proposed additions). The honest status is therefore **DRAFT**. The worked run's sample-run attestation table was signed by the author on 2026-10-21. The frontmatter `attestation` stays `null`, because SNICKERDOODLE records it only at VERIFIED.

## Required reads

1. `SNICKERDOODLE.md`, `DOMAIN.md`, `DATA_CONTRACT.md` §Zero-Conditions.
2. `recipes/local-wage-adjustment.md` and `scripts/bls/README.md`: the maintained metro gates this recipe calls.
3. `book/chapters/09-is-the-role-any-good-bls-onet-role-quality.md`: the national-vs-local limit.
4. `scripts/contrib/2026fa/kommurisi-data-role-salary-floor/README.md`.

## Source inventory

| Source | Path / command | Layer | Used for | Label |
|---|---|---|---|---|
| BLS OEWS metro wages, May 2024 | `oesm24ma.zip` → `MSA_M2024_dl.xlsx` (sha256 `2a172aed…d6ec`), rebuilt into `.data/metro_oews.csv` by `build_local_wage_inputs.py` | Cognitive Pivot | floor (`A_PCT25`), median, p75, employment | record |
| BEA Regional Price Parities 2024 | `MARPP.zip` → `MARPP_MSA_2008_2024.csv` (sha256 `4ce7a7e2…e9f4`) → `.data/bea_rpp.csv` | Cognitive Pivot | the maintained script's RPP join and the p25 cross-check | record |
| Maintained metro gates | `scripts/bls/local-wage-adjustment.py` (`load_tables`, `resolve_metro`, `evaluate_pair`), imported, not copied | Cognitive Pivot | metro match, missing / suppressed / no-crosswalk reasons, RPP-adjusted median | script-output |
| O\*NET + national OEWS compact | `data/bls/compact/soc_occupation_compact.csv` | Cognitive Pivot | candidate SOCs from exact title / alternate-title match; national median | record (sample only) |
| 80 Days to Stay | `data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv` | 80 Days | company-wide H-1B `median_salary_offered`, `Total Approvals` | record (company-wide) |
| Greenhouse job API | `fetch_pay_ranges.py` → `boards-api.greenhouse.io/v1/boards/<b>/jobs/<id>?pay_transparency=true` | Job-Ops | liveness gate (200 / 404) and posted `pay_input_ranges` | record (dated capture) |
| Persona + postings | `fixtures/worked-run/postings.json` | — | metro, title, SOC candidates/choice, floor rule | your-input |

## Inputs

`postings.json`:
- `profile`: `metro` (an exact BLS `AREA_TITLE` or 5-digit code), `floor_percentile` (default 25), `soc_spread_limit` (default 0.15), and a `persona` line (fictional, no personal data).
- `postings[]`: `id`, `company`, `csv_name` (exact 80 Days `company_name`), `title`, optional `greenhouse {board, job_id}` or a manual `posted_range [min, max]`, optional `soc_candidates_added` and `soc_choice` with `soc_choice_reason`, and `constructed: true` for test cases.

## Phase gates

Gates are hard stops. A failed gate yields **Unresolved** (or **Skip**) with a reason. Never a guessed number.

| Gate | Test | Pass | Fail |
|---|---|---|---|
| **G1 SOC choice** (human) | candidates = O\*NET exact title / alternate-title matches ∪ `soc_candidates_added`. If no `soc_choice`: exactly one candidate, or candidates' metro floors within `soc_spread_limit` (then the lowest is taken) | `ok: <SOC>` | `ambiguous-soc (floors differ by N%)` or `no-soc-candidate` |
| **G2 metro wage** | maintained `evaluate_pair` returns `ok` for (metro, SOC), **and** the `A_PCT<p>` cell is a number (not `#`, `*` or blank) | floor emitted | `no-metro-match` · `no-occupation-row` · `suppressed-small-sample` · `no-crosswalk-match` · `top-coded-or-blank-percentile` — **no national fallback** |
| **G3 liveness** | Greenhouse API status from the dated capture | 200 → compare the range | 404 → **Skip**; no capture → comparison flagged provisional |
| **G4 LCA prevailing wage** | OFLC wage level for (SOC, area) ≤ offer | — | always `not-checked` until TODO-1 closes. **Never claimed.** |

The visa timeline is not a gate here, because a salary floor does not depend on the OPT clock. Pair this mode with an OPT-runway mode before applying.

## What it can verify

- The BLS May 2024 metro wage percentiles for (metro, SOC), traced to a file line, and that the maintained script's RPP-adjusted p25 × RPP/100 gives back the same nominal p25 (`crosscheck_p25`).
- That a metro name is or is not an exact BLS area, and why a (metro, SOC) pair has no usable wage.
- How far apart the candidate SOCs' floors are (`soc_floor_spread`), so the choice is visible.
- The company's recorded company-wide H-1B median and approval count, and whether that median sits above the role's metro 75th percentile.
- That a Greenhouse posting existed (200) or not (404) at the capture time, and its posted base range.

## What it cannot verify

- **The legal H-1B floor:** the OFLC prevailing wage for this SOC, area and level (TODO-1). A range above the BLS floor can still be below the wage level an LCA requires.
- **Which SOC the employer's attorney will file.** G1 is a human judgment and is labelled `your-input`.
- This posting's seniority, bonus, equity or benefits. BLS percentiles are base wages across the whole occupation.
- Anything after the May 2024 reference period. Wages drift.
- That the company's H-1B median describes **this** role. It averages every H-1B role at the company, which is mostly engineers.
- Lever, Ashby or Workday postings' ranges (TODO-2). Only Greenhouse is captured.

## Workflow

1. **Data (once):** save `oesm24ma.zip` from https://www.bls.gov/oes/tables.htm in a browser (BLS refuses scripted downloads), download `MARPP.zip`, and run `build_local_wage_inputs.py --bls … --bea …`. Check that `manifest.json` shows `crosswalk_exact_matches: 387`.
2. **Reproduce the maintained checks** on the rebuilt inputs: Glens Falls × 15-1252 → `suppressed-small-sample`; × 15-1243 → `no-occupation-row`; New York × 15-1252 → median 161,970, RPP 112.563, adjusted 143,892.75.
3. **Capture postings (network):** `python3 scripts/contrib/2026fa/kommurisi-data-role-salary-floor/fetch_pay_ranges.py`.
4. **Run (offline):** `python3 scripts/contrib/2026fa/kommurisi-data-role-salary-floor/salary_floor.py`.
5. **Human gate:** resolve every `ambiguous-soc` by writing a `soc_choice` with a reason. Look up the OFLC wage for each SOC you will negotiate on. Re-run.

## Output contract

Two artifacts, because one cannot serve both readers (P5):

- **Agent log** `salary-floor.log.json`: `meta`, `profile`, `results[]`. Each result has `id`, `company`, `title`, `metro`, `constructed`, `gates{G1_soc, G2_metro_wage, G3_liveness, G4_lca_prevailing_wage}`, `values{…}`, `flags[]`, `decision` and `reason`. Every value is `{value, source, label}`, with label ∈ record / script-output / your-input.
- **Human report** `salary-floor.report.md`: an executive summary first; then one table row per posting (Posting · SOC gate · Floor · Metro median · Posted range · Company H-1B median (all roles) · Decision); then per-posting evidence with labels, and the cannot-verify list.

Decisions: **Range clears floor** · **Range starts below floor** · **Floor only** (no range posted) · **Skip** (posting not live) · **Unresolved** (a gate failed; the reason is named).

## Stop conditions and next action per result

| Result | Means | Do |
|---|---|---|
| Range clears floor | the posted minimum ≥ floor | apply; never name a number below the floor |
| Range starts below floor | the posted minimum < floor | ask at or above the floor, or skip if the range's top is also low |
| Floor only | no range posted | use the floor as your ask |
| Skip | API 404 | no time this week |
| Unresolved: ambiguous-soc | candidate floors differ by more than the limit | read the duties, choose one SOC, record why, re-run |
| Unresolved: no-metro-match / missing / top-coded | no usable metro wage | fix the metro to an exact BLS title, or accept that there is no floor. **Do not substitute the national wage.** |

The mode must refuse to produce a floor whenever G1 or G2 fails.

## Proposed additions

- **[TODO-1 DATA SOURCE]** OFLC prevailing-wage levels (Online Wage Library, flag.dol.gov / flcdatacenter.com) by SOC × area × level, to close G4. *Why it belongs:* the employer must pay at least this to file an H-1B LCA. A student who accepts below Level I for the filed SOC may have an offer that cannot be sponsored as written. Closure: the file exists at a named path with a provenance note.
- **[TODO-2 DEV]** Pay ranges from Lever and Ashby public posting APIs (same 200/404 liveness rule). *Why:* Greenhouse is only part of the Boston market; CarGurus and Toast happen to use it. Closure: script + tests + conformance.
- **[TODO-3 DATA SOURCE]** The maintained `recipes/local-wage-adjustment.md` says its inputs are committed, but `git ls-files data/bls/local-wage` is empty on `main` at `015843d`. This recipe rebuilds them with `build_local_wage_inputs.py` and pins source checksums. *Why:* without the inputs the maintained recipe cannot run from a fresh clone. Closure: maintainers restore the files, or adopt the builder plus checksums.

## Verification checks

- `.venv/Scripts/python.exe -m unittest scripts/contrib/2026fa/kommurisi-data-role-salary-floor/test_salary_floor.py -v` → 13 tests OK.
- `python3 scripts/contrib/2026fa/kommurisi-data-role-salary-floor/mutation_test.py` → 4/4 mutants killed:
  - floor taken from the company H-1B median;
  - national fallback;
  - ambiguity gate removed;
  - liveness ignored.
- A hand cross-check of the report's Boston values against `MSA_M2024_dl.xlsx`, read directly.
- `npm run verify`, `npm run doctor`, `node scripts/pii-scan.mjs --diff main`.

## Logging rules

- One file per run in `logs/runs/2026fa-<handle>-<n>.md`. Never edit `logs/RUN_LOG.md` (CONTRIBUTING).
- No personal data: personas only. The persona's metro, program and graduation term are not identifying.

### Run-log template

```markdown
# 2026fa-<handle>-<n> — data-role-salary-floor v0.1.0
- **Date:** YYYY-MM-DD
- **Recipe:** recipes/cases/2026fa/<handle>-data-role-salary-floor.md v0.1.0 (status …, N open TODOs)
- **Mode:** sample | live
- **Inputs:** postings.json (persona: yes; N postings: R real, C CONSTRUCTED); pay-ranges.json captured <UTC>; BLS MSA_M2024_dl.xlsx sha256 …; BEA MARPP sha256 …; 80 Days CSV + O*NET compact as shipped at <commit>
- **Commands:** (verbatim)
- **Gates:** G1 … · G2 … · G3 … · G4 not-checked (TODO-1)
- **Result:** Range clears floor N · Below floor N · Floor only N · Skip N · Unresolved N
- **Outputs:** <out-dir>/salary-floor.{log.json,report.md}
- **Verified vs inferred:** records = BLS rows (file:line), 80 Days rows, API captures; your-input = SOC choices, floor percentile, spread limit; model-judgment = none
- **Open issues:** …
```
