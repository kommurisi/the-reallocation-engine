# FRICTIONAL — data-role-salary-floor

## Executive summary

This is the honest log of building the salary-floor mode. Part A records what happened while Claude Code built it on 21 October 2026: what broke, and what was changed. Part B is for Siddi to write in their own words; the course AI policy says the experience must be the student's.

## Part A: build log (Claude Code session, 2026-10-21)

**Assignment mismatch.** The pasted text matches `course/summer-2026/reallocation-engine-mode-build.md` exactly. Its paths (`recipes/`, `assignments/submissions/`, `mode/<name>-<domain>`) do not exist in the fall layout, and `CONTRIBUTING.md` (enforced by CI) requires `recipes/cases/2026fa/`, `course/2026fa/submissions/` and `contrib/2026fa-…`. The fall paths were followed. PR #31 is still open, against "one open PR per student", so Siddi chose to ask the TA before any push.

**The maintained script would not start.** `npm run bls:local-wage …` printed "missing .venv" with a `.venv` present. It hard-codes `.venv/bin/python`, and Windows uses `Scripts\python.exe` (evidence 01). After fixing that, `os.execv` split the interpreter path at the space in the user folder, because Windows `execv` does not quote. Fixed by re-launching with `subprocess` on Windows (evidence 02). This is one declared patch.

**Its data isn't in the repo.** Its README says the inputs are "committed", but `git ls-files data/bls/local-wage` is empty on `main`, and no branch or history has them. BLS answered `curl` with 403, so the file was saved through the browser, with approval. The builder's crosswalk count (387) matched the README, and the three documented checks reproduced to the cent (evidence 03). This was the moment the rebuild could be trusted.

**The domain finding.**
- Boston floors for "data" work run from $72,130 (13-1161) to $132,660 (15-1243), depending on the SOC.
- O\*NET lists "Data Analyst" under seven occupations.
- "Business Intelligence Analyst" has no BLS wage row of its own (it lives in 15-2051).
- This became gate G1 and failure mode 1.

**Few early-career postings.** A scan of Greenhouse boards for Boston employers in the 80 Days CSV found mostly senior data roles with posted ranges. The worked run therefore uses three real senior or mid postings plus three CONSTRUCTED tests, and the reflection says so.

**Errors caught in the build itself:**
- The shell mangled backslashes inside heredocs twice, which broke a privacy-scrub regex; it was rewritten as a script file.
- One evidence file holds Windows-1252 en dashes from the console; this is annotated, not rewritten.
- A mutant was misnamed "take-highest" when the code takes the lowest; it was renamed.
- The draft docs said "Data Analyst → seven codes with floors". The log showed only six have a Boston wage. Fixed.
- The report hid a posted range on Unresolved rows. It now shows the range, and all evidence was re-run afterwards.

**Checks:** 13/13 tests; 4/4 mutants killed; the audit (A1–A5) held; a re-run gave identical results; and a hand re-read of the BLS xlsx matched.

## Part B: my entries (Siddi, in my own words)

**2026-10-21 · the salary-floor mode**

- **I tried / expected:** I set out to add a salary-floor mode for data and BI job postings in Boston: given a posting, say the lowest pay worth accepting, using official BLS wage data. I expected the repo's existing wage script and data to work as they were.
- **What happened:** The repo's wage script couldn't run on Windows, and its data files were missing. After a one-file patch and rebuilding the data from the official downloads, the script reproduced its own documented examples. The worked run on 3 real Boston postings and 3 test cases gave a $102,400 floor. Klaviyo and Toast cleared it. CarGurus stayed Unresolved because its possible occupation codes give floors 42% apart. Toast's H-1B median was flagged as a misleading benchmark.
- **What I did / decided:** I approved the Windows patch. I chose to push to my fork only and not open a PR, since #31 is still open and the TA said grading is on Canvas. I signed the attestation in WORKED-RUN.md on 2026-10-21.
- **What Claude contributed, and what I accepted, changed or rejected:** Claude wrote the code and tests, ran every command, rebuilt the data and drafted the occupation-code choice for each posting and the floor rule (25th percentile, 15% spread). I accepted the occupation codes and the floor rule as drafted. I checked each choice against the posting before accepting.
