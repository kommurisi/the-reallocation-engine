---
status: DRAFT
todos_open: 3
last_gate: "sample-run executed 2026-10-21 (logs/runs/2026fa-kommurisi-2.md) — not a lifecycle promotion"
attestation: null
recipe_version: 0.1.0
---

# Data-role salary floor — human card

## Executive summary

**What this is:** a one-page guide to a tool that tells you the lowest salary you should accept for a data or business-intelligence job in a given city, using the government's own wage survey.

**Why read it:** international students are often told to "just be flexible" on pay. But an offer far below what others in the same occupation earn locally is a warning sign. It can also make a later H-1B petition harder, because the employer must pay at least the official prevailing wage.

**What it found in the worked run (Boston, October 2026):**
- Two real postings clear the floor.
- One real posting can't get a floor until a person decides which occupation it is. The candidate floors differ by 42%.
- A company's average pay for its visa holders ($177,341 at Toast) is no guide to an entry-level offer.

**Agent twin:** `recipes/cases/2026fa/kommurisi-data-role-salary-floor.md` (DRAFT, v0.1.0).

## Purpose

Answer one question per posting: *what is the least I should accept for this occupation in this city, and does this posting start above it?*

## Use it when

- before a recruiter screen asks for your salary expectations;
- before accepting an offer;
- when a posting's range looks low and you want to know whether it is low.

## What it can verify

- The 25th-percentile, median and 75th-percentile wages that BLS measured (May 2024) for an occupation in a metro, traced to the row they came from.
- Why there is **no** number, when there isn't one: the city name isn't an exact BLS area, the occupation has no row there, or BLS suppressed the estimate. It never substitutes a national figure.
- How much the answer depends on the occupation code you pick.
- Whether a Greenhouse posting was live when checked, and the base pay range it published.

## What it cannot verify

- The **legal minimum** for an H-1B version of the job: the OFLC prevailing wage level. Look that up yourself before you accept (a proposed addition will close this).
- Which occupation code the employer's immigration attorney will actually file.
- Bonus, equity, seniority, or anything after May 2024.
- That a company's average H-1B salary says anything about **your** role.

## Annotated commands

Rebuild the wage inputs once. Save `oesm24ma.zip` from bls.gov in a browser, then:

```bash
.venv/Scripts/python.exe scripts/contrib/2026fa/kommurisi-data-role-salary-floor/build_local_wage_inputs.py \
  --bls ~/Downloads/reallocation-data/oesm24ma/oesm24ma/MSA_M2024_dl.xlsx \
  --bea ~/Downloads/reallocation-data/marpp/MARPP_MSA_2008_2024.csv
```

Capture each posting's status and range. This is the only network step:

```bash
python3 scripts/contrib/2026fa/kommurisi-data-role-salary-floor/fetch_pay_ranges.py
```

Run the mode offline. With no flags it reruns the committed worked run:

```bash
python3 scripts/contrib/2026fa/kommurisi-data-role-salary-floor/salary_floor.py
```

Prove it refuses safely:

```bash
.venv/Scripts/python.exe -m unittest scripts/contrib/2026fa/kommurisi-data-role-salary-floor/test_salary_floor.py -v
python3 scripts/contrib/2026fa/kommurisi-data-role-salary-floor/mutation_test.py
```

## Reading a result

| You see | It means | Do |
|---|---|---|
| **Range clears floor** | the posting's lowest pay is at or above the floor | apply; never name a number below the floor |
| **Range starts below floor** | the posting may start you below what the bottom quarter earns | ask at or above the floor |
| **Floor only** | no range posted | the floor is your ask |
| **Skip** | the posting is gone | nothing to do |
| **Unresolved: ambiguous-soc** | the job could be several occupations whose floors differ a lot | read the duties, pick one, write down why, re-run |
| **Unresolved: no-metro-match** | the city name isn't an exact BLS area | use the exact BLS title (e.g. "Boston-Cambridge-Newton, MA-NH"). **Don't** use the national figure |
| ⚠ company H-1B median above metro p75 | the company's sponsored staff are mostly senior engineers | don't anchor on that number |

## Named failure modes

1. **The occupation-code trap.** BLS publishes wages for 6-digit SOC codes. "Business Intelligence Analyst" (O\*NET 15-2051.01) shares the **Data Scientists** wage row. "Data Analyst" is an O\*NET alternate title for seven occupations. Six have a Boston wage, with floors from $46,190 to $132,660. Pick the code with the highest wage and you price yourself out; pick the lowest and you leave money on the table. A new graduate rarely sees the code the employer files. Mitigation: the ambiguity gate refuses until you choose, and shows the spread.
2. **The sponsor-median anchor.** The 80 Days CSV's `median_salary_offered` averages every H-1B filing at a company. At Toast it is $177,341, above the 75th percentile for Boston data scientists ($166,710). Students who most want a well-known sponsor are the likeliest to anchor on it. Mitigation: it is shown only as company-wide context, and flagged when it exceeds the role's metro p75.
3. **National for local.** A national median quietly stands in when the city name doesn't match. Mitigation: no fallback, ever. The no-metro case is Unresolved, and a test fails if a fallback appears.
