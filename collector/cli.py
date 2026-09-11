"""Command-line entry points for local validation and report assembly."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from .provider import FileQuoteProvider
from .statistics import rank_daily, rank_daily_decliners


def probe(path):
    started = datetime.now(timezone.utc)
    provider = FileQuoteProvider(path)
    quotes = provider.snapshot()
    payload = {
        "schema_version": "0.1",
        "provider": provider.name,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_ms": int((datetime.now(timezone.utc) - started).total_seconds() * 1000),
        "coverage": len(quotes),
        "fields": sorted(quotes[0].as_dict().keys()) if quotes else [],
        "daily_gainers": rank_daily(quotes),
        "daily_decliners": rank_daily_decliners(quotes),
        "status": "file-export-only; not a verified live source"
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="A-share daily report collector")
    parser.add_argument("command", choices=["probe"])
    parser.add_argument("path", help="JSON/CSV quote export")
    args = parser.parse_args()
    if args.command == "probe":
        probe(args.path)


if __name__ == "__main__":
    main()
