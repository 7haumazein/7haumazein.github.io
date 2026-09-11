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
from .statistics import frequency_board

URL = "https://push2.eastmoney.com/api/qt/clist/get?" + urllib.parse.urlencode({
    "pn": 1, "pz": 6000, "po": 1, "np": 1, "fltt": 2, "invt": 2,
    "fid": "f3", "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
    "fields": "f2,f3,f6,f8,f12,f13,f14,f100,f102,f103",
})


def fetch(timeout=20):
    req = urllib.request.Request(URL, headers={"User-Agent": "daily-report/1.0"})
    last_error = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
            break
        except Exception as exc:
            last_error = exc
            if attempt == 2:
                raise last_error
    rows = (payload.get("data") or {}).get("diff") or []
    quotes = []
    for row in rows:
        code = str(row.get("f12") or "").zfill(6)
        market = {1: "SH", 0: "SZ", 2: "BJ"}.get(row.get("f13"))
        if not market or len(code) != 6 or row.get("f2") in (None, "-"):
            continue
        try:
            price = float(row["f2"])
            change = float(row.get("f3")) if row.get("f3") not in (None, "-") else None
            prev = price / (1 + change / 100) if change is not None and change != -100 else None
        except (TypeError, ValueError, ZeroDivisionError):
            continue
        def number(field):
            try:
                return float(row[field]) if row.get(field) not in (None, "-") else None
            except (TypeError, ValueError):
                return None
        quotes.append(Quote(market, code, str(row.get("f14") or code), price, prev,
                            amount=number("f6"), turnover_rate=number("f8"),
                            industry=row.get("f100") or None, province=row.get("f102") or None,
                            city=row.get("f103") or None))
    return quotes


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "public/daily-data")
    now = datetime.now(timezone.utc)
    try:
        quotes = fetch()
        if not quotes:
            raise RuntimeError("public endpoint returned no A-share rows")
        previous = {}
        history_url = "https://7haumazein.github.io/daily-data/latest.json"
        try:
            with urllib.request.urlopen(history_url, timeout=5) as response:
                previous = json.loads(response.read().decode("utf-8"))
        except Exception:
            previous = {}
        prior_prices = {row.get("key"): row.get("price") for row in previous.get("quotes", []) if row.get("key")}
        slots = list(previous.get("frequency_slots", []))[-78:]
        latest = build_latest(quotes, five_minute_previous=prior_prices, provider="eastmoney-public", quote_time=now,
                              coverage_pct=min(100, round(len(quotes) / 5000 * 100, 2)))
        counts = dict(previous.get("frequency_counts", {})) if previous.get("frequency_date") == now.date().isoformat() else {}
        for row in latest["five_minute_gainers"]:
            counts[row["key"]] = counts.get(row["key"], 0) + 1
        info = {q.key: {"name": q.name, "code": q.code, "exchange": q.exchange,
                        "industry": q.industry, "province": q.province, "city": q.city}
                for q in quotes}
        latest["frequency_counts"] = counts
        latest["frequency_date"] = now.date().isoformat()
        latest["frequency_board"] = frequency_board(
            {key: {"count": value, "rank_points": 0, "rank_sum": 0}
             for key, value in counts.items()}, info, max(1, len(slots) + 1))
        latest["quotes"] = [{"key": q.key, "price": q.price} for q in quotes]
        latest["frequency_slots"] = slots + [{"time": now.isoformat(), "keys": [x["key"] for x in latest["five_minute_gainers"]]}]
        report_type = "close" if now.hour >= 7 else "noon"
        report = build_report(quotes, report_type=report_type, provider="eastmoney-public",
                              quote_time=now, coverage_pct=latest["coverage_pct"])
        report["frequency_all"] = latest["frequency_board"]
        write_json(root / "latest.json", latest)
        publish_report(root, report)
        print(json.dumps({"provider": "eastmoney-public", "quotes": len(quotes), "report": report_type}))
    except Exception as exc:
        latest = {"schema_version": "0.1", "provider": "eastmoney-public",
                  "status": "数据源暂时不可用", "quality": "stale",
                  "error": str(exc)[:200], "fetched_at": now.isoformat(),
                  "daily_gainers": [], "five_minute_gainers": []}
        write_json(root / "latest.json", latest)
        write_json(root / "reports/index.json", {"schema_version": "0.1", "reports": []})
        print(json.dumps(latest, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
