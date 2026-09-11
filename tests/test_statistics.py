import unittest
from datetime import datetime, timezone
from collector.models import Quote
from collector.statistics import rank_daily, rank_daily_decliners, rank_five_minute, rank_five_minute_decliners, add_frequency, frequency_board


def quote(code, price, prev=10, amount=0, name=None):
    return Quote("SZ", code, name or code, price, prev, amount=amount, status="normal")


class StatisticsTests(unittest.TestCase):
  def test_daily_tie_uses_amount_then_key(self):
    rows = rank_daily([quote("000002", 11, amount=1), quote("000001", 11, amount=2)])
    self.assertEqual([r["code"] for r in rows], ["000001", "000002"])


  def test_decliners_only_negative(self):
    rows = rank_daily_decliners([quote("000001", 9), quote("000002", 10)])
    self.assertEqual([r["code"] for r in rows], ["000001"])


  def test_five_minute_needs_previous_price(self):
    rows = rank_five_minute([quote("000001", 11)], {"SZ:000001": 10})
    self.assertEqual(rows[0]["change_pct"], 10)
    self.assertEqual(rank_five_minute([quote("000001", 11)], {}), [])

  def test_five_minute_decliners_only_negative(self):
    rows = rank_five_minute_decliners([quote("000001", 9)], {"SZ:000001": 10})
    self.assertEqual(rows[0]["change_pct"], -10)


  def test_frequency_denominator_is_valid_slots(self):
    now = datetime(2026, 9, 11, 9, 40, tzinfo=timezone.utc)
    freq = {}
    add_frequency(freq, [{"key": "SZ:000001", "rank": 1}], now)
    rows = frequency_board(freq, {"SZ:000001": {"name": "A"}}, 2)
    self.assertEqual(rows[0]["count"], 1)
    self.assertEqual(rows[0]["frequency_pct"], 50)


if __name__ == "__main__":
  unittest.main()
