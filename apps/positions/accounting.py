"""Paper position accounting.

Average-cost method. Buys increase quantity and cost basis including fees.
Sells realise PnL against average cost. Candle extremes are never fills.
A recommendation is not a fill.
"""

from decimal import Decimal


def account(fills, mark_price):
    qty = Decimal("0")
    cost = Decimal("0")
    realised = Decimal("0")
    for fill in fills:
        if fill.get("failed"):
            continue
        px = Decimal(str(fill["price"]))
        q = Decimal(str(fill["quantity"]))
        fee = Decimal(str(fill.get("fee_usd") or 0))
        if fill["side"] == "buy":
            qty += q
            cost += px * q + fee
        else:
            if qty <= 0:
                continue
            avg = cost / qty
            sell_q = min(q, qty)
            realised += (px * sell_q - fee) - avg * sell_q
            cost -= avg * sell_q
            qty -= sell_q
    unrealised = Decimal("0")
    if qty > 0 and mark_price is not None:
        avg = cost / qty
        unrealised = (Decimal(str(mark_price)) - avg) * qty
    return {
        "quantity": qty,
        "cost_basis_usd": cost,
        "realised_usd": realised,
        "unrealised_usd": unrealised,
        "average_price": (cost / qty) if qty else None,
    }
