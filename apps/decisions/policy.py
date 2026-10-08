"""Deterministic decision policy v1.

Scores are interpretable point contributions, not probabilities.
LLM text cannot select the action. Unknown critical safety inputs fail closed.
Discovery alone cannot emit BUY SMALL NOW.
"""

POLICY_VERSION = "policy-v1.0"

ACTIONS_FLAT = {"NO BUY", "BUY SMALL NOW"}
ACTIONS_OPEN = {"ADD NOW", "HOLD", "TAKE PROFIT", "EXIT"}


def _gate(name, ok, detail):
    return {"name": name, "ok": ok, "detail": detail}


def evaluate(obs: dict) -> dict:
    positive, negative, gates, missing = [], [], [], []
    status = "LIVE"
    if obs.get("synthetic"):
        status = "PAPER MODE"
    if obs.get("source_outage"):
        status = "DEGRADED"
    if obs.get("quote_age_seconds") is None:
        missing.append("quote_age")
        status = "INSUFFICIENT DATA"
    elif obs["quote_age_seconds"] > obs.get("quote_max_age", 90):
        status = "STALE"

    mint_revoked = obs.get("mint_authority_revoked")
    freeze = obs.get("freeze_authority_active")
    top10 = obs.get("top10_holder_pct")
    liquidity = obs.get("liquidity_usd")
    impact = obs.get("price_impact_pct_1k")
    min_liq = obs.get("min_liquidity_usd", 8000)

    gates.append(_gate(
        "mint_authority",
        mint_revoked is True,
        "revoked" if mint_revoked is True else "unknown or active — does not pass",
    ))
    if mint_revoked is None:
        missing.append("mint_authority")
    gates.append(_gate(
        "freeze_authority",
        freeze is False,
        "inactive" if freeze is False else "unknown or active — does not pass",
    ))
    if freeze is None:
        missing.append("freeze_authority")
    if top10 is None:
        missing.append("holder_concentration")
        gates.append(_gate("holder_concentration", False, "unknown — does not pass"))
    else:
        gates.append(_gate("holder_concentration", top10 <= 0.45, f"top10={top10}"))
    if liquidity is None:
        missing.append("liquidity")
        gates.append(_gate("liquidity", False, "unknown"))
    else:
        gates.append(_gate("liquidity", liquidity >= min_liq, f"usd={liquidity}"))
    if impact is None:
        missing.append("price_impact")
        gates.append(_gate("price_impact", False, "unknown"))
    else:
        gates.append(_gate("price_impact", impact <= obs.get("max_impact", 3.0), f"impact={impact}"))
    identity = obs.get("resolution")
    gates.append(_gate(
        "identity",
        identity in {"CLEAR_LEADER", "PROVISIONAL_LEADER"},
        identity or "unresolved",
    ))
    if identity in {None, "NO_CANDIDATE", "UNRESOLVED", "CONTESTED"}:
        status = "IDENTITY UNRESOLVED" if status == "LIVE" or status == "PAPER MODE" else status

    safety_ok = all(g["ok"] for g in gates) and status not in {"STALE", "INSUFFICIENT DATA", "DEGRADED"}
    # PAPER MODE may still trade paper if gates pass; DEGRADED/STALE block fresh risk.
    fresh_ok = status not in {"STALE", "INSUFFICIENT DATA", "DEGRADED", "SOURCE UNAVAILABLE"}
    tradable = all(g["ok"] for g in gates) and fresh_ok

    buyers = obs.get("unique_buyers_5m") or 0
    ratio = obs.get("buy_sell_ratio_5m") or 0
    extension = obs.get("extension_from_first") or 1
    independent = obs.get("independent_sources") or 0
    narrative = obs.get("narrative_state")
    age_min = obs.get("age_minutes") or 0
    if buyers >= 25:
        positive.append(f"unique buyers 5m = {buyers}")
    else:
        negative.append(f"unique buyers 5m = {buyers} below 25")
    if ratio >= 1.4:
        positive.append(f"buy/sell ratio {ratio}")
    else:
        negative.append(f"buy/sell ratio {ratio} below 1.4")
    if independent >= 3:
        positive.append(f"{independent} independent sources")
    else:
        negative.append(f"only {independent} independent sources")
    if extension > 2.5:
        negative.append(f"entry extended {extension}x from first observation")
    if obs.get("creator_sold"):
        negative.append("creator-associated sell observed")

    opportunity = None
    early = (
        tradable
        and age_min <= 45
        and buyers >= 25
        and ratio >= 1.4
        and extension < 2.5
        and independent >= 3
        and narrative in {"ACCELERATING", "ESTABLISHED"}
        and identity == "CLEAR_LEADER"
        and not obs.get("creator_sold")
    )
    momentum = (
        tradable
        and age_min >= 20
        and 0.15 <= (obs.get("return_1h") or 0) <= 1.5
        and (obs.get("volume_acceleration") or 0) >= 1.5
        and independent >= 3
        and identity == "CLEAR_LEADER"
        and not obs.get("creator_sold")
    )
    if early:
        opportunity = "EARLY_RUNNER"
    elif momentum:
        opportunity = "MOMENTUM_CONTINUATION"

    position = obs.get("position")
    action = "NO BUY"
    why = "Discovery or evidence does not clear entry rules."
    invalidation = "A later safety failure, leader change, or liquidity drop invalidates a watch."
    if not position:
        if early or momentum:
            action = "BUY SMALL NOW"
            why = f"{opportunity} rules cleared on policy {POLICY_VERSION}."
            invalidation = "Exit paper plan if liquidity falls 40% from entry, creator sells, or identity flips."
        elif identity in {None, "UNRESOLVED", "CONTESTED", "NO_CANDIDATE"}:
            why = "Contract identity is not a leader. No buy."
            if status in {"LIVE", "PAPER MODE"}:
                status = "IDENTITY UNRESOLVED"
    else:
        pnl = obs.get("unrealised_pct") or 0
        liq_drop = obs.get("liquidity_drop_from_entry") or 0
        if not tradable or obs.get("creator_sold") or liq_drop >= 0.40:
            action = "EXIT"
            why = "Safety, identity, freshness, creator sell, or liquidity deterioration."
            invalidation = "N/A — exit is the invalidation response."
            status = status if status != "PAPER MODE" else "PAPER MODE"
        elif pnl >= 0.40 and (obs.get("volume_acceleration") or 1) < 1.0:
            action = "TAKE PROFIT"
            why = "Unrealised gain at least 40% with fading volume. Partial take-profit rule."
            invalidation = "Reassess remainder if liquidity breaks."
        elif tradable and early and (obs.get("adds_used") or 0) < obs.get("max_adds", 1) and 0.08 <= (obs.get("pullback") or 0) <= 0.20:
            action = "ADD NOW"
            why = "Pullback inside 8-20% with entry rules still true."
        else:
            action = "HOLD"
            why = "Open paper position. No add, take-profit, or exit trigger."
            if status in {"STALE", "DEGRADED", "INSUFFICIENT DATA"}:
                why = "Open position during degraded data. Monitoring uncertainty — not a confident hold thesis."

    return {
        "action": action,
        "operational_status": status,
        "opportunity_type": opportunity or "",
        "policy_version": POLICY_VERSION,
        "why_now": why,
        "main_risks": "; ".join(negative) or "No rule failure recorded. This is not a safety certification.",
        "invalidation": invalidation,
        "positive": positive,
        "negative": negative,
        "hard_gates": gates,
        "missing": missing,
        "tradable": tradable,
        "safety_ok": safety_ok,
    }
