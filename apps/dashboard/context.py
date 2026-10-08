from django.conf import settings


def shell(request):
    return {
        "operating_mode": settings.OPERATING_MODE,
        "nav": [
            ("Overview", "/"),
            ("Hot Takes", "/hot-takes/"),
            ("Positions", "/positions/"),
            ("Narratives", "/narratives/"),
            ("Callers", "/callers/"),
            ("Replay", "/replay/"),
            ("Research", "/research/"),
            ("Sources", "/sources/"),
            ("Settings", "/settings/"),
        ],
    }
