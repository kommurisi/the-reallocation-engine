# Data-role salary floor — 2026-10-21

## Executive summary

This report sets a **salary floor** for each of 6 data and business-intelligence job postings in the Boston area: the lowest pay that matches what the bottom quarter of people in that occupation already earn there, from public government wage data. Read it before you name a salary or accept an offer. It also shows why a company's average pay for its visa-sponsored staff is not a fair benchmark for one early-career role.

**Found:** 2 where the posted pay range starts at or above the floor; 1 where the posted range starts below the floor, so ask for at least the floor; 1 where the posting is no longer live, so nothing was compared; 2 where a person must decide something first (which occupation the job is, or the exact metro name). 3 of the 6 postings are made-up test cases and are marked as such. It cannot yet check the legal minimum wage for a visa-sponsored version of the job.

## Run record

**For:** Fictional persona modelled on the author's situation: F-1 MS Information Systems (STEM) student in Boston, graduating Dec 2026, targeting early-career BI / analytics roles that will need H-1B sponsorship. No name, contacts or real dates.

**Metro:** Boston-Cambridge-Newton, MA-NH · **Floor rule:** BLS metro nominal **25th percentile** of the chosen SOC (your-input) · **SOC spread limit:** 15%

*Labels — record: read from a file or a saved API response · script-output: computed here or by the maintained script · your-input: a human choice · model-judgment: none in this run (no model was called).*

| Posting | SOC (gate) | Floor | Metro median | Posted range | Company H-1B median (all roles) | Decision |
|---|---|---|---|---|---|---|
| Klaviyo — Analytics Engineer | ok: 15-2051 | $102,400 | $131,830 | $140,000–$210,000 | $126,000 | **Range clears floor** |
| CarGurus — Senior Product Data Analyst | unresolved: ambiguous-soc (floors differ by 42%) | — | — | $120,000–$151,000 | — | **Unresolved** |
| Toast — Senior Manager, CS Data & Analytics | ok: 15-2051 | $102,400 | $131,830 | $145,000–$232,000 | $177,341 | **Range clears floor** |
| Northwind Analytics — Data Analyst (CONSTRUCTED) | ok: 15-2051 | $102,400 | $131,830 | $65,000–$78,000 | — | **Range starts below floor** |
| Klaviyo — Data Analyst (CONSTRUCTED) | ok: 15-2051 | $102,400 | $131,830 | — | $126,000 | **Skip** |
| Klaviyo — Business Intelligence Analyst (CONSTRUCTED) | — | — | — | $90,000–$110,000 | — | **Unresolved** |

## Per posting: evidence and reasons

### Klaviyo — Analytics Engineer
- **Decision:** Range clears floor — posted minimum $140,000 ≥ floor $102,400
- Gate G3_liveness: `live`
- Gate G1_soc: `ok: 15-2051`
- Gate G2_metro_wage: `ok`
- Gate G4_lca_prevailing_wage: `not-checked [TODO-1: OFLC wage level not in repo]`
- api_status: `200` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/fixtures/worked-run/pay-ranges.json (2026-10-21T21:26:05+00:00)
- posted_range: `[140000.0, 210000.0]` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/fixtures/worked-run/pay-ranges.json pay_input_ranges[0] (Base Pay Range For US Locations:)
- soc_candidates_onet: `"no exact O*NET title match (sample only)"` **[record]** — data/bls/compact/soc_occupation_compact.csv
- soc_candidates_added: `["15-1243", "15-2051"]` **[your-input]** — postings.json
- metro_floor_by_soc: `{"15-1243": "132660", "15-2051": "102400"}` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/.data/metro_oews.csv via maintained evaluate_pair
- soc_choice: `"15-2051"` **[your-input]** — your-input: analytics/BI modelling work (O*NET 15-2051.01 BI Analysts); the lower of the two candidate floors, so the conservative pick
- soc_floor_spread: `0.296` **[script-output]** — script-output: max/min of the candidates' metro floors
- floor: `102400.0` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/.data/metro_oews.csv:16965 A_PCT25 (Data Scientists, Boston-Cambridge-Newton, MA-NH, May 2024)
- metro_median: `131830.0` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/.data/metro_oews.csv:16965 A_MEDIAN
- metro_p75: `166710.0` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/.data/metro_oews.csv:16965 A_PCT75
- metro_employment: `"8220"` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/.data/metro_oews.csv:16965 TOT_EMP
- rpp_adjusted_median: `121764.91` **[script-output]** — maintained script (RPP 108.2660)
- national_median: `112590.0` **[record]** — data/bls/compact/soc_occupation_compact.csv
- crosscheck_p25: `true` **[script-output]** — maintained adjusted_low × RPP/100 = 102400.00
- company_h1b_median_all_roles: `126000.0` **[record]** — data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv:14495 median_salary_offered (all H-1B roles at KLAVIYO INC, not this role)
- company_h1b_approvals: `"154.0"` **[record]** — data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv:14495 Total Approvals

### CarGurus — Senior Product Data Analyst
- **Decision:** Unresolved — ambiguous-soc: 3 candidate SOCs, floors differ by 42%; choose one
- Gate G3_liveness: `live`
- Gate G1_soc: `unresolved: ambiguous-soc (floors differ by 42%)`
- api_status: `200` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/fixtures/worked-run/pay-ranges.json (2026-10-21T21:26:05+00:00)
- posted_range: `[120000.0, 151000.0]` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/fixtures/worked-run/pay-ranges.json pay_input_ranges[0] (Position Pay Range)
- soc_candidates_onet: `"no exact O*NET title match (sample only)"` **[record]** — data/bls/compact/soc_occupation_compact.csv
- soc_candidates_added: `["15-2051", "13-1161", "15-2041"]` **[your-input]** — postings.json
- metro_floor_by_soc: `{"13-1161": "72130", "15-2041": "81950", "15-2051": "102400"}` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/.data/metro_oews.csv via maintained evaluate_pair
- soc_floor_spread: `0.42` **[script-output]** — script-output: max/min of the candidates' metro floors

### Toast — Senior Manager, CS Data & Analytics
- **Decision:** Range clears floor — posted minimum $145,000 ≥ floor $102,400
- Gate G3_liveness: `live`
- Gate G1_soc: `ok: 15-2051`
- Gate G2_metro_wage: `ok`
- Gate G4_lca_prevailing_wage: `not-checked [TODO-1: OFLC wage level not in repo]`
- api_status: `200` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/fixtures/worked-run/pay-ranges.json (2026-10-21T21:26:05+00:00)
- posted_range: `[145000.0, 232000.0]` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/fixtures/worked-run/pay-ranges.json pay_input_ranges[0] (Pay Range)
- soc_candidates_onet: `"no exact O*NET title match (sample only)"` **[record]** — data/bls/compact/soc_occupation_compact.csv
- soc_candidates_added: `["15-2051", "11-3021"]` **[your-input]** — postings.json
- metro_floor_by_soc: `{"11-3021": "169010", "15-2051": "102400"}` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/.data/metro_oews.csv via maintained evaluate_pair
- soc_choice: `"15-2051"` **[your-input]** — your-input: leads analytics work; 11-3021 (computer & information systems managers) is the other filing a lawyer might choose
- soc_floor_spread: `0.65` **[script-output]** — script-output: max/min of the candidates' metro floors
- floor: `102400.0` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/.data/metro_oews.csv:16965 A_PCT25 (Data Scientists, Boston-Cambridge-Newton, MA-NH, May 2024)
- metro_median: `131830.0` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/.data/metro_oews.csv:16965 A_MEDIAN
- metro_p75: `166710.0` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/.data/metro_oews.csv:16965 A_PCT75
- metro_employment: `"8220"` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/.data/metro_oews.csv:16965 TOT_EMP
- rpp_adjusted_median: `121764.91` **[script-output]** — maintained script (RPP 108.2660)
- national_median: `112590.0` **[record]** — data/bls/compact/soc_occupation_compact.csv
- crosscheck_p25: `true` **[script-output]** — maintained adjusted_low × RPP/100 = 102400.00
- company_h1b_median_all_roles: `177341.0` **[record]** — data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv:27011 median_salary_offered (all H-1B roles at TOAST INC, not this role)
- company_h1b_approvals: `"150.0"` **[record]** — data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv:27011 Total Approvals
- ⚠ company-h1b-median-above-metro-p75: senior/engineering-weighted; do not anchor on it

### Northwind Analytics — Data Analyst (CONSTRUCTED test posting)
- **Decision:** Range starts below floor — posted minimum $65,000 is $37,400 under the floor $102,400; ask at or above the floor
- Gate G3_liveness: `unchecked`
- Gate G1_soc: `ok: 15-2051`
- Gate G2_metro_wage: `ok`
- Gate G4_lca_prevailing_wage: `not-checked [TODO-1: OFLC wage level not in repo]`
- posted_range: `[65000, 78000]` **[your-input]** — postings.json (constructed)
- soc_candidates_onet: `["13-2099.01 Financial Quantitative Analysts", "15-1243.00 Database Architects", "15-2041.00 Statisticians", "15-2051.00 Data Scientists", "15-2099.01 Bioinformatics Technicians", "19-3022.00 Survey Researchers", "19-4061.00 Social Science Research Assistants"]` **[record]** — data/bls/compact/soc_occupation_compact.csv
- metro_floor_by_soc: `{"13-2099": "67720", "15-1243": "132660", "15-2041": "81950", "15-2051": "102400", "15-2099": "72920", "19-3022": "missing: no-occupation-row", "19-4061": "46190"}` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/.data/metro_oews.csv via maintained evaluate_pair
- soc_choice: `"15-2051"` **[your-input]** — your-input: the persona targets BI-analyst work (15-2051.01)
- soc_floor_spread: `1.872` **[script-output]** — script-output: max/min of the candidates' metro floors
- floor: `102400.0` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/.data/metro_oews.csv:16965 A_PCT25 (Data Scientists, Boston-Cambridge-Newton, MA-NH, May 2024)
- metro_median: `131830.0` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/.data/metro_oews.csv:16965 A_MEDIAN
- metro_p75: `166710.0` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/.data/metro_oews.csv:16965 A_PCT75
- metro_employment: `"8220"` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/.data/metro_oews.csv:16965 TOT_EMP
- rpp_adjusted_median: `121764.91` **[script-output]** — maintained script (RPP 108.2660)
- national_median: `112590.0` **[record]** — data/bls/compact/soc_occupation_compact.csv
- crosscheck_p25: `true` **[script-output]** — maintained adjusted_low × RPP/100 = 102400.00
- company_h1b_median_all_roles: `null` **[record]** — no exact row for 'NORTHWIND ANALYTICS' in data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv
- ⚠ liveness-unchecked: the comparison is provisional until the posting is confirmed live

### Klaviyo — Data Analyst (CONSTRUCTED test posting)
- **Decision:** Skip — posting not live (Greenhouse API 404): no comparison
- Gate G3_liveness: `not-live`
- Gate G1_soc: `ok: 15-2051`
- Gate G2_metro_wage: `ok`
- Gate G4_lca_prevailing_wage: `not-checked [TODO-1: OFLC wage level not in repo]`
- api_status: `404` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/fixtures/worked-run/pay-ranges.json (2026-10-21T21:26:05+00:00)
- soc_candidates_onet: `["13-2099.01 Financial Quantitative Analysts", "15-1243.00 Database Architects", "15-2041.00 Statisticians", "15-2051.00 Data Scientists", "15-2099.01 Bioinformatics Technicians", "19-3022.00 Survey Researchers", "19-4061.00 Social Science Research Assistants"]` **[record]** — data/bls/compact/soc_occupation_compact.csv
- metro_floor_by_soc: `{"13-2099": "67720", "15-1243": "132660", "15-2041": "81950", "15-2051": "102400", "15-2099": "72920", "19-3022": "missing: no-occupation-row", "19-4061": "46190"}` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/.data/metro_oews.csv via maintained evaluate_pair
- soc_choice: `"15-2051"` **[your-input]** — your-input: constructed liveness test (a job id that does not exist)
- soc_floor_spread: `1.872` **[script-output]** — script-output: max/min of the candidates' metro floors
- floor: `102400.0` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/.data/metro_oews.csv:16965 A_PCT25 (Data Scientists, Boston-Cambridge-Newton, MA-NH, May 2024)
- metro_median: `131830.0` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/.data/metro_oews.csv:16965 A_MEDIAN
- metro_p75: `166710.0` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/.data/metro_oews.csv:16965 A_PCT75
- metro_employment: `"8220"` **[record]** — scripts/contrib/2026fa/kommurisi-data-role-salary-floor/.data/metro_oews.csv:16965 TOT_EMP
- rpp_adjusted_median: `121764.91` **[script-output]** — maintained script (RPP 108.2660)
- national_median: `112590.0` **[record]** — data/bls/compact/soc_occupation_compact.csv
- crosscheck_p25: `true` **[script-output]** — maintained adjusted_low × RPP/100 = 102400.00
- company_h1b_median_all_roles: `126000.0` **[record]** — data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv:14495 median_salary_offered (all H-1B roles at KLAVIYO INC, not this role)
- company_h1b_approvals: `"154.0"` **[record]** — data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv:14495 Total Approvals

### Klaviyo — Business Intelligence Analyst (CONSTRUCTED test posting)
- **Decision:** Unresolved — no-metro-match (no national fallback)
- Gate G3_liveness: `unchecked`
- Gate G2_metro_wage: `missing: no-metro-match`
- posted_range: `[90000, 110000]` **[your-input]** — postings.json (constructed)
- soc_candidates_onet: `["15-2051.01 Business Intelligence Analysts"]` **[record]** — data/bls/compact/soc_occupation_compact.csv

## What this run cannot verify

- The **legal H-1B floor**: the OFLC prevailing wage level for this SOC and area (G4 is always `not-checked`; TODO-1).
- **Which SOC the employer's attorney will file** on the LCA. The SOC choice here is a human judgment.
- **This** posting's level, bonus or equity. BLS percentiles are base wages for the whole occupation in the metro.
- Any year after May 2024 (the OEWS reference period).
- That the company's H-1B median describes this role. It covers all its H-1B roles, and is context only.
