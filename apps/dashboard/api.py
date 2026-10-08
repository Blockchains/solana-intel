from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.decisions.models import Decision
from apps.hottakes.models import HotTake
from apps.sources.models import Source


@api_view(["GET"])
@permission_classes([AllowAny])
def decisions(request):
    rows = []
    for d in Decision.objects.select_related("token").order_by("-as_of")[:20]:
        rows.append({
            "mint": d.token.mint,
            "symbol": d.token.symbol,
            "action": d.action,
            "status": d.operational_status,
            "as_of": d.as_of,
            "why_now": d.why_now,
            "synthetic": d.synthetic,
            "policy_version": d.policy_version,
        })
    return Response({"results": rows, "update_mechanism": "poll this endpoint; not a websocket"})


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({
        "sources": [
            {"key": s.key, "live_verification": s.live_verification, "notes": s.notes}
            for s in Source.objects.all()
        ],
        "hot_takes": HotTake.objects.filter(active=True).count(),
    })
