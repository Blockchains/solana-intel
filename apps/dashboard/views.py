from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.conf import settings

from apps.callers.models import Caller
from apps.decisions.models import Decision
from apps.hottakes.models import HotTake
from apps.markets.models import Candle, MarketSnapshot
from apps.narratives.models import Narrative, TokenCandidate
from apps.positions.accounting import account
from apps.positions.models import Position
from apps.research.models import ResearchResult
from apps.sources.models import Source
from apps.tokens.models import Token


def overview(request):
    decisions = Decision.objects.select_related("token").order_by("-as_of")[:8]
    cards = []
    seen = set()
    for d in decisions:
        if d.token_id in seen:
            continue
        seen.add(d.token_id)
        cards.append(d)
        if len(cards) == 5:
            break
    return render(request, "dashboard/overview.html", {"cards": cards})


def hot_takes(request):
    rows = HotTake.objects.select_related("token", "narrative").filter(active=True)
    return render(request, "dashboard/hot_takes.html", {"rows": rows})


def positions(request):
    rows = []
    for pos in Position.objects.select_related("token").prefetch_related("fills"):
        fills = [{
            "side": f.side, "price": f.price, "quantity": f.quantity,
            "fee_usd": f.fee_usd, "failed": f.failed,
        } for f in pos.fills.all()]
        snap = MarketSnapshot.objects.filter(token=pos.token).order_by("-as_of").first()
        mark = snap.price_usd if snap and pos.status == "open" else None
        rows.append({"position": pos, "pnl": account(fills, mark), "snap": snap})
    return render(request, "dashboard/positions.html", {"rows": rows})


def narratives(request):
    rows = Narrative.objects.all()
    return render(request, "dashboard/narratives.html", {"rows": rows})


def narrative_detail(request, narrative_id):
    narrative = get_object_or_404(Narrative, narrative_id=narrative_id)
    candidates = TokenCandidate.objects.filter(narrative=narrative).select_related("token").order_by("-as_of", "rank")
    return render(request, "dashboard/narrative_detail.html", {"narrative": narrative, "candidates": candidates})


def token_detail(request, mint):
    token = get_object_or_404(Token, mint=mint)
    decisions = token.decisions.all()[:12]
    candles = Candle.objects.filter(token=token, origin=Candle.DERIVED, empty=False)[:60]
    snaps = token.snapshots.order_by("as_of")
    return render(request, "dashboard/token_detail.html", {
        "token": token, "decisions": decisions, "candles": candles, "snaps": snaps,
    })


def callers(request):
    return render(request, "dashboard/callers.html", {"rows": Caller.objects.all()})


def replay(request):
    return render(request, "dashboard/replay.html", {
        "note": "Replay uses available_at <= clock. This build exercises that filter inside the synthetic command and unit tests. It is not a full historical corpus.",
    })


def research(request):
    return render(request, "dashboard/research.html", {"rows": ResearchResult.objects.all()})


def sources(request):
    return render(request, "dashboard/sources.html", {"rows": Source.objects.all()})


@login_required
def settings_page(request):
    risk = dict(settings.RISK)
    risk["portfolio_configured"] = bool(risk.get("portfolio_reference_value"))
    return render(request, "dashboard/settings.html", {"risk": risk, "mode": settings.OPERATING_MODE})
