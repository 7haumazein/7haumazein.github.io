"""Deterministic ranking and five-minute frequency calculations."""
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timedelta
from typing import Iterable, Mapping, Sequence


def _change(price, base):
    if price is None or base in (None, 0):
        return None
    return (price / base - 1) * 100


def rank_daily(quotes: Iterable, limit: int = 30):
    rows = []
    for q in quotes:
        change = _change(q.price, q.prev_close)
        if change is None or change <= 0 or q.status != "normal":
            continue
        rows.append({"key": q.key, "exchange": q.exchange, "code": q.code.zfill(6),
                     "name": q.name, "industry": q.industry, "province": q.province,
                     "city": q.city, "change_pct": round(change, 4),
                     "amount": q.amount or 0, "st": q.st, "status": q.status})
    rows.sort(key=lambda x: (-x["change_pct"], -x["amount"], x["key"]))
    for index, row in enumerate(rows[:limit], 1):
        row["rank"] = index
    return rows[:limit]


def rank_daily_decliners(quotes: Iterable, limit: int = 30):
    rows = []
    for q in quotes:
        change = _change(q.price, q.prev_close)
        if change is None or change >= 0 or q.status != "normal":
            continue
        rows.append({"key": q.key, "exchange": q.exchange, "code": q.code.zfill(6),
                     "name": q.name, "industry": q.industry, "province": q.province,
                     "city": q.city, "change_pct": round(change, 4),
                     "amount": q.amount or 0, "st": q.st, "status": q.status})
    rows.sort(key=lambda x: (x["change_pct"], -x["amount"], x["key"]))
    for index, row in enumerate(rows[:limit], 1):
        row["rank"] = index
    return rows[:limit]


def five_minute_change(current, previous):
    return _change(current, previous)


def rank_five_minute(quotes: Iterable, previous_prices: Mapping[str, float], limit: int = 30):
    rows = []
    for q in quotes:
        change = five_minute_change(q.price, previous_prices.get(q.key))
        if change is None or change <= 0 or q.status != "normal":
            continue
        rows.append({"key": q.key, "exchange": q.exchange, "code": q.code.zfill(6),
                     "name": q.name, "industry": q.industry, "province": q.province,
                     "city": q.city, "change_pct": round(change, 4),
                     "amount": q.amount or 0, "st": q.st, "status": q.status})
    rows.sort(key=lambda x: (-x["change_pct"], -x["amount"], x["key"]))
    for index, row in enumerate(rows[:limit], 1):
        row["rank"] = index
    return rows[:limit]


def rank_five_minute_decliners(quotes: Iterable, previous_prices: Mapping[str, float], limit: int = 30):
    rows = []
    for q in quotes:
        change = five_minute_change(q.price, previous_prices.get(q.key))
        if change is None or change >= 0 or q.status != "normal":
            continue
        rows.append({"key": q.key, "exchange": q.exchange, "code": q.code.zfill(6),
                     "name": q.name, "industry": q.industry, "province": q.province,
                     "city": q.city, "change_pct": round(change, 4),
                     "amount": q.amount or 0, "st": q.st, "status": q.status})
    rows.sort(key=lambda x: (x["change_pct"], -x["amount"], x["key"]))
    for index, row in enumerate(rows[:limit], 1):
        row["rank"] = index
    return rows[:limit]


def add_frequency(frequency, board: Sequence[dict], slot_time: datetime):
    """Count one valid slot. Caller is responsible for slot de-duplication."""
    for row in board:
        item = frequency.setdefault(row["key"], {"count": 0, "rank_points": 0,
                                                  "first_seen": slot_time.isoformat(),
                                                  "last_seen": slot_time.isoformat(),
                                                  "rank_sum": 0})
        item["count"] += 1
        item["rank_points"] += (31 - row["rank"]) / 30
        item["rank_sum"] += row["rank"]
        item["last_seen"] = slot_time.isoformat()


def frequency_board(frequency: Mapping[str, dict], stock_info: Mapping[str, dict], valid_slots: int,
                    limit: int = 30):
    rows = []
    for key, item in frequency.items():
        info = stock_info.get(key, {"name": key, "industry": None, "province": None, "city": None})
        rows.append({"key": key, **info, **item,
                     "frequency_pct": round(item["count"] / valid_slots * 100, 2) if valid_slots else None,
                     "average_rank": round(item["rank_sum"] / item["count"], 2) if item["count"] else None})
    rows.sort(key=lambda x: (-x["count"], -x["rank_points"], x["key"]))
    for index, row in enumerate(rows[:limit], 1):
        row["rank"] = index
    return rows[:limit]


def sector_top(rows: Sequence[dict], limit: int = 3):
    grouped = defaultdict(lambda: {"count": 0, "rank_points": 0, "keys": []})
    for row in rows:
        industry = row.get("industry") or "待补充"
        grouped[industry]["count"] += 1
        grouped[industry]["rank_points"] += (31 - row.get("rank", 30)) / 30
        grouped[industry]["keys"].append(row["key"])
    result = [{"industry": name, **values} for name, values in grouped.items() if name != "待补充"]
    result.sort(key=lambda x: (-x["count"], -x["rank_points"], x["industry"]))
    return result[:limit]
