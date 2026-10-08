from django.urls import path
from apps.dashboard import views

urlpatterns = [
    path("", views.overview, name="overview"),
    path("hot-takes/", views.hot_takes, name="hot-takes"),
    path("positions/", views.positions, name="positions"),
    path("narratives/", views.narratives, name="narratives"),
    path("narratives/<slug:narrative_id>/", views.narrative_detail, name="narrative-detail"),
    path("tokens/<str:mint>/", views.token_detail, name="token-detail"),
    path("callers/", views.callers, name="callers"),
    path("replay/", views.replay, name="replay"),
    path("research/", views.research, name="research"),
    path("sources/", views.sources, name="sources"),
    path("settings/", views.settings_page, name="settings"),
]
