#!/usr/bin/env python3
"""The mode's only network step: capture each posting's Greenhouse API status and posted pay range.

For every posting in postings.json that names {"greenhouse": {"board", "job_id"}}, GET
https://boards-api.greenhouse.io/v1/boards/<board>/jobs/<job_id>?pay_transparency=true
and save status (200 = live, 404 = gone), title, location, updated_at and pay_input_ranges.
Only that host is ever contacted. salary_floor.py then runs offline on the saved file.

    python3 fetch_pay_ranges.py --input fixtures/worked-run/postings.json --out fixtures/worked-run/pay-ranges.json
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

HOST = "boards-api.greenhouse.io"
HERE = Path(__file__).resolve().parent


def build_url(board: str, job_id: str) -> str:
    """The only URL this mode may fetch. Board and job id must be plain tokens, so nothing can redirect the host."""
    if not re.fullmatch(r"[A-Za-z0-9_-]+", str(board)) or not re.fullmatch(r"[0-9]+", str(job_id)):
        raise ValueError(f"refusing board/job id that is not a plain token: {board!r}/{job_id!r}")
    url = f"https://{HOST}/v1/boards/{board}/jobs/{job_id}?pay_transparency=true"
    if urlparse(url).hostname != HOST:   # the permission boundary, stated in code
        raise ValueError(f"refusing non-Greenhouse host: {url}")
    return url


def fetch(board: str, job_id: str, timeout: float = 20.0) -> dict:
    url = build_url(board, job_id)
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            d = json.load(r)
            return {"url": url, "status": r.status, "title": d.get("title"),
                    "location": (d.get("location") or {}).get("name"), "updated_at": d.get("updated_at"),
                    "pay_input_ranges": d.get("pay_input_ranges") or [], "error": None}
    except urllib.error.HTTPError as e:
        return {"url": url, "status": e.code, "title": None, "location": None, "updated_at": None,
                "pay_input_ranges": [], "error": None}
    except (urllib.error.URLError, TimeoutError) as e:
        return {"url": url, "status": None, "title": None, "location": None, "updated_at": None,
                "pay_input_ranges": [], "error": f"{type(e).__name__}: {e}"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--input", type=Path, default=HERE / "fixtures" / "worked-run" / "postings.json")
    ap.add_argument("--out", type=Path, default=HERE / "fixtures" / "worked-run" / "pay-ranges.json")
    a = ap.parse_args()
    spec = json.loads(a.input.read_text(encoding="utf-8"))
    jobs = {}
    for p in spec["postings"]:
        gh = p.get("greenhouse")
        if gh:
            jobs[f"{gh['board']}/{gh['job_id']}"] = fetch(gh["board"], str(gh["job_id"]))
    out = {"host": f"https://{HOST}", "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "jobs": jobs}
    a.out.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    for k, j in jobs.items():
        pr = j["pay_input_ranges"][0] if j["pay_input_ranges"] else None
        rng = f"${pr['min_cents'] // 100:,}-${pr['max_cents'] // 100:,}" if pr else "no range"
        print(f"{j['status']}  {k}  {j['title'] or ''}  {rng}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
