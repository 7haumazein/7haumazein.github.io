"""Build versioned report payloads from already collected snapshots.

This module is intentionally pure: collection, publication and any network
provider remain separate so a failed optional explanation cannot alter rankings.
"""
from datetime import datetime, timezone
from .statistics import rank_daily, rank_daily_decliners, rank_five_minute, rank_five_minute_decliners, add_frequency, frequency_board, sector_top


def _info(quotes):
    return {q.key: {"name": q.name, "code": q.code.zfill(6), "exchange": q.exchange,
                    "industry": q.industry, "province": q.province, "city": q.city,
                    "st": q.st, "status": q.status} for q in quotes}


def build_report(quotes, previous_prices=None, five_minute_slots=None, afternoon_slots=None, report_type="close",
                 coverage_pct=None, provider="unconfigured", quote_time=None, published_at=None):
    """Return a schema-versioned report. ``five_minute_slots`` is a sequence of
    ``(slot_time, quotes, previous_prices)`` tuples from one trading window.
    """
    previous_prices = previous_prices or {}
    slots = list(five_minute_slots or [])
    afternoon = list(afternoon_slots or [])
    stock_info = _info(quotes)
    frequency = {}
    valid_slots = 0
    for slot_time, slot_quotes, slot_previous in slots:
        board = rank_five_minute(slot_quotes, slot_previous or {})
        if board:
            valid_slots += 1
            add_frequency(frequency, board, slot_time)
    freq = frequency_board(frequency, stock_info, valid_slots)
    afternoon_frequency = {}
    afternoon_valid_slots = 0
    for slot_time, slot_quotes, slot_previous in afternoon:
        board = rank_five_minute(slot_quotes, slot_previous or {})
        if board:
            afternoon_valid_slots += 1
            add_frequency(afternoon_frequency, board, slot_time)
    freq_afternoon = frequency_board(afternoon_frequency, stock_info, afternoon_valid_slots)
    gainers = rank_daily(quotes)
    return {
        "schema_version": "0.1",
        "report_type": report_type,
        "provider": provider,
        "report_date": (quote_time or datetime.now(timezone.utc)).date().isoformat(),
        "quote_time": quote_time.isoformat() if quote_time else None,
        "published_at": published_at or datetime.now(timezone.utc).isoformat(),
        "statistics_window": "09:30-11:30" if report_type == "noon" else "09:30-15:00",
        "quality": {"coverage_pct": coverage_pct, "valid_five_minute_slots": valid_slots,
                     "status": "complete" if coverage_pct is not None and coverage_pct >= 98 else "partial"},
        "daily_gainers": gainers,
        "daily_decliners": rank_daily_decliners(quotes),
        "daily_sectors": sector_top(gainers),
        "frequency_all": freq,
        "frequency_afternoon": freq_afternoon,
        "frequency_sectors_all": sector_top(freq),
        "frequency_sectors_afternoon": sector_top(freq_afternoon),
        "sector_explanations": [],
        "analysis": {"enabled": False, "status": "disabled"},
    }


def build_latest(quotes, five_minute_previous=None, provider="unconfigured", quote_time=None,
                 coverage_pct=None):
    previous = five_minute_previous or {}
    gainers = rank_daily(quotes)
    return {
        "schema_version": "0.1", "provider": provider,
        "quote_time": quote_time.isoformat() if quote_time else None,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "published_at": datetime.now(timezone.utc).isoformat(),
        "coverage_pct": coverage_pct, "quality": "complete" if coverage_pct is not None and coverage_pct >= 98 else "partial",
        "status": "实时数据已更新" if quotes else "尚未连接实时数据源",
        "daily_gainers": gainers, "five_minute_gainers": rank_five_minute(quotes, previous),
        "five_minute_decliners": rank_five_minute_decliners(quotes, previous),
    }
