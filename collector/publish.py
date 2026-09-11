"""Atomic JSON publication for a static site or object storage sync job."""
import json
import os
from pathlib import Path


def write_json(path, payload):
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, destination)


def publish_report(root, report):
    root = Path(root)
    report_date = report["report_date"]
    report_type = report["report_type"]
    report_path = root / "reports" / report_date / f"{report_type}.json"
    write_json(report_path, report)
    index_path = root / "reports" / "index.json"
    index = {"schema_version": "0.1", "reports": []}
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding="utf-8"))
    entries = [x for x in index.get("reports", []) if not (x.get("date") == report_date and x.get("type") == report_type)]
    entries.append({"date": report_date, "type": report_type, "published_at": report.get("published_at")})
    index["reports"] = sorted(entries, key=lambda x: (x["date"], x["type"]), reverse=True)
    write_json(index_path, index)
    return report_path
