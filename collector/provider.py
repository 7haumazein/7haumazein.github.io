"""Provider boundary. A JSON/CSV adapter is useful for local verification; no fake quotes are generated."""
import csv
import json
from datetime import datetime
from pathlib import Path
from .models import Quote


class ProviderError(RuntimeError):
    pass


class QuoteProvider:
    name = "unconfigured"

    def snapshot(self):
        raise ProviderError("No verified market-data provider is configured")


class FileQuoteProvider(QuoteProvider):
    """Read a user-exported JSON or CSV snapshot for parser and algorithm checks."""
    name = "file-export"

    def __init__(self, path):
        self.path = Path(path)

    def snapshot(self):
        if not self.path.exists():
            raise ProviderError(f"Snapshot does not exist: {self.path}")
        if self.path.suffix.lower() == ".json":
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            rows = payload.get("quotes", payload) if isinstance(payload, dict) else payload
        else:
            with self.path.open(encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.DictReader(stream))
        result = []
        for row in rows:
            when = row.get("quote_time")
            result.append(Quote(exchange=row.get("exchange", "SZ"), code=str(row["code"]),
                name=row.get("name", ""), price=float(row["price"]) if row.get("price") not in (None, "") else None,
                prev_close=float(row["prev_close"]) if row.get("prev_close") not in (None, "") else None,
                amount=float(row["amount"]) if row.get("amount") not in (None, "") else None,
                quote_time=datetime.fromisoformat(when) if when else None,
                industry=row.get("industry") or None, province=row.get("province") or None,
                city=row.get("city") or None, status=row.get("status", "normal"),
                st=str(row.get("st", "false")).lower() in ("1", "true", "yes")))
        return result
