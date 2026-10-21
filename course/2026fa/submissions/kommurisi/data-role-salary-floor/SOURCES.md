# SOURCES — data-role-salary-floor

## Executive summary

This page lists every data source, tool and piece of code behind the salary-floor mode, and says plainly who did what. In short:
- The data is public government and company-posting data.
- One repository script was repaired and is reused, not copied.
- Claude Code wrote the new code and documents.
- Siddi chose the mode and approved the decisions that touch the outside world, and signs the results.

## Data (all public; nothing personal)

- **BLS OEWS, May 2024, metropolitan and nonmetropolitan areas.**
  - Source: https://www.bls.gov/oes/tables.htm → `oesm24ma.zip`, saved 2026-10-21 in the app's browser (BLS answers scripted downloads with HTTP 403).
  - Checksums: `oesm24ma.zip` sha256 `7bf915fc47e464983c5b8b8200d63a733ef90275c7af0576b78875e5b04d35d9`; `MSA_M2024_dl.xlsx` sha256 `2a172aed29693f50afa398be03fd107ce6bfff8b04e5fd163b4c5ddcf941d6ec` (BLS re-issued it on 2026-02-24).
- **BEA Regional Price Parities by MSA, 2008–2024.**
  - Source: https://apps.bea.gov/regional/zip/MARPP.zip, downloaded 2026-10-21.
  - Checksums: sha256 `5dbf2e6ac2af222cc9abc205586c9b480344d89392752eb689c3ec823a34c83e`; `MARPP_MSA_2008_2024.csv` sha256 `4ce7a7e2ea08ff721de83f50d8a70bb9c93956a49970462f462372aa58cee9f4`.
- **The repo, as shipped at `015843d`:**
  - `data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv` (sha256 `eccdee2a…6270`);
  - `data/bls/compact/soc_occupation_compact.csv` (sha256 `bac5acf7…43d1`).
- **Greenhouse public job board API**, `boards-api.greenhouse.io`, captured 2026-10-21T21:26Z: Klaviyo job 7737707003, CarGurus 8096751, Toast 8243192, and the nonexistent Klaviyo 1000000001. These are public postings. Nothing personal.

## Code reused (called, not copied)

- `scripts/bls/local-wage-adjustment.py` (maintained): `load_tables`, `resolve_metro` and `evaluate_pair`, imported by `salary_floor.py`.
  - **Patched** (the one declared maintained-file patch): two Windows fixes, the venv interpreter path and `execv` quoting. The behaviour is otherwise unchanged; its three documented checks reproduce exactly.

## Personas

`fixtures/worked-run/postings.json` uses a fictional persona modelled on the author's situation (program type, city, graduation term, target role family). It has no name, contact details or real dates. Three of the six postings are CONSTRUCTED test cases and are labelled so everywhere.

## Tools

- Python 3.13.2 with pandas 3.0.6 and openpyxl 3.1.5, in the repo `.venv`; Node 24 for `npm run`; Git for Windows; curl.
- Claude Code (Anthropic, Claude Opus 5.5).

## What Claude contributed (Claude Code session, 2026-10-21)

- **Investigated the repo.** Found that the pasted assignment is the summer-2026 text, so it followed the fall `CONTRIBUTING.md` paths instead. Found PR #31 still open, against the "one open PR" rule.
- **Proposed three modes.** Siddi chose the salary floor.
- **Found and fixed problems in the maintained wage script.**
  - Found its two Windows bugs and that its inputs are missing from `main`.
  - Wrote the patch, which Siddi approved.
  - Wrote `build_local_wage_inputs.py`, and reproduced the documented checks.
- **Downloaded the data:** BLS through the app's browser and BEA by script, both approved by Siddi, with the checksums recorded.
- **Wrote all the mode's code and tests:**
  - `salary_floor.py`, `fetch_pay_ranges.py`, `audit_log.py`;
  - `test_salary_floor.py` (13 tests) and `mutation_test.py` (4 mutants);
  - the fixtures.
- **Chose, as drafts for Siddi to confirm:**
  - the three real postings;
  - every SOC candidate list and SOC choice in `postings.json`;
  - the 25th-percentile floor rule and the 15% spread limit.
- **Wrote the documents:** the recipe and card, the README, DOMAIN-JUSTIFICATION, WORKED-RUN, this file, the Part A build log in FRICTIONAL.md, and the run log.
- **Ran every command** in WORKED-RUN and the repo checks.
- **Caught one error in its own draft docs** (the "seven codes with floors" claim) and corrected it.

## What Siddi decided

- Treat this as a new assignment, separate from the Oct 3 recipe.
- Build the **salary-floor** mode.
- Download the BLS file in the app browser, and BEA by script.
- Patch the maintained script and declare it in the PR.
- Ask the TA before any push or PR, given PR #31.
- *[Siddi: add here anything you changed, rejected, or confirmed: the SOC choices, the floor rule, the postings.]*
