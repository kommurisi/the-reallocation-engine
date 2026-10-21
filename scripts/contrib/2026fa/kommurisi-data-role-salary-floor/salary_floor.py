#!/usr/bin/env python3
"""data-role-salary-floor: a sourced salary floor for a data/BI posting in one metro, or a named refusal.

For each posting:
  G1 SOC choice     O*NET alternate-title lookup lists candidate SOCs (record, sample only). If the candidates'
                    metro floors differ by more than --soc-spread and no human choice is given, refuse:
                    Unresolved: ambiguous-soc.
  G2 metro wage     scripts/bls/local-wage-adjustment.py (maintained) decides ok / missing + reason for
                    (metro, SOC). No national fallback, ever.
  G3 liveness       Greenhouse job API status captured by fetch_pay_ranges.py (404 closes the gate).
  G4 LCA wage       OFLC prevailing wage level for (SOC, area): NOT in the repo -> always "not-checked" [TODO].
Floor = the BLS metro nominal A_PCT<p> (default 25) of the chosen SOC, read from the same OEWS file the
maintained script read. The company's H-1B median (80 Days CSV) is shown as company-wide context, never
used as the floor.

    python3 salary_floor.py                       # reruns the committed worked run
    python3 salary_floor.py --input <postings.json> --pay <pay-ranges.json> --out-dir <dir>
Exit: 0 ran · 2 usage / bad input / missing data file.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import re
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
DATA = HERE / ".data"
MAINTAINED = REPO / "scripts" / "bls" / "local-wage-adjustment.py"
CSV_80 = REPO / "data" / "80-days-to-stay" / "80-days-csv" / "mapped_student_employment_targets_v3.csv"
ONET = REPO / "data" / "bls" / "compact" / "soc_occupation_compact.csv"
TOP_CODED = "#"   # BLS: wage >= $239,200/yr; the true value is unknown


def load_maintained():
    """Import the maintained local-wage script (hyphenated file) so its gates are used, not re-implemented."""
    spec = importlib.util.spec_from_file_location("local_wage_adjustment", MAINTAINED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rec(value, source, label="record"):
    return {"value": value, "source": source, "label": label}


def rel(p: Path) -> str:
    try:
        return Path(p).resolve().relative_to(REPO).as_posix()
    except ValueError:
        return Path(p).as_posix()


def soc_candidates_from_onet(title: str, onet_path: Path) -> list[dict]:
    """Exact (case-insensitive) match of the posting title against O*NET titles and alternate-title samples."""
    key = title.strip().casefold()
    out = []
    with open(onet_path, encoding="utf-8", newline="") as f:
        for i, row in enumerate(csv.DictReader(f), start=2):
            alts = [a.strip().casefold() for a in (row.get("alternate_titles_sample") or "").split(";")]
            alts += [re.sub(r"\s*\(.*\)$", "", a) for a in alts]
            if key in alts or key == row["title"].strip().casefold() or key + "s" == row["title"].strip().casefold():
                out.append({"onet": row["onet_soc_code"], "soc": row["bls_soc_code"], "title": row["title"],
                            "source": f"{rel(onet_path)}:{i}"})
    return out


def oews_row(oews_path: Path, area: str, soc: str):
    """The OEWS detailed row for (AREA, SOC) with its file line, for the nominal percentiles."""
    with open(oews_path, encoding="utf-8", newline="") as f:
        for i, row in enumerate(csv.DictReader(f), start=2):
            if row["AREA"] == area and row["OCC_CODE"] == soc and row["O_GROUP"] == "detailed":
                return row, i
    return None, None


def company_row(csv_path: Path, name: str):
    if not name:
        return None, None
    with open(csv_path, encoding="utf-8", newline="") as f:
        for i, row in enumerate(csv.DictReader(f), start=2):
            if row["company_name"].strip().upper() == name.strip().upper():
                return row, i
    return None, None


def money(v):
    return None if v in (None, "") else float(str(v).replace(",", ""))


def evaluate(posting, profile, pay, mw, tables, paths):
    by_area, by_title, wage_index, rpp_by_fips, area_to_fips, national = tables
    pct = int(profile.get("floor_percentile", 25))
    metro = posting.get("metro") or profile["metro"]
    out = {"id": posting["id"], "company": posting["company"], "title": posting["title"], "metro": metro,
           "constructed": bool(posting.get("constructed")), "gates": {}, "flags": [], "values": {}}
    v = out["values"]

    # G3 liveness (gate) from the captured Greenhouse API status
    gh = posting.get("greenhouse")
    live = "unchecked"
    if gh:
        cap = (pay.get("jobs") or {}).get(f"{gh['board']}/{gh['job_id']}")
        if cap:
            live = "live" if cap.get("status") == 200 else "not-live" if cap.get("status") == 404 else "unchecked"
            v["api_status"] = rec(cap.get("status"), f"{paths['pay']} ({pay.get('checked_at')})")
    out["gates"]["G3_liveness"] = live

    # Posted range (record from the capture, or typed for a constructed posting). Read before any gate can stop,
    # so a person resolving an Unresolved posting still sees what it pays.
    rng = None
    if gh:
        cap = (pay.get("jobs") or {}).get(f"{gh['board']}/{gh['job_id']}") or {}
        prs = cap.get("pay_input_ranges") or []
        if prs and prs[0].get("currency_type") == "USD":
            rng = (prs[0]["min_cents"] / 100, prs[0]["max_cents"] / 100)
            v["posted_range"] = rec(list(rng), f"{paths['pay']} pay_input_ranges[0] ({prs[0].get('title', '').strip()})")
    elif posting.get("posted_range"):
        rng = tuple(posting["posted_range"])
        v["posted_range"] = rec(list(rng), "postings.json (constructed)" if posting.get("constructed") else "postings.json", "your-input")

    # G1 SOC candidates: O*NET exact-title lookup (record) plus any the human added (your-input)
    onet_hits = soc_candidates_from_onet(posting["title"], paths["onet"])
    cands = sorted({h["soc"] for h in onet_hits} | set(posting.get("soc_candidates_added", [])))
    v["soc_candidates_onet"] = rec([f"{h['onet']} {h['title']}" for h in onet_hits] or "no exact O*NET title match (sample only)",
                                   rel(paths["onet"]))
    if posting.get("soc_candidates_added"):
        v["soc_candidates_added"] = rec(posting["soc_candidates_added"], "postings.json", "your-input")

    resolved = mw.resolve_metro(metro, by_area, by_title)
    if resolved is None:
        out["gates"]["G2_metro_wage"] = "missing: no-metro-match"
        out["decision"] = "Unresolved"
        out["reason"] = "no-metro-match (no national fallback)"
        return out
    area, area_title = resolved

    per_soc = {}
    for soc in cands:
        r = mw.evaluate_pair(area, soc, by_area=by_area, by_title=by_title, wage_index=wage_index,
                             rpp_by_fips=rpp_by_fips, area_to_fips=area_to_fips, national=national,
                             run_date=str(date.today()), bls_src=rel(paths["oews"]), bea_src=rel(paths["rpp"]))
        row, line = oews_row(paths["oews"], area, soc)
        p = (row or {}).get(f"A_PCT{pct}") if pct != 50 else (row or {}).get("A_MEDIAN")
        per_soc[soc] = {"status": r["status"], "reason": r["missing_reason"], "row": row, "line": line,
                        "floor_raw": p, "maintained": r}
    v["metro_floor_by_soc"] = rec({s: (d["floor_raw"] if d["status"] == "ok" else f"missing: {d['reason']}")
                                   for s, d in per_soc.items()}, f"{rel(paths['oews'])} via maintained evaluate_pair")

    ok_floors = {s: money(d["floor_raw"]) for s, d in per_soc.items()
                 if d["status"] == "ok" and d["floor_raw"] not in (None, "", TOP_CODED)}
    choice = posting.get("soc_choice")
    if choice:
        v["soc_choice"] = rec(choice, posting.get("soc_choice_reason", "postings.json"), "your-input")
        per_soc.setdefault(choice, None)
    spread = (max(ok_floors.values()) / min(ok_floors.values()) - 1) if len(ok_floors) > 1 else 0.0
    v["soc_floor_spread"] = rec(round(spread, 3), "script-output: max/min of the candidates' metro floors", "script-output")
    if not choice:
        if len(cands) == 1:
            choice = cands[0]
        elif not cands:
            out["gates"]["G1_soc"] = "unresolved: no-soc-candidate"
            out["decision"], out["reason"] = "Unresolved", "no SOC candidate: name one in postings.json"
            return out
        elif spread > float(profile.get("soc_spread_limit", 0.15)):
            out["gates"]["G1_soc"] = f"unresolved: ambiguous-soc (floors differ by {spread:.0%})"
            out["decision"] = "Unresolved"
            out["reason"] = f"ambiguous-soc: {len(cands)} candidate SOCs, floors differ by {spread:.0%}; choose one"
            return out
        else:
            choice = min(ok_floors, key=ok_floors.get)   # all close: take the lowest, conservative
    out["gates"]["G1_soc"] = f"ok: {choice}"

    d = per_soc.get(choice)
    if d is None:   # human chose a SOC outside the candidate list: evaluate it the same way
        r = mw.evaluate_pair(area, choice, by_area=by_area, by_title=by_title, wage_index=wage_index,
                             rpp_by_fips=rpp_by_fips, area_to_fips=area_to_fips, national=national,
                             run_date=str(date.today()), bls_src=rel(paths["oews"]), bea_src=rel(paths["rpp"]))
        row, line = oews_row(paths["oews"], area, choice)
        d = {"status": r["status"], "reason": r["missing_reason"], "row": row, "line": line,
             "floor_raw": (row or {}).get(f"A_PCT{pct}"), "maintained": r}
    if d["status"] != "ok":
        out["gates"]["G2_metro_wage"] = f"missing: {d['reason']}"
        out["decision"], out["reason"] = "Unresolved", f"{d['reason']} for {choice} in {area_title} (no fallback)"
        return out
    if d["floor_raw"] in (None, "", TOP_CODED):
        out["gates"]["G2_metro_wage"] = "missing: top-coded-or-blank-percentile"
        out["decision"], out["reason"] = "Unresolved", f"A_PCT{pct} is '{d['floor_raw']}' (BLS top-code/blank)"
        return out
    out["gates"]["G2_metro_wage"] = "ok"
    row, line, m = d["row"], d["line"], d["maintained"]
    src = f"{rel(paths['oews'])}:{line}"
    floor = money(d["floor_raw"])
    v["floor"] = rec(floor, f"{src} A_PCT{pct} ({row['OCC_TITLE']}, {area_title}, May 2024)")
    v["metro_median"] = rec(money(row["A_MEDIAN"]), f"{src} A_MEDIAN")
    v["metro_p75"] = rec(money(row["A_PCT75"]) if row["A_PCT75"] != TOP_CODED else None, f"{src} A_PCT75")
    v["metro_employment"] = rec(row["TOT_EMP"], f"{src} TOT_EMP")
    v["rpp_adjusted_median"] = rec(money(m["adjusted_wage_median"]), f"maintained script (RPP {m['bea_rpp_value']})", "script-output")
    v["national_median"] = rec(money(m["national_median_wage"]), rel(paths["national"]))
    # cross-check: the maintained script's RPP-adjusted p25 times RPP/100 must give back BLS's nominal p25
    if pct == 25 and m["adjusted_wage_band_low"]:
        back = money(m["adjusted_wage_band_low"]) * money(m["bea_rpp_value"]) / 100
        v["crosscheck_p25"] = rec(abs(back - floor) <= 1.0, f"maintained adjusted_low × RPP/100 = {back:.2f}", "script-output")

    # Company H-1B lens: company-wide, never the floor
    crow, cline = company_row(paths["csv80"], posting.get("csv_name", ""))
    if crow:
        cm = money(crow.get("median_salary_offered"))
        v["company_h1b_median_all_roles"] = rec(cm, f"{rel(paths['csv80'])}:{cline} median_salary_offered (all H-1B roles at {crow['company_name']}, not this role)")
        v["company_h1b_approvals"] = rec(crow.get("Total Approvals") or None, f"{rel(paths['csv80'])}:{cline} Total Approvals")
        p75 = v["metro_p75"]["value"]
        if cm and p75 and cm > p75:
            out["flags"].append("company-h1b-median-above-metro-p75: senior/engineering-weighted; do not anchor on it")
    else:
        v["company_h1b_median_all_roles"] = rec(None, f"no exact row for '{posting.get('csv_name', '')}' in {rel(paths['csv80'])}")

    out["gates"]["G4_lca_prevailing_wage"] = "not-checked [TODO-1: OFLC wage level not in repo]"

    # Posted range vs floor (only for a live posting)
    if live == "not-live":
        out["decision"], out["reason"] = "Skip", "posting not live (Greenhouse API 404): no comparison"
        return out
    if rng is None:
        out["decision"], out["reason"] = "Floor only", "no posted range: use the floor as your ask"
    elif rng[0] < floor:
        out["decision"] = "Range starts below floor"
        out["reason"] = f"posted minimum ${rng[0]:,.0f} is ${floor - rng[0]:,.0f} under the floor ${floor:,.0f}; ask at or above the floor"
    else:
        out["decision"] = "Range clears floor"
        out["reason"] = f"posted minimum ${rng[0]:,.0f} ≥ floor ${floor:,.0f}"
    if live == "unchecked" and out["decision"] != "Floor only":
        out["flags"].append("liveness-unchecked: the comparison is provisional until the posting is confirmed live")
    return out


def executive_summary(profile, results):
    """Plain-language opening (SNICKERDOODLE P9): what this is, why read it, what it found."""
    n = len(results)
    by = {}
    for r in results:
        by.setdefault(r["decision"], []).append(r)
    real = sum(1 for r in results if not r["constructed"])
    found = []
    for label, text in (("Range clears floor", "the posted pay range starts at or above the floor"),
                        ("Range starts below floor", "the posted range starts below the floor, so ask for at least the floor"),
                        ("Floor only", "no pay range was posted; the floor is the number to ask for"),
                        ("Skip", "the posting is no longer live, so nothing was compared"),
                        ("Unresolved", "a person must decide something first (which occupation the job is, or the exact metro name)")):
        if by.get(label):
            found.append(f"{len(by[label])} where {text}")
    return ["## Executive summary", "",
            f"This report sets a **salary floor** for each of {n} data and business-intelligence job postings in the "
            f"{profile['metro'].split('-')[0]} area: the lowest pay that matches what the bottom quarter of people in that "
            "occupation already earn there, from public government wage data. Read it before you name a salary or accept "
            "an offer. It also shows why a company's average pay for its visa-sponsored staff is not a fair benchmark for one "
            "early-career role.", "",
            f"**Found:** {'; '.join(found)}. {n - real} of the {n} postings are made-up test cases and are marked as such. "
            "It cannot yet check the legal minimum wage for a visa-sponsored version of the job.", ""]


def report_md(profile, results, meta):
    lines = [f"# Data-role salary floor — {meta['run_date']}", ""] + executive_summary(profile, results) + [
             "## Run record", "",
             f"**For:** {profile.get('persona', '')}", "",
             f"**Metro:** {profile['metro']} · **Floor rule:** BLS metro nominal **{profile.get('floor_percentile', 25)}th percentile** "
             f"of the chosen SOC (your-input) · **SOC spread limit:** {profile.get('soc_spread_limit', 0.15):.0%}", "",
             "*Labels — record: read from a file or a saved API response · script-output: computed here or by the maintained script · "
             "your-input: a human choice · model-judgment: none in this run (no model was called).*", "",
             "| Posting | SOC (gate) | Floor | Metro median | Posted range | Company H-1B median (all roles) | Decision |",
             "|---|---|---|---|---|---|---|"]
    for r in results:
        v = r["values"]
        f = lambda k: (f"${v[k]['value']:,.0f}" if v.get(k) and isinstance(v[k]["value"], (int, float)) else "—")
        pr = v.get("posted_range", {}).get("value")
        name = f"{r['company']} — {r['title']}" + (" (CONSTRUCTED)" if r["constructed"] else "")
        lines.append(f"| {name} | {r['gates'].get('G1_soc', '—')} | {f('floor')} | {f('metro_median')} | "
                     f"{'$%s–$%s' % (f'{pr[0]:,.0f}', f'{pr[1]:,.0f}') if pr else '—'} | {f('company_h1b_median_all_roles')} | **{r['decision']}** |")
    lines += ["", "## Per posting: evidence and reasons", ""]
    for r in results:
        lines.append(f"### {r['company']} — {r['title']}" + (" (CONSTRUCTED test posting)" if r["constructed"] else ""))
        lines.append(f"- **Decision:** {r['decision']} — {r['reason']}")
        for g, s in r["gates"].items():
            lines.append(f"- Gate {g}: `{s}`")
        for k, val in r["values"].items():
            lines.append(f"- {k}: `{json.dumps(val['value'])}` **[{val['label']}]** — {val['source']}")
        for fl in r["flags"]:
            lines.append(f"- ⚠ {fl}")
        lines.append("")
    lines += ["## What this run cannot verify", "",
              "- The **legal H-1B floor**: the OFLC prevailing wage level for this SOC and area (G4 is always `not-checked`; TODO-1).",
              "- **Which SOC the employer's attorney will file** on the LCA. The SOC choice here is a human judgment.",
              "- **This** posting's level, bonus or equity. BLS percentiles are base wages for the whole occupation in the metro.",
              "- Any year after May 2024 (the OEWS reference period).",
              "- That the company's H-1B median describes this role. It covers all its H-1B roles, and is context only."]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="data-role salary floor (see module docstring)")
    ap.add_argument("--input", type=Path, default=HERE / "fixtures" / "worked-run" / "postings.json")
    ap.add_argument("--pay", type=Path, default=HERE / "fixtures" / "worked-run" / "pay-ranges.json")
    ap.add_argument("--out-dir", type=Path, default=REPO / "course" / "2026fa" / "submissions" / "kommurisi" / "data-role-salary-floor" / "runs" / "latest")
    ap.add_argument("--oews", type=Path, default=DATA / "metro_oews.csv")
    ap.add_argument("--rpp", type=Path, default=DATA / "bea_rpp.csv")
    ap.add_argument("--crosswalk", type=Path, default=DATA / "bls_bea_msa_crosswalk.csv")
    ap.add_argument("--national", type=Path, default=ONET)
    ap.add_argument("--onet", type=Path, default=ONET)
    ap.add_argument("--csv80", type=Path, default=CSV_80)
    a = ap.parse_args()
    for p in (a.input, a.oews, a.rpp, a.crosswalk, a.national, a.csv80, a.onet):
        if not Path(p).exists():
            sys.stderr.write(f"missing input: {p}\n  (metro inputs: run build_local_wage_inputs.py first)\n")
            return 2
    spec = json.loads(Path(a.input).read_text(encoding="utf-8"))
    pay = json.loads(Path(a.pay).read_text(encoding="utf-8")) if Path(a.pay).exists() else {}
    if "profile" not in spec or "postings" not in spec:
        sys.stderr.write("input must have 'profile' and 'postings'\n")
        return 2
    mw = load_maintained()
    tables = mw.load_tables(a.oews, a.rpp, a.crosswalk, a.national)
    paths = {"oews": a.oews, "rpp": a.rpp, "national": a.national, "onet": a.onet, "csv80": a.csv80,
             "pay": rel(a.pay)}
    results = [evaluate(p, spec["profile"], pay, mw, tables, paths) for p in spec["postings"]]
    meta = {"run_date": str(date.today()), "input": rel(a.input), "pay": rel(a.pay),
            "maintained_script": rel(MAINTAINED), "oews": rel(a.oews), "mode": "data-role-salary-floor v0.1.0"}
    a.out_dir.mkdir(parents=True, exist_ok=True)
    (a.out_dir / "salary-floor.log.json").write_text(json.dumps({"meta": meta, "profile": spec["profile"], "results": results},
                                                                indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (a.out_dir / "salary-floor.report.md").write_text(report_md(spec["profile"], results, meta), encoding="utf-8")
    counts = {}
    for r in results:
        counts[r["decision"]] = counts.get(r["decision"], 0) + 1
    print(f"{len(results)} postings → " + " · ".join(f"{k} {n}" for k, n in counts.items()))
    print(f"wrote {rel(a.out_dir / 'salary-floor.report.md')} and salary-floor.log.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
