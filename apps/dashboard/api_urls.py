from django.urls import path
from apps.dashboard import api

urlpatterns = [
    path("decisions/", api.decisions, name="api-decisions"),
    path("health/", api.health, name="api-health"),
]
