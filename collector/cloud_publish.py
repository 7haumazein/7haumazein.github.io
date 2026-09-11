"""Fetch a public A-share snapshot and build static daily-data files.

Designed for a short-lived GitHub Actions job. It has no credentials and never
touches trading APIs. The public endpoint is treated as best-effort input.
"""
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from .models import Quote
from .report import build_latest, build_report
from .publish import publish_report, write_json

URL = "https://push2.eastmoney.com/api/qt/clist/get?" + urllib.parse.urlencode({
    "pn": 1, "pz": 6000, "po": 1, "np": 1, "fltt": 2, "invt": 2,
    "fid": "f3", "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
    "fields": "f2,f3,f6,f12,f13,f14",
})


def fetch(timeout=20):
    req = urllib.request.Request(URL, headers={"User-Agent": "daily-report/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    rows = (payload.get("data") or {}).get("diff") or []
    quotes = []
    for row in rows:
        code = str(row.get("f12") or "").zfill(6)
        market = {1: "SZ", 0: "SH", 2: "BJ"}.get(row.get("f13"))
        if not market or len(code) != 6 or row.get("f2") in (None, "-"):
            continue
        try:
            price = float(row["f2"])
            change = float(row.get("f3")) if row.get("f3") not in (None, "-") else None
            prev = price / (1 + change / 100) if change is not None and change != -100 else None
        except (TypeError, ValueError, ZeroDivisionError):
            continue
        quotes.append(Quote(market, code, str(row.get("f14") or code), price, prev,
                            amount=float(row["f6"]) if row.get("f6") not in (None, "-") else None))
    return quotes


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "public/daily-data")
    now = datetime.now(timezone.utc)
    try:
        quotes = fetch()
        if not quotes:
            raise RuntimeError("public endpoint returned no A-share rows")
        latest = build_latest(quotes, provider="eastmoney-public", quote_time=now,
                              coverage_pct=min(100, round(len(quotes) / 5000 * 100, 2)))
        report_type = "close" if now.hour >= 7 else "noon"
        report = build_report(quotes, report_type=report_type, provider="eastmoney-public",
                              quote_time=now, coverage_pct=latest["coverage_pct"])
        write_json(root / "latest.json", latest)
        publish_report(root, report)
        print(json.dumps({"provider": "eastmoney-public", "quotes": len(quotes), "report": report_type}))
    except Exception as exc:
        latest = {"schema_version": "0.1", "provider": "eastmoney-public",
                  "status": "数据源暂时不可用", "quality": "stale",
                  "error": str(exc)[:200], "fetched_at": now.isoformat(),
                  "daily_gainers": [], "five_minute_gainers": [], "five_minute_decliners": []}
        write_json(root / "latest.json", latest)
        write_json(root / "reports/index.json", {"schema_version": "0.1", "reports": []})
        print(json.dumps(latest, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
