"""SQLite persistence for raw snapshots and immutable report payloads."""
import json
import sqlite3
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS snapshots (
  slot TEXT NOT NULL, fetched_at TEXT NOT NULL, provider TEXT NOT NULL,
  quality TEXT NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(slot, provider)
);
CREATE TABLE IF NOT EXISTS reports (
  report_date TEXT NOT NULL, report_type TEXT NOT NULL, version INTEGER NOT NULL,
  payload TEXT NOT NULL, created_at TEXT NOT NULL,
  PRIMARY KEY(report_date, report_type, version)
);
"""


class Store:
    def __init__(self, path="data/daily.sqlite3"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.executescript(SCHEMA)
        self.connection.commit()

    def save_snapshot(self, slot, fetched_at, provider, quotes, quality="complete"):
        payload = json.dumps([q.as_dict() for q in quotes], ensure_ascii=False)
        self.connection.execute("INSERT OR REPLACE INTO snapshots VALUES (?, ?, ?, ?, ?)",
                               (slot, fetched_at, provider, quality, payload))
        self.connection.commit()

    def save_report(self, report_date, report_type, version, payload, created_at):
        self.connection.execute("INSERT OR REPLACE INTO reports VALUES (?, ?, ?, ?, ?)",
                               (report_date, report_type, version, json.dumps(payload, ensure_ascii=False), created_at))
        self.connection.commit()

    def close(self):
        self.connection.close()
