from django.db import models
from apps.tokens.models import Token
from apps.narratives.models import Narrative


class HotTake(models.Model):
    token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name="hottakes")
    narrative = models.ForeignKey(Narrative, null=True, blank=True, on_delete=models.SET_NULL)
    entry_reason = models.CharField(max_length=200)
    priority = models.PositiveSmallIntegerField(default=50)
    active = models.BooleanField(default=True)
    last_evaluation = models.DateTimeField(null=True, blank=True)
    last_change = models.CharField(max_length=200, blank=True)
    next_check = models.DateTimeField(null=True, blank=True)
    expiry = models.DateTimeField(null=True, blank=True)
    triggers = models.JSONField(default=list)
