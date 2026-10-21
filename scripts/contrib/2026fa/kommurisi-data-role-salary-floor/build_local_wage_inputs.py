#!/usr/bin/env python3
"""Rebuild the three inputs that scripts/bls/local-wage-adjustment.py reads, from the official files.

Why: the maintained recipe says its inputs (data/bls/local-wage/metro_oews.csv, bea_rpp.csv,
bls_bea_msa_crosswalk.csv) are committed, but `git ls-files data/bls/local-wage` is empty on main
at 015843d. This script rebuilds them from the two public sources, without editing any value:

  BLS  OEWS May 2024 metropolitan and nonmetropolitan areas   oesm24ma.zip -> MSA_M2024_dl.xlsx
       https://www.bls.gov/oes/special-requests/oesm24ma.zip  (BLS refuses scripted downloads; save it from
       https://www.bls.gov/oes/tables.htm in a browser)
  BEA  Regional Price Parities by MSA, 2008-2024             MARPP.zip -> MARPP_MSA_2008_2024.csv
       https://apps.bea.gov/regional/zip/MARPP.zip

Outputs (untracked; default ./.data/ beside this script):
  metro_oews.csv            the BLS sheet's own columns, unchanged values (wages stay strings: '*', '#' kept)
  bea_rpp.csv               GeoFIPS, GeoName, rpp_all_items_2024  (LineCode 1 = "RPPs: All items")
  bls_bea_msa_crosswalk.csv AREA, GeoFIPS where the BLS AREA code equals the BEA GeoFIPS exactly
  manifest.json             SHA-256 of both sources, row counts, the crosswalk size

    .venv/Scripts/python.exe build_local_wage_inputs.py --bls <MSA_M2024_dl.xlsx> --bea <MARPP_MSA_2008_2024.csv>
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
OEWS_COLS = ["AREA", "AREA_TITLE", "AREA_TYPE", "PRIM_STATE", "OCC_CODE", "OCC_TITLE", "O_GROUP", "TOT_EMP",
             "A_MEAN", "A_PCT10", "A_PCT25", "A_MEDIAN", "A_PCT75", "A_PCT90"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def five(code: object) -> str:
    digits = "".join(ch for ch in str(code) if ch.isdigit())
    return digits.zfill(5) if 0 < len(digits) <= 5 else str(code).strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--bls", type=Path, required=True, help="MSA_M2024_dl.xlsx from oesm24ma.zip")
    ap.add_argument("--bea", type=Path, required=True, help="MARPP_MSA_2008_2024.csv from MARPP.zip")
    ap.add_argument("--out", type=Path, default=HERE / ".data")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)

    oews = pd.read_excel(a.bls, sheet_name=0, dtype=str, usecols=OEWS_COLS, engine="openpyxl")
    oews["AREA"] = oews["AREA"].map(five)
    oews.to_csv(a.out / "metro_oews.csv", index=False)

    bea = pd.read_csv(a.bea, dtype=str, skipinitialspace=True)
    bea = bea[bea["LineCode"].str.strip() == "1"].copy()
    bea["GeoFIPS"] = bea["GeoFIPS"].map(five)
    rpp = bea[["GeoFIPS", "GeoName", "2024"]].rename(columns={"2024": "rpp_all_items_2024"})
    rpp.to_csv(a.out / "bea_rpp.csv", index=False)

    areas = set(oews["AREA"])
    xwalk = pd.DataFrame(sorted(areas & set(rpp["GeoFIPS"])), columns=["AREA"])
    xwalk["GeoFIPS"] = xwalk["AREA"]
    xwalk.to_csv(a.out / "bls_bea_msa_crosswalk.csv", index=False)

    manifest = {
        "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sources": {
            "bls": {"file": a.bls.name, "sha256": sha256(a.bls), "url": "https://www.bls.gov/oes/special-requests/oesm24ma.zip"},
            "bea": {"file": a.bea.name, "sha256": sha256(a.bea), "url": "https://apps.bea.gov/regional/zip/MARPP.zip"},
        },
        "rows": {"metro_oews": len(oews), "metro_oews_areas": len(areas),
                 "metro_oews_detailed": int((oews["O_GROUP"] == "detailed").sum()),
                 "bea_rpp_all_items": len(rpp), "crosswalk_exact_matches": len(xwalk)},
    }
    (a.out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["rows"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
