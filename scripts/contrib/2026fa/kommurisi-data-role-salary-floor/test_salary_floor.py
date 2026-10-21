#!/usr/bin/env python3
"""Offline tests for data-role-salary-floor. Fixtures only (fixtures/test/), no network.

They drive the real CLI (salary_floor.py), which imports the maintained
scripts/bls/local-wage-adjustment.py for the metro gates. Nothing here re-implements those gates.

    .venv/Scripts/python.exe -m unittest scripts/contrib/2026fa/kommurisi-data-role-salary-floor/test_salary_floor.py -v
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
FX = HERE / "fixtures" / "test"
SCRIPT = Path(os.environ.get("SALARY_FLOOR_SCRIPT", HERE / "salary_floor.py"))   # mutation_test.py swaps in mutants
sys.path.insert(0, str(HERE))
import fetch_pay_ranges  # noqa: E402

PROFILE = {"persona": "test", "metro": "Testville, ZZ", "floor_percentile": 25, "soc_spread_limit": 0.15}


def run(postings, profile=None, expect_exit=0):
    with tempfile.TemporaryDirectory() as d:
        inp = Path(d) / "postings.json"
        inp.write_text(json.dumps({"profile": profile or PROFILE, "postings": postings}), encoding="utf-8")
        cmd = [sys.executable, str(SCRIPT), "--input", str(inp), "--pay", str(FX / "pay.json"),
               "--out-dir", d, "--oews", str(FX / "mini_oews.csv"), "--rpp", str(FX / "mini_rpp.csv"),
               "--crosswalk", str(FX / "mini_xwalk.csv"), "--national", str(FX / "mini_onet.csv"),
               "--onet", str(FX / "mini_onet.csv"), "--csv80", str(FX / "mini_80days.csv")]
        p = subprocess.run(cmd, capture_output=True, text=True)
        if p.returncode != expect_exit:
            raise AssertionError(f"exit {p.returncode} != {expect_exit}\n{p.stdout}\n{p.stderr}")
        if expect_exit != 0:
            return None
        log = json.loads((Path(d) / "salary-floor.log.json").read_text(encoding="utf-8"))
        report = (Path(d) / "salary-floor.report.md").read_text(encoding="utf-8")
        return log["results"], report


def P(**kw):
    base = {"id": "t", "company": "Test", "csv_name": "SMALLCO INC", "title": "Data Analyst"}
    base.update(kw)
    return base


class SalaryFloor(unittest.TestCase):
    def test_ambiguous_soc_without_choice_refuses(self):
        (r,), _ = run([P(title="Data Analyst", posted_range=[90000, 110000])])
        self.assertEqual(r["decision"], "Unresolved")
        self.assertIn("ambiguous-soc", r["reason"])
        self.assertNotIn("floor", r["values"])            # no floor emitted when the SOC is ambiguous

    def test_close_candidates_take_the_lowest_floor(self):
        (r,), _ = run([P(title="Close Analyst", posted_range=[96000, 120000])])   # 15-2041 p25 95k vs 15-2051 100k
        self.assertEqual(r["gates"]["G1_soc"], "ok: 15-2041")
        self.assertEqual(r["values"]["floor"]["value"], 95000.0)

    def test_floor_is_the_bls_p25_of_the_chosen_soc(self):
        (r,), _ = run([P(soc_choice="15-2051", posted_range=[100000, 120000])])
        f = r["values"]["floor"]
        self.assertEqual(f["value"], 100000.0)
        self.assertEqual(f["label"], "record")
        self.assertIn("mini_oews.csv:3 A_PCT25", f["source"])   # file line of the 15-2051 row
        self.assertTrue(r["values"]["crosscheck_p25"]["value"])  # maintained adjusted_low x RPP/100 == nominal p25

    def test_equal_to_floor_clears_and_below_floor_is_flagged(self):
        res, _ = run([P(id="eq", soc_choice="15-2051", greenhouse={"board": "testboard", "job_id": "222"}),
                      P(id="lo", soc_choice="15-2051", greenhouse={"board": "testboard", "job_id": "111"})])
        self.assertEqual(res[0]["decision"], "Range clears floor")
        self.assertEqual(res[1]["decision"], "Range starts below floor")
        self.assertIn("$10,000 under", res[1]["reason"])

    def test_suppressed_median_refuses(self):
        (r,), _ = run([P(title="Developer", soc_choice="15-1252")])
        self.assertEqual(r["decision"], "Unresolved")
        self.assertIn("suppressed-small-sample", r["reason"])
        self.assertNotIn("floor", r["values"])

    def test_no_metro_match_never_falls_back_to_national(self):
        (r,), _ = run([P(soc_choice="15-2051", metro="Testville")])   # not the exact BLS title
        self.assertEqual(r["decision"], "Unresolved")
        self.assertIn("no-metro-match", r["reason"])
        self.assertNotIn("floor", r["values"])
        self.assertNotIn("national_median", r["values"])

    def test_top_coded_percentile_refuses(self):
        (r,), _ = run([P(title="Topcoded Tester", soc_choice="15-9999")])
        self.assertEqual(r["decision"], "Unresolved")
        # the maintained gate fires first ('#' median) or ours does ('#' p25): either way, no floor
        self.assertNotIn("floor", r["values"])

    def test_company_h1b_median_is_context_never_the_floor(self):
        (r,), _ = run([P(csv_name="BIGCO INC", soc_choice="15-2051", posted_range=[150000, 200000])])
        self.assertEqual(r["values"]["floor"]["value"], 100000.0)
        self.assertEqual(r["values"]["company_h1b_median_all_roles"]["value"], 200000.0)
        self.assertIn("not this role", r["values"]["company_h1b_median_all_roles"]["source"])
        self.assertTrue(any(f.startswith("company-h1b-median-above-metro-p75") for f in r["flags"]))

    def test_dead_posting_is_skipped_without_comparison(self):
        (r,), _ = run([P(soc_choice="15-2051", greenhouse={"board": "testboard", "job_id": "333"})])
        self.assertEqual(r["gates"]["G3_liveness"], "not-live")
        self.assertEqual(r["decision"], "Skip")

    def test_lca_wage_gate_is_never_claimed(self):
        (r,), report = run([P(soc_choice="15-2051", posted_range=[100000, 120000])])
        self.assertTrue(r["gates"]["G4_lca_prevailing_wage"].startswith("not-checked"))
        self.assertTrue(report.startswith("# Data-role salary floor"))
        self.assertIn("## Executive summary", report.split("## Run record")[0])

    def test_bad_input_exits_2(self):
        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / "bad.json"
            bad.write_text(json.dumps({"postings": []}), encoding="utf-8")
            p = subprocess.run([sys.executable, str(SCRIPT), "--input", str(bad), "--out-dir", d,
                                "--oews", str(FX / "mini_oews.csv"), "--rpp", str(FX / "mini_rpp.csv"),
                                "--crosswalk", str(FX / "mini_xwalk.csv"), "--national", str(FX / "mini_onet.csv"),
                                "--onet", str(FX / "mini_onet.csv"), "--csv80", str(FX / "mini_80days.csv")],
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 2)

    def test_missing_data_file_exits_2(self):
        with tempfile.TemporaryDirectory() as d:
            p = subprocess.run([sys.executable, str(SCRIPT), "--oews", str(Path(d) / "nope.csv"),
                                "--out-dir", d], capture_output=True, text=True)
            self.assertEqual(p.returncode, 2)
            self.assertIn("missing input", p.stderr)


class NetworkBoundary(unittest.TestCase):
    def test_only_greenhouse_urls_are_built(self):
        self.assertEqual(fetch_pay_ranges.build_url("klaviyo", "7737707003"),
                         "https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs/7737707003?pay_transparency=true")
        for board, job in [("evil.com", "1"), ("x@evil", "1"), ("../../x", "1"), ("klaviyo", "1?x=@evil"),
                           ("klaviyo/jobs/1#", "2"), ("", "1")]:
            with self.assertRaises(ValueError):
                fetch_pay_ranges.build_url(board, job)


if __name__ == "__main__":
    unittest.main()
