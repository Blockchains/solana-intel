"""One-minute candle construction from trade observations.

Bucket boundaries are UTC minute starts: [T, T+60s).
Price is the trade's USD price. OHLC uses trade order within the bucket.
Volume is sum of size_usd. Unique buyers/sellers are sets of wallet ids.
Empty intervals are stored only when explicitly requested and are marked empty.
They never invent a trade. Late trades with available_at after the build
cutoff are excluded; a later rebuild can correct a provisional candle.
Vendor candles must be stored with origin=vendor and are never mixed in.
"""

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal


def floor_minute(ts: datetime) -> datetime:
    ts = ts.astimezone(timezone.utc)
    return ts.replace(second=0, microsecond=0)


def build_candles(trades, start, end, fill_empty=False):
    buckets = defaultdict(list)
    for trade in trades:
        if trade["available_at"] > end:
            continue
        if not (start <= trade["event_time"] < end):
            continue
        buckets[floor_minute(trade["event_time"])].append(trade)

    candles = []
    cursor = floor_minute(start)
    last = floor_minute(end - timedelta(seconds=1))
    while cursor <= last:
        rows = sorted(buckets.get(cursor, []), key=lambda t: (t["event_time"], t.get("log_index", 0)))
        if not rows:
            if fill_empty:
                candles.append({
                    "bucket_start": cursor,
                    "empty": True,
                    "provisional": cursor + timedelta(minutes=1) > end,
                    "open": None,
                    "high": None,
                    "low": None,
                    "close": None,
                    "volume_usd": Decimal("0"),
                    "buy_count": 0,
                    "sell_count": 0,
                    "unique_buyers": 0,
                    "unique_sellers": 0,
                })
        else:
            prices = [Decimal(str(r["price_usd"])) for r in rows]
            buyers = {r["wallet"] for r in rows if r["side"] == "buy"}
            sellers = {r["wallet"] for r in rows if r["side"] == "sell"}
            candles.append({
                "bucket_start": cursor,
                "empty": False,
                "provisional": cursor + timedelta(minutes=1) > end,
                "open": prices[0],
                "high": max(prices),
                "low": min(prices),
                "close": prices[-1],
                "volume_usd": sum(Decimal(str(r["size_usd"])) for r in rows),
                "buy_count": sum(1 for r in rows if r["side"] == "buy"),
                "sell_count": sum(1 for r in rows if r["side"] == "sell"),
                "unique_buyers": len(buyers),
                "unique_sellers": len(sellers),
            })
        cursor += timedelta(minutes=1)
    return candles
