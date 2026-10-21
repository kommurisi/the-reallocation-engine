# Domain justification — data-role-salary-floor

## Executive summary

This page explains who the salary-floor mode is for and what it shows them that they can't easily see. An international student looking for a first data job in Boston can't easily tell whether an offer is low. They usually don't know which official occupation their job counts as, and that one choice moves the fair minimum by tens of thousands of dollars. The mode makes that choice visible, gives a floor from government wage data, and refuses to give one when the evidence is not there.

## Who uses it, and when

An F-1 student in a STEM-designated **MS Information Systems** program in Boston, graduating in December 2026 and moving to OPT. They are targeting **early-career BI, analytics and data roles** that will need H-1B sponsorship. They use the mode at two moments:

1. **The recruiter screen**, when asked "what are your salary expectations?";
2. **The offer**, when deciding whether to accept, counter, or walk away.

Both moments come with time pressure: the 90-day OPT unemployment limit makes accepting the first offer tempting.

## The information asymmetry

The employer knows three things the student usually does not:

- **What the local market pays for the occupation.** BLS publishes metro wage percentiles, but in a 30 MB spreadsheet keyed by occupation code, not by job title.
- **Which occupation code the job is.** The employer, usually through its immigration attorney, chooses that code on the H-1B Labor Condition Application. The student rarely sees it before the petition is being prepared. It decides the answer. In Boston (BLS, May 2024), "Data Analyst" is an O\*NET alternate title for seven occupations; six have a Boston wage, with 25th-percentile floors from **$46,190** (Social Science Research Assistants) to **$132,660** (Database Architects). "Business Intelligence Analyst" has no wage row of its own: BLS folds it into **Data Scientists** (15-2051, Boston p25 **$102,400**).
- **What a legal H-1B wage would be.** The prevailing wage level for that code and area. The mode does not have this yet and says so (TODO-1).

## Engine layers

- **Cognitive Pivot (BLS/O\*NET):** the metro wage percentiles, through the maintained `local-wage-adjustment` gates, plus O\*NET's title-to-occupation map.
- **80 Days to Stay:** each company's recorded H-1B median salary and approval count, used as context.
- **Job-Ops:** the posting's liveness and its published pay range, from the Greenhouse job API.

## Failure modes specific to this domain

1. **The occupation-code trap.**
   - *The shape of the error:* a confident floor computed for the wrong code. A "Data Analyst" priced as a Data Scientist expects $102,400 and may be screened out of a role the employer files as Market Research Analyst (Boston p25 $72,130). Priced as a market researcher, the same person under-asks by $30,000.
   - *Hardest to catch for:* the new graduate. The job title gives no hint, and the code appears only later, on a filing they rarely see. A generic salary website hides it completely, because it averages titles, not codes.
   - *Mitigation:* the ambiguity gate refuses to give a floor until a person picks one code, and shows how far apart the candidates are.
2. **The sponsor-median anchor.**
   - *The shape of the error:* treating the 80 Days `median_salary_offered` as a pay benchmark. It is the median of **every** H-1B filing at the company, and that is dominated by senior engineers. At Toast it is **$177,341**, above Boston's 75th percentile for data scientists ($166,710).
   - *Hardest to catch for:* the student who most wants a well-known sponsor. That number is the one they look at, and it makes an early-career offer look insultingly low when it isn't.
   - *Mitigation:* the mode shows it only as company-wide context, flags it when it exceeds the role's metro p75, and a test fails if it ever becomes the floor.
