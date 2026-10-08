"""Thesis-to-token resolution. First-created is not assumed canonical."""


def resolve_candidates(candidates):
    """candidates: list of dicts with mint, score, explicit_contract, created_at."""
    if not candidates:
        return {"state": "NO_CANDIDATE", "leader": None, "margin": None, "ranked": []}
    ranked = sorted(candidates, key=lambda c: c["score"], reverse=True)
    leader = ranked[0]
    second = ranked[1]["score"] if len(ranked) > 1 else 0.0
    margin = round(leader["score"] - second, 4)
    if leader["score"] < 0.35:
        state = "UNRESOLVED"
        leader_mint = None
    elif margin < 0.08:
        state = "CONTESTED"
        leader_mint = None
    elif leader["score"] >= 0.72 and margin >= 0.15 and leader.get("explicit_contract"):
        state = "CLEAR_LEADER"
        leader_mint = leader["mint"]
    else:
        state = "PROVISIONAL_LEADER"
        leader_mint = leader["mint"]
    return {"state": state, "leader": leader_mint, "margin": margin, "ranked": ranked}
